"use client";

import React, { useState, useEffect } from "react";
import { Address, AddressAPI } from "@/lib/api";
import { Plus, Check, MapPin, Phone, User } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import AddressForm, { AddressFormInput } from "@/components/AddressForm";

interface AddressSelectorProps {
  selectedAddressId: string | null;
  onSelect: (addressId: string) => void;
}

export default function AddressSelector({ selectedAddressId, onSelect }: AddressSelectorProps) {
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  // Load addresses on mount
  useEffect(() => {
    let active = true;
    async function loadAddresses() {
      try {
        const list = await AddressAPI.getAddresses();
        if (!active) return;
        setAddresses(list);
        
        // Auto-select default address if available and nothing is selected
        if (!selectedAddressId && list.length > 0) {
          const def = list.find((a) => a.is_default) || list[0];
          onSelect(def.id);
        }
      } catch (err) {
        console.error("Failed to load addresses", err);
      } finally {
        if (active) setLoading(false);
      }
    }
    loadAddresses();
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only fetch addresses once on mount

  const onSubmit = async (data: AddressFormInput) => {
    setIsSubmitting(true);
    try {
      const newAddr = await AddressAPI.addAddress(data);
      setAddresses((prev) => [...prev, newAddr]);
      onSelect(newAddr.id);
      setIsFormOpen(false);
    } catch (err) {
      console.error("Failed to save address", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="h-6 w-48 bg-white/5 rounded-md animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="h-32 bg-white/5 rounded-2xl animate-pulse" />
          <div className="h-32 bg-white/5 rounded-2xl animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <MapPin className="h-5 w-5 text-indigo-400" />
          <span>Delivery Address</span>
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Saved Addresses Grid */}
        {addresses.map((address) => {
          const isSelected = selectedAddressId === address.id;
          return (
            <div
              key={address.id}
              onClick={() => onSelect(address.id)}
              className={`relative cursor-pointer text-left p-5 rounded-2xl border transition-all duration-300 flex flex-col justify-between ${
                isSelected
                  ? "bg-indigo-500/10 border-indigo-500 shadow-lg shadow-indigo-500/5"
                  : "bg-white/5 border-white/5 hover:border-white/10 hover:bg-white/10"
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="font-extrabold text-sm text-white flex items-center gap-1.5">
                    <User className="h-4 w-4 text-indigo-400" />
                    {address.recipient_name}
                  </span>
                  <div className="flex items-center gap-2">
                    {address.is_default && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-slate-400">
                        Default
                      </span>
                    )}
                    {isSelected && (
                      <span className="h-5 w-5 rounded-full bg-indigo-500 flex items-center justify-center">
                        <Check className="h-3.5 w-3.5 text-white" />
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed pl-5">
                  {address.street}
                  <br />
                  {address.city}, {address.state} {address.postal_code}
                  <br />
                  {address.country}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-white/5 flex items-center gap-1.5 text-[11px] text-slate-400 font-medium pl-5">
                <Phone className="h-3.5 w-3.5 text-slate-500" />
                <span>{address.recipient_phone}</span>
              </div>
            </div>
          );
        })}

        {/* Add New Address Card */}
        <button
          onClick={() => {
            setIsFormOpen((prev) => !prev);
          }}
          className={`h-full min-h-[148px] border-2 border-dashed rounded-2xl bg-transparent flex flex-col items-center justify-center gap-2 group transition-all duration-300 ${
            isFormOpen
              ? "border-indigo-500 bg-indigo-500/5"
              : "border-white/10 hover:border-indigo-500/50 hover:bg-indigo-500/5"
          }`}
        >
          <div className={`h-10 w-10 rounded-full flex items-center justify-center transition-colors duration-300 ${
            isFormOpen
              ? "bg-indigo-500 text-white animate-spin-once"
              : "bg-white/5 text-slate-400 group-hover:bg-indigo-500 group-hover:text-white"
          }`}>
            <Plus className={`h-5 w-5 transition-transform duration-300 ${isFormOpen ? "rotate-45" : ""}`} />
          </div>
          <span className={`text-sm font-bold transition-colors duration-300 ${
            isFormOpen ? "text-indigo-400" : "text-slate-400 group-hover:text-white"
          }`}>
            {isFormOpen ? "Close Form" : "Add New Address"}
          </span>
        </button>
      </div>

      {/* Inline Address Form Collapsible Container */}
      <AnimatePresence>
        {isFormOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 mt-4">
              <div className="flex items-center justify-between pb-4 border-b border-white/5 mb-6">
                <h3 className="text-base font-extrabold text-white">Add Delivery Address</h3>
              </div>
              <AddressForm
                onSubmit={onSubmit}
                onCancel={() => setIsFormOpen(false)}
                isSubmitting={isSubmitting}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
