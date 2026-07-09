"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { api, setAccessToken } from "@/lib/api";

export interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: "customer" | "super_admin";
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; message?: string }>;
  logout: () => Promise<void>;
  signup: (name: string, email: string, phone: string, password: string) => Promise<{ success: boolean; message?: string }>;
  refreshSession: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Silently hydrate session from HttpOnly cookie
  const refreshSession = async (): Promise<boolean> => {
    try {
      const res = await api.post("/auth/refresh");
      if (res.success && res.data?.access_token) {
        setAccessToken(res.data.access_token);
        setUser(res.data.user);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      await refreshSession();
      setLoading(false);
    };
    initAuth();

    // Listen for global API forced logout events
    const handleForcedLogout = () => {
      setUser(null);
    };
    window.addEventListener("auth-logout", handleForcedLogout);
    return () => {
      window.removeEventListener("auth-logout", handleForcedLogout);
    };
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const res = await api.post("/auth/login", { email, password });
      if (res.success && res.data) {
        setAccessToken(res.data.access_token);
        setUser(res.data.user);
        setLoading(false);
        return { success: true };
      }
      setLoading(false);
      return { success: false, message: res.message };
    } catch (err) {
      setLoading(false);
      const message = err instanceof Error ? err.message : "Login connection failed";
      return { success: false, message };
    }
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch (e) {
      console.error(e);
    } finally {
      setAccessToken("");
      setUser(null);
    }
  };

  const signup = async (name: string, email: string, phone: string, password: string) => {
    try {
      const res = await api.post("/auth/signup", { name, email, phone, password });
      if (res.success) {
        return { success: true };
      }
      return { success: false, message: res.message };
    } catch (err) {
      const message = err instanceof Error ? err.message : "Registration failed";
      return { success: false, message };
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        logout,
        signup,
        refreshSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
