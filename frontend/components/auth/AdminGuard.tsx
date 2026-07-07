"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAdminAuth } from "../../context/AdminAuthContext";
import { useAuth } from "../../context/AuthContext";

export const AdminGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { admin, loading } = useAdminAuth();
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (user) {
        // Enforce role isolation: Logged in as customer, redirect to customer home
        router.push("/");
      } else if (!admin) {
        // Redirect to admin login page
        router.push("/admin/login");
      }
    }
  }, [admin, user, loading, router]);

  // Loading state with visual premium dark-neon placeholder (pink accent for admin)
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0B0B0F] text-[#F4F4F7]">
        <div className="relative flex flex-col items-center gap-4">
          {/* Glowing Neon Pulse Ring - Pink accent for CMS */}
          <div className="h-12 w-12 rounded-full border-4 border-t-transparent border-[#FF2E8A] animate-spin shadow-[0_0_15px_#FF2E8A]" />
          <span className="text-sm font-semibold tracking-wider uppercase text-[#FF2E8A] animate-pulse">
            Verifying Admin Session...
          </span>
        </div>
      </div>
    );
  }

  // Render children only if admin is authenticated and customer is not active
  if (admin && !user) {
    return <>{children}</>;
  }

  // Prevent flash of content during redirect
  return null;
};
