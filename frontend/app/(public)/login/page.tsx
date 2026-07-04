"use client";

import { AuthForm } from "../../../components/auth/AuthForm";
import Link from "next/link";
import { Suspense } from "react";

function LoginContent() {
  return <AuthForm initialMode="login" />;
}

export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 bg-[#0B0B0F]">
      {/* Home Link */}
      <Link 
        href="/" 
        className="mb-8 text-2xl font-bold tracking-widest text-[#F4F4F7] hover:text-[#18E7FF] transition-colors"
      >
        GAL<span className="text-[#FF2E8A]">XY</span>
      </Link>
      
      {/* Suspense boundary is required in Next.js when components use useSearchParams() */}
      <Suspense fallback={
        <div className="h-96 w-full max-w-md rounded-2xl bg-[#16161C]/50 border border-white/5 animate-pulse" />
      }>
        <LoginContent />
      </Suspense>
    </div>
  );
}
