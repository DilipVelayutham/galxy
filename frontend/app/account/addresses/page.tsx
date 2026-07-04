"use client";

import Link from "next/link";
import { ArrowLeft, MapPin } from "lucide-react";

export default function AddressesPage() {
  return (
    <div className="min-h-screen bg-[#0B0B0F] px-6 py-12 flex flex-col items-center justify-center">
      <div className="w-full max-w-md p-8 rounded-2xl border border-white/10 bg-[#16161C]/75 backdrop-blur-xl shadow-xl">
        <Link 
          href="/account/profile" 
          className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#8A8A97] hover:text-[#18E7FF] mb-6 transition-colors"
        >
          <ArrowLeft size={14} /> Back to Profile
        </Link>
        
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 rounded-xl bg-[#FF2E8A]/10 text-[#FF2E8A]">
            <MapPin size={24} />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-[#F4F4F7]">SAVED ADDRESSES</h2>
            <p className="text-xs text-[#8A8A97] uppercase tracking-wider">Manage Delivery Points</p>
          </div>
        </div>

        <p className="text-sm text-[#8A8A97]">
          No addresses saved yet. In2 (Naresh) will build the address list cards and the addition form components here.
        </p>
      </div>
    </div>
  );
}
