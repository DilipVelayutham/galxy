"use client";

import Link from "next/link";
import { useAuth } from "../../../context/AuthContext";
import { ArrowLeft, User } from "lucide-react";

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-[#0B0B0F] px-6 py-12 flex flex-col items-center justify-center">
      <div className="w-full max-w-md p-8 rounded-2xl border border-white/10 bg-[#16161C]/75 backdrop-blur-xl shadow-xl">
        <Link 
          href="/" 
          className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#8A8A97] hover:text-[#18E7FF] mb-6 transition-colors"
        >
          <ArrowLeft size={14} /> Back to Portal
        </Link>
        
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 rounded-xl bg-[#18E7FF]/10 text-[#18E7FF]">
            <User size={24} />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-[#F4F4F7]">YOUR PROFILE</h2>
            <p className="text-xs text-[#8A8A97] uppercase tracking-wider">Customer Details</p>
          </div>
        </div>

        {user ? (
          <div className="space-y-4 text-sm">
            <div>
              <span className="block text-xxs uppercase tracking-widest text-[#8A8A97]">Display Name</span>
              <p className="font-semibold text-lg text-[#F4F4F7]">{user.name}</p>
            </div>
            <div>
              <span className="block text-xxs uppercase tracking-widest text-[#8A8A97]">Email Address</span>
              <p className="font-semibold text-[#F4F4F7]">{user.email}</p>
            </div>
            <div>
              <span className="block text-xxs uppercase tracking-widest text-[#8A8A97]">Phone Number</span>
              <p className="font-semibold text-[#F4F4F7]">{user.phone || "Not set"}</p>
            </div>
            <div className="pt-4 border-t border-white/5">
              <Link 
                href="/account/addresses"
                className="text-xs font-bold uppercase tracking-wider text-[#FF2E8A] hover:underline"
              >
                Manage Saved Addresses &rarr;
              </Link>
            </div>
          </div>
        ) : (
          <p className="text-sm text-[#8A8A97]">No user details available.</p>
        )}
      </div>
    </div>
  );
}
