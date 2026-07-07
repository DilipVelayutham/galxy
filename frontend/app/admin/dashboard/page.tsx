"use client";

import React from "react";
import { AdminGuard } from "../../../components/auth/AdminGuard";
import { useAdminAuth } from "../../../context/AdminAuthContext";
import Link from "next/link";
import { LogOut, Shield, Users, LayoutDashboard, Settings } from "lucide-react";

function DashboardContent() {
  const { admin, logout } = useAdminAuth();

  return (
    <div className="flex min-h-screen bg-[#0B0B0F] text-[#F4F4F7]">
      {/* Sidebar */}
      <aside className="w-64 bg-[#16161C] border-r border-white/5 flex flex-col">
        {/* Sidebar Header */}
        <div className="h-16 flex items-center px-6 border-b border-white/5">
          <Shield className="w-5 h-5 text-[#FF2E8A] mr-2" />
          <span className="font-bold text-lg tracking-wider">GALXY CMS</span>
        </div>
        
        {/* Nav Links */}
        <nav className="flex-1 px-4 py-6 space-y-1">
          <Link href="/admin/dashboard" className="flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold bg-[#FF2E8A]/10 text-[#FF2E8A] transition-colors">
            <LayoutDashboard className="w-4 h-4 mr-3" />
            Dashboard
          </Link>
          <div className="flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold text-[#8A8A97] hover:text-[#F4F4F7] hover:bg-white/5 cursor-not-allowed">
            <Users className="w-4 h-4 mr-3" />
            Users (Module 1)
          </div>
          <div className="flex items-center px-4 py-2.5 rounded-lg text-sm font-semibold text-[#8A8A97] hover:text-[#F4F4F7] hover:bg-white/5 cursor-not-allowed">
            <Settings className="w-4 h-4 mr-3" />
            Settings
          </div>
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-white/5">
          <button 
            onClick={logout}
            className="w-full flex items-center justify-center px-4 py-2.5 rounded-lg bg-neutral-900 border border-white/5 hover:border-red-500/30 hover:bg-red-500/10 text-[#8A8A97] hover:text-red-400 font-semibold text-sm transition-all"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Log Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Topbar */}
        <header className="h-16 border-b border-white/5 bg-[#16161C]/50 backdrop-blur-md px-8 flex items-center justify-between">
          <h1 className="font-bold text-lg">Dashboard</h1>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-semibold">{admin?.name}</p>
              <p className="text-xxs text-[#8A8A97] uppercase tracking-wider">{admin?.role}</p>
            </div>
            <div className="w-8 h-8 rounded-full bg-[#FF2E8A]/20 border border-[#FF2E8A]/50 flex items-center justify-center font-bold text-[#FF2E8A]">
              {admin?.name?.substring(0, 1).toUpperCase()}
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 p-8 space-y-6">
          <div className="p-6 rounded-xl border border-white/5 bg-[#16161C] space-y-2">
            <h2 className="text-xl font-bold text-[#F4F4F7]">Welcome back, {admin?.name}!</h2>
            <p className="text-sm text-[#8A8A97]">This is the secure administration dashboard. All core backend auth, service, and decorator endpoints are fully integrated.</p>
          </div>

          {/* Dummy Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl border border-white/5 bg-[#16161C] space-y-1">
              <p className="text-xxs font-bold text-[#8A8A97] uppercase tracking-wider">Active Customers</p>
              <p className="text-2xl font-bold text-[#18E7FF]">1,280</p>
            </div>
            <div className="p-6 rounded-xl border border-white/5 bg-[#16161C] space-y-1">
              <p className="text-xxs font-bold text-[#8A8A97] uppercase tracking-wider">Default Invariants</p>
              <p className="text-2xl font-bold text-[#FFD84D]">Active</p>
            </div>
            <div className="p-6 rounded-xl border border-white/5 bg-[#16161C] space-y-1">
              <p className="text-xxs font-bold text-[#8A8A97] uppercase tracking-wider">Identity Isolation</p>
              <p className="text-2xl font-bold text-[#FF2E8A]">Enforced</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function AdminDashboardPage() {
  return (
    <AdminGuard>
      <DashboardContent />
    </AdminGuard>
  );
}
