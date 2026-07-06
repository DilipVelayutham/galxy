import React from 'react';
import { Home, Briefcase, MapPin, Trash2, Edit3, CheckCircle } from 'lucide-react';

export interface Address {
  _id: string;
  label: 'Home' | 'Work' | 'Other';
  line1: string;
  line2?: string;
  city: string;
  state: string;
  pincode: string;
  is_default: boolean;
}

interface AddressCardProps {
  address: Address;
  onEdit: (address: Address) => void;
  onDelete: (addressId: string) => void;
  onSetDefault: (addressId: string) => void;
  isSettingDefault?: boolean;
}

export const AddressCard: React.FC<AddressCardProps> = ({
  address,
  onEdit,
  onDelete,
  onSetDefault,
  isSettingDefault = false
}) => {
  const getIcon = () => {
    switch (address.label) {
      case 'Home':
        return <Home className="w-5 h-5 text-[#FF2E8A]" />;
      case 'Work':
        return <Briefcase className="w-5 h-5 text-[#18E7FF]" />;
      default:
        return <MapPin className="w-5 h-5 text-[#9B5CFF]" />;
    }
  };

  return (
    <div
      className={`relative overflow-hidden rounded-2xl p-6 transition-all duration-300 transform hover:-translate-y-1 border ${
        address.is_default
          ? 'bg-[#16161C]/90 border-[#18E7FF] shadow-[0_0_20px_rgba(24,231,255,0.15)]'
          : 'bg-[#16161C]/50 border-neutral-800/80 hover:border-[#9B5CFF]/50 hover:shadow-[0_0_15px_rgba(155,92,255,0.08)]'
      } backdrop-blur-md`}
    >
      {/* Glow highlight for default */}
      {address.is_default && (
        <div className="absolute top-0 right-0 w-24 h-24 bg-[#18E7FF]/5 blur-[40px] pointer-events-none rounded-full" />
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-neutral-900 border border-neutral-800">
            {getIcon()}
          </div>
          <div>
            <h3 className="text-[#F4F4F7] font-semibold text-lg">{address.label}</h3>
            {address.is_default && (
              <span className="inline-flex items-center gap-1 mt-0.5 text-xs text-[#18E7FF] font-medium bg-[#18E7FF]/10 px-2 py-0.5 rounded-full border border-[#18E7FF]/20">
                <CheckCircle className="w-3 h-3" /> Default
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={() => onEdit(address)}
            className="p-2 rounded-lg text-[#8A8A97] hover:text-[#F4F4F7] hover:bg-neutral-800/60 transition-colors"
            title="Edit Address"
          >
            <Edit3 className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(address._id)}
            className="p-2 rounded-lg text-[#8A8A97] hover:text-rose-500 hover:bg-rose-500/10 transition-colors"
            title="Delete Address"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Body / Address lines */}
      <div className="space-y-1 text-sm text-[#8A8A97] mb-6">
        <p className="text-[#F4F4F7] font-medium">{address.line1}</p>
        {address.line2 && <p>{address.line2}</p>}
        <p>
          {address.city}, {address.state} - <span className="text-[#F4F4F7] font-mono">{address.pincode}</span>
        </p>
      </div>

      {/* Footer action */}
      {!address.is_default && (
        <button
          onClick={() => onSetDefault(address._id)}
          disabled={isSettingDefault}
          className="w-full py-2.5 px-4 text-xs font-semibold rounded-xl bg-neutral-900 hover:bg-neutral-800 text-[#8A8A97] hover:text-[#F4F4F7] border border-neutral-800 hover:border-[#18E7FF]/40 hover:shadow-[0_0_10px_rgba(24,231,255,0.1)] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSettingDefault ? 'Updating...' : 'Set as Default'}
        </button>
      )}
    </div>
  );
};
