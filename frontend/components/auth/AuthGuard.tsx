"use client";

import React, { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "../../context/AuthContext";

export const AuthGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) {
      // Redirect to login page and preserve the path for post-auth redirect
      const redirectUrl = `/login?redirect=${encodeURIComponent(pathname)}`;
      router.push(redirectUrl);
    }
  }, [user, loading, pathname, router]);

  // Loading state with visual premium dark-neon placeholder
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0B0B0F] text-[#F4F4F7]">
        <div className="relative flex flex-col items-center gap-4">
          {/* Glowing Neon Pulse Ring */}
          <div className="h-12 w-12 rounded-full border-4 border-t-transparent border-[#18E7FF] animate-spin shadow-[0_0_15px_#18E7FF]" />
          <span className="text-sm font-semibold tracking-wider uppercase text-[#18E7FF] animate-pulse">
            Verifying Session...
          </span>
        </div>
      </div>
    );
  }

  // If user is logged in, render children
  if (user) {
    return <>{children}</>;
  }

  // Prevent flash of content during redirect
  return null;
};
