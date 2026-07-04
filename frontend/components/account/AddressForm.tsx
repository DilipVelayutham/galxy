import React, { useState, useEffect } from 'react';
import { X, Check } from 'lucide-react';
import { Address } from './AddressCard';

interface AddressFormProps {
  address?: Address; // If present, we are editing; if not, we are adding
  onSave: (data: Omit<Address, '_id'> & { _id?: string }) => Promise<void>;
  onClose: () => void;
  isSaving?: boolean;
}

export const AddressForm: React.FC<AddressFormProps> = ({
  address,
  onSave,
  onClose,
  isSaving = false
}) => {
  const [formData, setFormData] = useState({
    label: 'Home' as 'Home' | 'Work' | 'Other',
    line1: '',
    line2: '',
    city: '',
    state: '',
    pincode: '',
    is_default: false
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (address) {
      setFormData({
        label: address.label,
        line1: address.line1,
        line2: address.line2 || '',
        city: address.city,
        state: address.state,
        pincode: address.pincode,
        is_default: address.is_default
      });
    }
  }, [address]);

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.line1.trim()) {
      newErrors.line1 = 'Street address is required.';
    }

    if (!formData.city.trim()) {
      newErrors.city = 'City is required.';
    }

    if (!formData.state.trim()) {
      newErrors.state = 'State is required.';
    }

    // Pincode validation: 6-digit numeric
    const pinStr = formData.pincode.trim();
    if (!pinStr) {
      newErrors.pincode = 'Pincode is required.';
    } else if (!/^\d{6}$/.test(pinStr)) {
      newErrors.pincode = 'Pincode must be exactly 6 digits.';
    }

    // Label validation
    if (!['Home', 'Work', 'Other'].includes(formData.label)) {
      newErrors.label = 'Label must be Home, Work, or Other.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      await onSave({
        ...formData,
        _id: address?._id
      });
    } catch (err: any) {
      // Parse backend validation error response if applicable
      if (err.errors) {
        setErrors(err.errors);
      } else {
        setErrors({ general: err.message || 'An error occurred.' });
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-lg overflow-hidden rounded-2xl bg-[#16161C] border border-neutral-800/80 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        {/* Border glow */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-[#FF2E8A] via-[#9B5CFF] to-[#18E7FF]" />
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-neutral-800/50">
          <h2 className="text-xl font-bold text-[#F4F4F7] tracking-tight">
            {address ? 'Edit Delivery Address' : 'Add New Address'}
          </h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#8A8A97] hover:text-[#F4F4F7] hover:bg-neutral-800/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {errors.general && (
            <div className="p-3 text-sm text-[#FFD84D] bg-[#FFD84D]/10 border border-[#FFD84D]/20 rounded-xl">
              {errors.general}
            </div>
          )}

          {/* Label Selector */}
          <div>
            <label className="block text-xs font-semibold text-[#8A8A97] uppercase tracking-wider mb-2">Address Type</label>
            <div className="grid grid-cols-3 gap-3">
              {(['Home', 'Work', 'Other'] as const).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setFormData({ ...formData, label: type })}
                  className={`py-2 px-4 rounded-xl border text-sm font-semibold transition-all duration-300 ${
                    formData.label === type
                      ? 'bg-neutral-900 border-[#FF2E8A] text-[#FF2E8A] shadow-[0_0_10px_rgba(255,46,138,0.15)]'
                      : 'bg-neutral-900/40 border-neutral-800 text-[#8A8A97] hover:border-neutral-700 hover:text-[#F4F4F7]'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
            {errors.label && <p className="mt-1 text-xs text-[#FFD84D]">{errors.label}</p>}
          </div>

          {/* Line 1 */}
          <div>
            <label className="block text-xs font-semibold text-[#8A8A97] uppercase tracking-wider mb-2">Street Address</label>
            <input
              type="text"
              value={formData.line1}
              onChange={(e) => setFormData({ ...formData, line1: e.target.value })}
              placeholder="e.g. 12, Park Avenue"
              className={`w-full py-2.5 px-4 rounded-xl bg-neutral-900/60 border text-sm text-[#F4F4F7] placeholder-neutral-700 focus:outline-none transition-all duration-300 ${
                errors.line1
                  ? 'border-[#FFD84D] focus:border-[#FFD84D]'
                  : 'border-neutral-800 focus:border-[#FF2E8A] focus:shadow-[0_0_15px_rgba(255,46,138,0.15)]'
              }`}
            />
            {errors.line1 && <p className="mt-1 text-xs text-[#FFD84D]">{errors.line1}</p>}
          </div>

          {/* Line 2 */}
          <div>
            <label className="block text-xs font-semibold text-[#8A8A97] uppercase tracking-wider mb-2">Address Line 2 (Optional)</label>
            <input
              type="text"
              value={formData.line2}
              onChange={(e) => setFormData({ ...formData, line2: e.target.value })}
              placeholder="Apartment, suite, unit, etc."
              className="w-full py-2.5 px-4 rounded-xl bg-neutral-900/60 border border-neutral-800 focus:border-[#FF2E8A] text-sm text-[#F4F4F7] placeholder-neutral-700 focus:outline-none transition-all duration-300 focus:shadow-[0_0_15px_rgba(255,46,138,0.15)]"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* City */}
            <div>
              <label className="block text-xs font-semibold text-[#8A8A97] uppercase tracking-wider mb-2">City</label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                placeholder="City"
                className={`w-full py-2.5 px-4 rounded-xl bg-neutral-900/60 border text-sm text-[#F4F4F7] placeholder-neutral-700 focus:outline-none transition-all duration-300 ${
                  errors.city
                    ? 'border-[#FFD84D] focus:border-[#FFD84D]'
                    : 'border-neutral-800 focus:border-[#FF2E8A] focus:shadow-[0_0_15px_rgba(255,46,138,0.15)]'
                }`}
              />
              {errors.city && <p className="mt-1 text-xs text-[#FFD84D]">{errors.city}</p>}
            </div>

            {/* State */}
            <div>
              <label className="block text-xs font-semibold text-[#8A8A97] uppercase tracking-wider mb-2">State</label>
              <input
                type="text"
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                placeholder="State"
                className={`w-full py-2.5 px-4 rounded-xl bg-neutral-900/60 border text-sm text-[#F4F4F7] placeholder-neutral-700 focus:outline-none transition-all duration-300 ${
                  errors.state
                    ? 'border-[#FFD84D] focus:border-[#FFD84D]'
                    : 'border-neutral-800 focus:border-[#FF2E8A] focus:shadow-[0_0_15px_rgba(255,46,138,0.15)]'
                }`}
              />
              {errors.state && <p className="mt-1 text-xs text-[#FFD84D]">{errors.state}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Pincode */}
            <div>
              <label className="block text-xs font-semibold text-[#8A8A97] uppercase tracking-wider mb-2">Pincode</label>
              <input
                type="text"
                value={formData.pincode}
                onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                placeholder="6-digit PIN"
                maxLength={6}
                className={`w-full py-2.5 px-4 rounded-xl bg-neutral-900/60 border text-sm text-[#F4F4F7] placeholder-neutral-700 focus:outline-none transition-all duration-300 ${
                  errors.pincode
                    ? 'border-[#FFD84D] focus:border-[#FFD84D]'
                    : 'border-neutral-800 focus:border-[#FF2E8A] focus:shadow-[0_0_15px_rgba(255,46,138,0.15)]'
                }`}
              />
              {errors.pincode && <p className="mt-1 text-xs text-[#FFD84D]">{errors.pincode}</p>}
            </div>

            {/* Set Default Checkbox */}
            <div className="flex items-center pt-8">
              <label className="flex items-center gap-3 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={formData.is_default}
                  onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                  className="sr-only"
                />
                <div
                  className={`flex items-center justify-center w-5 h-5 rounded-md border transition-all ${
                    formData.is_default
                      ? 'bg-[#FF2E8A] border-[#FF2E8A] shadow-[0_0_8px_rgba(255,46,138,0.3)]'
                      : 'border-neutral-700 hover:border-neutral-500'
                  }`}
                >
                  {formData.is_default && <Check className="w-3.5 h-3.5 text-white" />}
                </div>
                <span className="text-sm font-medium text-[#8A8A97] hover:text-[#F4F4F7]">
                  Make default address
                </span>
              </label>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-neutral-800/50">
            <button
              type="button"
              onClick={onClose}
              className="py-2.5 px-5 rounded-xl border border-neutral-800 text-[#8A8A97] hover:text-[#F4F4F7] hover:bg-neutral-800/40 text-sm font-semibold transition-all duration-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="relative py-2.5 px-6 rounded-xl bg-gradient-to-r from-[#FF2E8A] to-[#9B5CFF] text-[#F4F4F7] font-semibold text-sm hover:shadow-[0_0_20px_rgba(255,46,138,0.3)] hover:brightness-110 active:scale-[0.98] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? 'Saving...' : address ? 'Save Changes' : 'Add Address'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
