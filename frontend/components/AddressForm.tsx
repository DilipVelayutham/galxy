"use client";

import React from "react";
import { useForm } from "react-hook-form";

export interface AddressFormInput {
  recipient_name: string;
  recipient_phone: string;
  street: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}

interface AddressFormProps {
  onSubmit: (data: AddressFormInput) => Promise<void> | void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export default function AddressForm({ onSubmit, onCancel, isSubmitting = false }: AddressFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AddressFormInput>({
    defaultValues: {
      recipient_name: "",
      recipient_phone: "",
      street: "",
      city: "",
      state: "",
      postal_code: "",
      country: "United States",
      is_default: false,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 text-left">
      {/* Recipient Details */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-400">Recipient Name</label>
          <input
            type="text"
            className="w-full rounded-xl px-4 py-3 text-sm glass-input"
            placeholder="e.g. Alex Mercer"
            {...register("recipient_name", { required: "Name is required" })}
          />
          {errors.recipient_name && (
            <span className="text-[10px] font-medium text-red-400">{errors.recipient_name.message}</span>
          )}
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-400">Recipient Phone</label>
          <input
            type="text"
            className="w-full rounded-xl px-4 py-3 text-sm glass-input"
            placeholder="e.g. +1 (555) 019-2834"
            {...register("recipient_phone", { 
              required: "Phone number is required",
              pattern: {
                value: /^(\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}$/,
                message: "Enter a valid phone number"
              }
            })}
          />
          {errors.recipient_phone && (
            <span className="text-[10px] font-medium text-red-400">{errors.recipient_phone.message}</span>
          )}
        </div>
      </div>

      {/* Street Address */}
      <div className="space-y-1">
        <label className="text-xs font-bold text-slate-400">Street Address</label>
        <input
          type="text"
          className="w-full rounded-xl px-4 py-3 text-sm glass-input"
          placeholder="e.g. 742 Evergreen Terrace"
          {...register("street", { required: "Street address is required" })}
        />
        {errors.street && (
          <span className="text-[10px] font-medium text-red-400">{errors.street.message}</span>
        )}
      </div>

      {/* City & State */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-400">City</label>
          <input
            type="text"
            className="w-full rounded-xl px-4 py-3 text-sm glass-input"
            placeholder="e.g. Springfield"
            {...register("city", { required: "City is required" })}
          />
          {errors.city && (
            <span className="text-[10px] font-medium text-red-400">{errors.city.message}</span>
          )}
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-400">State / Region</label>
          <input
            type="text"
            className="w-full rounded-xl px-4 py-3 text-sm glass-input"
            placeholder="e.g. IL"
            {...register("state", { required: "State is required" })}
          />
          {errors.state && (
            <span className="text-[10px] font-medium text-red-400">{errors.state.message}</span>
          )}
        </div>
      </div>

      {/* Postal Code & Country */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-400">Postal / Zip Code</label>
          <input
            type="text"
            className="w-full rounded-xl px-4 py-3 text-sm glass-input"
            placeholder="e.g. 62704"
            {...register("postal_code", { 
              required: "Zip code is required",
              pattern: {
                value: /^[a-zA-Z0-9 -]{3,10}$/,
                message: "Enter a valid zip code"
              }
            })}
          />
          {errors.postal_code && (
            <span className="text-[10px] font-medium text-red-400">{errors.postal_code.message}</span>
          )}
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-slate-400">Country</label>
          <input
            type="text"
            className="w-full rounded-xl px-4 py-3 text-sm glass-input"
            placeholder="e.g. United States"
            {...register("country", { required: "Country is required" })}
          />
          {errors.country && (
            <span className="text-[10px] font-medium text-red-400">{errors.country.message}</span>
          )}
        </div>
      </div>

      {/* Set default checkbox */}
      <div className="flex items-center gap-2 pt-2 select-none">
        <input
          type="checkbox"
          id="is_default"
          className="h-4.5 w-4.5 rounded border-white/10 bg-white/5 text-indigo-600 focus:ring-indigo-500/30 cursor-pointer"
          {...register("is_default")}
        />
        <label htmlFor="is_default" className="text-xs font-semibold text-slate-300 cursor-pointer">
          Set as default delivery address
        </label>
      </div>

      {/* Actions Buttons */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/5">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2.5 rounded-xl text-xs font-bold text-slate-400 hover:text-white transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-6 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 active:scale-95 transition-all shadow-md shadow-indigo-600/10 flex items-center gap-1.5"
        >
          {isSubmitting ? (
            <>
              <div className="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
              <span>Saving...</span>
            </>
          ) : (
            <span>Save Address</span>
          )}
        </button>
      </div>
    </form>
  );
}
