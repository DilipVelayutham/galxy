"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import axios, { AxiosInstance } from "axios";

interface User {
  _id: string;
  name: string;
  email: string;
  phone: string;
  is_verified: boolean;
  auth_provider: string;
  addresses?: unknown[];
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, phone: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  api: AxiosInstance;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// API Client instance configured for cookies and base URL
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000/api",
  withCredentials: true, // Necessary to send and receive HTTPOnly cookies
});

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Setup request interceptor to attach bearer token
  useEffect(() => {
    const requestInterceptor = api.interceptors.request.use(
      (config) => {
        if (accessToken) {
          config.headers["Authorization"] = `Bearer ${accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => {
      api.interceptors.request.eject(requestInterceptor);
    };
  }, [accessToken]);

  // Setup response interceptor for 401 token refresh logic
  useEffect(() => {
    const responseInterceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            // Silently request a token refresh
            const res = await axios.post(
              `${api.defaults.baseURL}/auth/refresh`,
              {},
              { withCredentials: true }
            );
            
            if (res.status === 200 && res.data?.success) {
              const newAccessToken = res.data.data.access_token;
              setAccessToken(newAccessToken);
              
              // Retry original request with new token
              originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
              return api(originalRequest);
            }
          } catch {
            // Invalidate session if refresh failed
            setAccessToken(null);
            setUser(null);
            // On refresh failure, redirect to login if we are in account route
            if (typeof window !== "undefined" && window.location.pathname.startsWith("/account")) {
              window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
            }
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.response.eject(responseInterceptor);
    };
  }, []);

  // Hydrate session silently on application mount
  useEffect(() => {
    const hydrateSession = async () => {
      try {
        const res = await api.post("/auth/refresh");
        if (res.data?.success) {
          setAccessToken(res.data.data.access_token);
          
          // Load public profile
          const profileRes = await api.get("/user/profile", {
            headers: { Authorization: `Bearer ${res.data.data.access_token}` }
          });
          if (profileRes.data?.success) {
            setUser(profileRes.data.data);
          }
        }
      } catch {
        // No active session, ignore
      } finally {
        setLoading(false);
      }
    };

    hydrateSession();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const res = await api.post("/auth/login", { email, password });
      if (res.data?.success) {
        setAccessToken(res.data.data.access_token);
        setUser(res.data.data.user);
      } else {
        throw new Error(res.data?.message || "Login failed");
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || error.message || "Login failed");
      }
      throw new Error(error instanceof Error ? error.message : "Login failed");
    }
  };

  const signup = async (name: string, email: string, phone: string, password: string) => {
    try {
      const res = await api.post("/auth/signup", { name, email, phone, password });
      if (res.data?.success) {
        setAccessToken(res.data.data.access_token);
        setUser(res.data.data.user);
      } else {
        throw new Error(res.data?.message || "Signup failed");
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || error.message || "Signup failed");
      }
      throw new Error(error instanceof Error ? error.message : "Signup failed");
    }
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      // Proceed with clearing local state regardless of server logout response
    } finally {
      setAccessToken(null);
      setUser(null);
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
  };

  return (
    <AuthContext.Provider value={{ user, accessToken, loading, login, signup, logout, api }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
