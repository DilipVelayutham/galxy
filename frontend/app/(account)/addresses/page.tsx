'use client';

import React, { useState, useEffect } from 'react';
import { Plus, MapPin, Loader, AlertTriangle, CheckCircle } from 'lucide-react';
import { AddressCard, Address } from '../../components/account/AddressCard';
import { AddressForm } from '../../components/account/AddressForm';

export default function AddressesPage() {
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingAddress, setEditingAddress] = useState<Address | undefined>(undefined);
  const [isSaving, setIsSaving] = useState(false);
  const [isSettingDefault, setIsSettingDefault] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    fetchAddresses();
  }, []);

  const fetchAddresses = async () => {
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
        setAddresses(data.data.addresses || []);
      } else {
        setStatus({ type: 'error', message: data.message || 'Failed to load addresses.' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Failed to load addresses. Connection error.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenAddForm = () => {
    setEditingAddress(undefined);
    setIsFormOpen(true);
  };

  const handleOpenEditForm = (address: Address) => {
    setEditingAddress(address);
    setIsFormOpen(true);
  };

  const handleSaveAddress = async (formData: Omit<Address, '_id'> & { _id?: string }) => {
    setIsSaving(true);
    setStatus(null);
    try {
      const token = localStorage.getItem('access_token');
      const isEdit = !!formData._id;
      const url = isEdit ? `/api/user/addresses/${formData._id}` : '/api/user/addresses';
      const method = isEdit ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token || ''}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      const data = await res.json();

      if (data.success) {
        if (isEdit) {
          // Update in local state
          setAddresses(prev =>
            prev.map(addr => (addr._id === formData._id ? data.data : data.data.is_default ? { ...addr, is_default: false } : addr))
          );
          // If the edited address was set to default, we must unset it on all others
          if (data.data.is_default) {
            setAddresses(prev => prev.map(addr => (addr._id === data.data._id ? data.data : { ...addr, is_default: false })));
          }
          setStatus({ type: 'success', message: 'Address updated successfully.' });
        } else {
          // Add to local state
          if (data.data.is_default) {
            // Unset other defaults
            setAddresses(prev => [...prev.map(addr => ({ ...addr, is_default: false })), data.data]);
          } else {
            setAddresses(prev => [...prev, data.data]);
          }
          setStatus({ type: 'success', message: 'Address added successfully.' });
        }
        setIsFormOpen(false);
      } else {
        throw data;
      }
    } catch (err: any) {
      throw err; // Form component will catch and show inline errors
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteAddress = async (addressId: string) => {
    if (!confirm('Are you sure you want to delete this address?')) return;

    setStatus(null);
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/user/addresses/${addressId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token || ''}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await res.json();

      if (data.success) {
        setAddresses(prev => prev.filter(addr => addr._id !== addressId));
        // If we deleted the default address, reload profile to fetch the new promoted default
        const deletedAddr = addresses.find(a => a._id === addressId);
        if (deletedAddr?.is_default) {
          fetchAddresses();
        }
        setStatus({ type: 'success', message: 'Address deleted successfully.' });
      } else {
        setStatus({ type: 'error', message: data.errors?.message || data.message || 'Failed to delete address.' });
      }
    } catch (err) {
      setStatus({ type: 'error', message: 'Connection error while deleting address.' });
    }
  };

  const handleSetDefaultAddress = async (addressId: string) => {
    setIsSettingDefault(true);
    setStatus(null);

    // Save previous state for rollback
    const previousAddresses = [...addresses];

    // Optimistic UI update: immediately set requested address as default and others to false
    setAddresses(prev =>
      prev.map(addr => ({
        ...addr,
        is_default: addr._id === addressId
      }))
    );

    try {
      const token = localStorage.getItem('access_token');
      // Trigger API update
      const res = await fetch(`/api/user/addresses/${addressId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token || ''}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_default: true })
      });
      const data = await res.json();

      if (!data.success) {
        // Rollback on server failure
        setAddresses(previousAddresses);
        setStatus({ type: 'error', message: data.message || 'Failed to set default address.' });
      } else {
        // Ensure state is perfectly matching server returned state
        setAddresses(prev =>
          prev.map(addr => (addr._id === addressId ? data.data : { ...addr, is_default: false }))
        );
        setStatus({ type: 'success', message: 'Default address updated.' });
      }
    } catch (err) {
      // Rollback on network failure
      setAddresses(previousAddresses);
      setStatus({ type: 'error', message: 'Network error. Failed to update default address.' });
    } finally {
      setIsSettingDefault(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
        <div className="relative w-16 h-16 rounded-full border-2 border-[#18E7FF]/20 flex items-center justify-center">
          <Loader className="w-8 h-8 text-[#18E7FF] animate-spin" />
          <div className="absolute inset-0 rounded-full border-t-2 border-[#9B5CFF] animate-pulse" />
        </div>
        <p className="text-sm font-semibold text-[#8A8A97] tracking-wider uppercase animate-pulse">
          Loading Saved Addresses...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0B0F] text-[#F4F4F7] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
        
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">
              Saved <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#18E7FF] via-[#9B5CFF] to-[#FF2E8A] drop-shadow-[0_0_10px_rgba(24,231,255,0.15)]">Addresses</span>
            </h1>
            <p className="mt-2 text-sm text-[#8A8A97]">
              Manage your delivery addresses for seamless order checkout.
            </p>
          </div>
          <button
            onClick={handleOpenAddForm}
            className="flex items-center justify-center gap-2 py-3 px-6 rounded-xl bg-gradient-to-r from-[#18E7FF] to-[#9B5CFF] text-[#0B0B0F] font-bold text-sm hover:shadow-[0_0_25px_rgba(24,231,255,0.35)] hover:brightness-110 active:scale-[0.98] transition-all duration-300"
          >
            <Plus className="w-4 h-4 text-[#0B0B0F]" /> Add Address
          </button>
        </div>

        {/* Global status message */}
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

        {/* Addresses Grid */}
        {addresses.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-3xl bg-[#16161C]/30 border border-neutral-800/80 p-12 text-center space-y-4">
            <div className="p-4 rounded-full bg-neutral-900 border border-neutral-800">
              <MapPin className="w-10 h-10 text-[#8A8A97]" />
            </div>
            <div className="space-y-1">
              <h3 className="text-[#F4F4F7] font-semibold text-lg">No saved addresses</h3>
              <p className="text-sm text-[#8A8A97] max-w-sm">
                You haven't saved any addresses yet. Add one to speed up checkout on your future custom orders.
              </p>
            </div>
            <button
              onClick={handleOpenAddForm}
              className="py-2.5 px-6 text-sm font-semibold rounded-xl bg-neutral-900 border border-neutral-800 text-[#F4F4F7] hover:border-[#18E7FF]/40 hover:bg-neutral-800/60 transition-all duration-300"
            >
              Add Your First Address
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {addresses.map((address) => (
              <AddressCard
                key={address._id}
                address={address}
                onEdit={handleOpenEditForm}
                onDelete={handleDeleteAddress}
                onSetDefault={handleSetDefaultAddress}
                isSettingDefault={isSettingDefault}
              />
            ))}
          </div>
        )}

        {/* Add/Edit Modal */}
        {isFormOpen && (
          <AddressForm
            address={editingAddress}
            onSave={handleSaveAddress}
            onClose={() => setIsFormOpen(false)}
            isSaving={isSaving}
          />
        )}

      </div>
    </div>
  );
}
