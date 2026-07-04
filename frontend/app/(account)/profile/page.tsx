'use client';

import React, { useState, useEffect } from 'react';
import { User, Phone, Mail, Save, AlertTriangle, CheckCircle, Loader } from 'lucide-react';

interface UserProfile {
  name: string;
  email: string;
  phone: string;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [formData, setFormData] = useState({ name: '', phone: '' });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch('/api/user/profile', {
        headers: {
          'Authorization': `Bearer ${token || ''}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await res.json();
      if (data.success) {
        setProfile(data.data);
        setFormData({ name: data.data.name, phone: data.data.phone });
      } else {
        setStatus({ type: 'error', message: data.message || 'Failed to load profile.' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Failed to load profile. Connection error.' });
    } finally {
      setIsLoading(false);
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required.';
    }

    const phoneStr = formData.phone.trim();
    if (!phoneStr) {
      newErrors.phone = 'Phone number is required.';
    } else if (!/^[6-9]\d{9}$/.test(phoneStr)) {
      newErrors.phone = 'Please enter a valid 10-digit Indian mobile number.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    if (!validate()) return;

    setIsSaving(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch('/api/user/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token || ''}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (data.success) {
        setProfile(data.data);
        setStatus({ type: 'success', message: 'Profile updated successfully.' });
      } else {
        setStatus({ type: 'error', message: data.message || 'Failed to update profile.' });
        if (data.errors) {
          setErrors(data.errors);
        }
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
        {/* Pulsing neon scan line placeholder */}
        <div className="relative w-16 h-16 rounded-full border-2 border-[#18E7FF]/20 flex items-center justify-center">
          <Loader className="w-8 h-8 text-[#18E7FF] animate-spin" />
          <div className="absolute inset-0 rounded-full border-t-2 border-[#FF2E8A] animate-pulse" />
        </div>
        <p className="text-sm font-semibold text-[#8A8A97] tracking-wider uppercase animate-pulse">
          Retrieving Profile...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0B0F] text-[#F4F4F7] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto space-y-8">
        
        {/* Title */}
        <div className="text-center sm:text-left">
          <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">
            Account <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF2E8A] to-[#9B5CFF] drop-shadow-[0_0_10px_rgba(255,46,138,0.2)]">Profile</span>
          </h1>
          <p className="mt-2 text-sm text-[#8A8A97]">
            Manage your customer account details and contact information.
          </p>
        </div>

        {/* Form Container */}
        <div className="relative overflow-hidden rounded-3xl bg-[#16161C]/60 border border-neutral-800/80 backdrop-blur-md p-8 shadow-[0_20px_40px_rgba(0,0,0,0.4)]">
          <div className="absolute top-0 right-0 w-64 h-64 bg-[#FF2E8A]/5 blur-[80px] pointer-events-none rounded-full" />
          
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Status alerts */}
            {status && (
              <div
                className={`flex items-start gap-3 p-4 rounded-2xl border text-sm font-medium transition-all ${
                  status.type === 'success'
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                    : 'bg-[#FFD84D]/10 border-[#FFD84D]/30 text-[#FFD84D]'
                }`}
              >
                {status.type === 'success' ? (
                  <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                )}
                <span>{status.message}</span>
              </div>
            )}

            {/* Email (Read only) */}
            <div className="relative">
              <label className="block text-xs font-semibold text-[#8A8A97] uppercase tracking-wider mb-2">Email Address</label>
              <div className="flex items-center gap-3 w-full py-3 px-4 rounded-xl bg-neutral-900/30 border border-neutral-800/50 text-[#8A8A97] select-none">
                <Mail className="w-5 h-5 text-neutral-600" />
                <span className="text-sm font-mono">{profile?.email}</span>
                <span className="ml-auto text-[10px] text-neutral-600 border border-neutral-800/80 px-2 py-0.5 rounded-full uppercase tracking-wider font-semibold">
                  Locked
                </span>
              </div>
              <p className="mt-1.5 text-[11px] text-[#8A8A97]/60">
                To update your registered email address, please contact customer support.
              </p>
            </div>

            {/* Name Input */}
            <div>
              <label className="block text-xs font-semibold text-[#8A8A97] uppercase tracking-wider mb-2">Display Name</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-4 text-neutral-600">
                  <User className="w-5 h-5" />
                </span>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Adarsh Sen"
                  className={`w-full py-3 pl-12 pr-4 rounded-xl bg-neutral-900/50 border text-sm text-[#F4F4F7] placeholder-neutral-700 focus:outline-none transition-all duration-300 ${
                    errors.name
                      ? 'border-[#FFD84D] focus:border-[#FFD84D]'
                      : 'border-neutral-800 focus:border-[#FF2E8A] focus:shadow-[0_0_15px_rgba(255,46,138,0.15)]'
                  }`}
                />
              </div>
              {errors.name && <p className="mt-1.5 text-xs text-[#FFD84D]">{errors.name}</p>}
            </div>

            {/* Phone Input */}
            <div>
              <label className="block text-xs font-semibold text-[#8A8A97] uppercase tracking-wider mb-2">Mobile Number</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-4 text-neutral-600">
                  <Phone className="w-5 h-5" />
                </span>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="10-digit number"
                  maxLength={10}
                  className={`w-full py-3 pl-12 pr-4 rounded-xl bg-neutral-900/50 border text-sm text-[#F4F4F7] placeholder-neutral-700 focus:outline-none transition-all duration-300 ${
                    errors.phone
                      ? 'border-[#FFD84D] focus:border-[#FFD84D]'
                      : 'border-neutral-800 focus:border-[#FF2E8A] focus:shadow-[0_0_15px_rgba(255,46,138,0.15)]'
                  }`}
                />
              </div>
              {errors.phone && <p className="mt-1.5 text-xs text-[#FFD84D]">{errors.phone}</p>}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end pt-4 border-t border-neutral-800/40">
              <button
                type="submit"
                disabled={isSaving}
                className="flex items-center justify-center gap-2 py-3 px-8 rounded-xl bg-gradient-to-r from-[#FF2E8A] to-[#9B5CFF] text-[#F4F4F7] font-semibold text-sm hover:shadow-[0_0_25px_rgba(255,46,138,0.35)] hover:brightness-110 active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="w-4 h-4" />
                {isSaving ? 'Updating Profile...' : 'Save Profile Details'}
              </button>
            </div>
            
          </form>
        </div>

      </div>
    </div>
  );
}
