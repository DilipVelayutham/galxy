"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAdminAuth } from "../../context/AdminAuthContext";

export const AdminGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { admin, loading } = useAdminAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !admin) {
      // Redirect to admin login page (no query param since admin always redirects back to dashboard/panel)
      router.push("/admin/login");
    }
  }, [admin, loading, router]);

  // Loading state with visual premium dark-neon placeholder for admin panel
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0B0B0F] text-[#F4F4F7]">
        <div className="relative flex flex-col items-center gap-4">
          {/* Glowing Neon Pulse Ring - admin theme (magenta/glow) */}
          <div className="h-12 w-12 rounded-full border-4 border-t-transparent border-[#FF2E8A] animate-spin shadow-[0_0_15px_#FF2E8A]" />
          <span className="text-sm font-semibold tracking-wider uppercase text-[#FF2E8A] animate-pulse">
            Verifying Admin Session...
          </span>
        </div>
      </div>
    );
  }

  // If admin is logged in, render children
  if (admin) {
    return <>{children}</>;
  }

  // Prevent flash of content during redirect
  return null;
};
