"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import axios, { AxiosInstance } from "axios";

interface Admin {
  _id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
}

interface AdminAuthContextType {
  admin: Admin | null;
  accessToken: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  api: AxiosInstance;
}

const AdminAuthContext = createContext<AdminAuthContextType | undefined>(undefined);

// API Client instance configured for cookies and base URL specifically for admin
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000/api",
  withCredentials: true, // Necessary to send and receive HTTPOnly cookies
});

export const AdminAuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [admin, setAdmin] = useState<Admin | null>(null);
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
            // Silently request a token refresh via admin endpoint
            const res = await axios.post(
              `${api.defaults.baseURL}/admin/auth/refresh`,
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
          } catch (refreshError) {
            // Invalidate session if refresh failed
            setAccessToken(null);
            setAdmin(null);
            // On refresh failure, redirect to admin login if we are in admin route (excluding login page itself)
            if (typeof window !== "undefined") {
              const pathname = window.location.pathname;
              if (pathname.startsWith("/admin") && pathname !== "/admin/login") {
                window.location.href = `/admin/login`;
              }
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
        const res = await api.post("/admin/auth/refresh");
        if (res.data?.success) {
          const newAccessToken = res.data.data.access_token;
          setAccessToken(newAccessToken);
          
          // Load public profile for admin
          const profileRes = await api.get("/admin/auth/me", {
            headers: { Authorization: `Bearer ${newAccessToken}` }
          });
          if (profileRes.data?.success) {
            setAdmin(profileRes.data.data.admin);
          }
        }
      } catch (err) {
        // No active session, ignore
      } finally {
        setLoading(false);
      }
    };

    hydrateSession();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const res = await api.post("/admin/auth/login", { email, password });
      if (res.data?.success) {
        setAccessToken(res.data.data.access_token);
        setAdmin(res.data.data.admin);
      } else {
        throw new Error(res.data?.message || "Login failed");
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || error.message || "Login failed");
    }
  };

  const logout = async () => {
    try {
      await api.post("/admin/auth/logout");
    } catch (err) {
      // Proceed with clearing local state regardless of server logout response
    } finally {
      setAccessToken(null);
      setAdmin(null);
      if (typeof window !== "undefined") {
        window.location.href = "/admin/login";
      }
    }
  };

  return (
    <AdminAuthContext.Provider value={{ admin, accessToken, loading, login, logout, api }}>
      {children}
    </AdminAuthContext.Provider>
  );
};

export const useAdminAuth = () => {
  const context = useContext(AdminAuthContext);
  if (context === undefined) {
    throw new Error("useAdminAuth must be used within an AdminAuthProvider");
  }
  return context;
};
