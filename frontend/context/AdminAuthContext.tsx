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
const adminApi = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000/api",
  withCredentials: true, // Necessary to send and receive HTTPOnly cookies
});

export const AdminAuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [admin, setAdmin] = useState<Admin | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Setup request interceptor to attach bearer token
  useEffect(() => {
    const requestInterceptor = adminApi.interceptors.request.use(
      (config) => {
        if (accessToken) {
          config.headers["Authorization"] = `Bearer ${accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => {
      adminApi.interceptors.request.eject(requestInterceptor);
    };
  }, [accessToken]);

  // Setup response interceptor for 401 token refresh logic
  useEffect(() => {
    const responseInterceptor = adminApi.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            // Silently request a token refresh for admin
            const res = await axios.post(
              `${adminApi.defaults.baseURL}/admin/auth/refresh`,
              {},
              { withCredentials: true }
            );
            
            if (res.status === 200 && res.data?.success) {
              const newAccessToken = res.data.data.access_token;
              setAccessToken(newAccessToken);
              
              // Retry original request with new token
              originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
              return adminApi(originalRequest);
            }
          } catch (refreshError) {
            // Invalidate admin session if refresh failed
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
      adminApi.interceptors.response.eject(responseInterceptor);
    };
  }, []);

  // Hydrate admin session silently on application mount
  useEffect(() => {
    const hydrateAdminSession = async () => {
      try {
        const res = await adminApi.post("/admin/auth/refresh");
        if (res.data?.success) {
          const newAccessToken = res.data.data.access_token;
          setAccessToken(newAccessToken);
          
          // Load admin details
          const meRes = await adminApi.get("/admin/auth/me", {
            headers: { Authorization: `Bearer ${newAccessToken}` }
          });
          if (meRes.data?.success) {
            setAdmin(meRes.data.data.admin);
          }
        }
      } catch (err) {
        // No active session, ignore
      } finally {
        setLoading(false);
      }
    };

    hydrateAdminSession();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const res = await adminApi.post("/admin/auth/login", { email, password });
      if (res.data?.success) {
        setAccessToken(res.data.data.access_token);
        setAdmin(res.data.data.admin);
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

  const logout = async () => {
    try {
      await adminApi.post("/admin/auth/logout");
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
    <AdminAuthContext.Provider value={{ admin, accessToken, loading, login, logout, api: adminApi }}>
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
