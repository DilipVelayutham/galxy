// components/admin/SchemaWarningModal.tsx
'use client';
import { NeonButton } from '@/components/ui/NeonButton';
import { ReactNode } from 'react';

type Props = {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  children?: ReactNode;
};

export const SchemaWarningModal = ({ isOpen, onConfirm, onCancel, children }: Props) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/70 backdrop-blur-sm z-50">
      <div className="bg-panelCharcoal p-6 rounded-lg shadow-neon neon-glow max-w-md w-full">
        <h4 className="text-lg font-bold text-primaryNeon mb-4">
          Warning – Schema Modification
        </h4>
        <p className="mb-6 text-textPrimary">{children ?? 'Changing or removing an attribute may affect existing products, carts and historical orders.'}</p>
        <div className="flex justify-end gap-3">
          <NeonButton variant="secondary" onClick={onCancel}>
            Cancel
          </NeonButton>
          <NeonButton variant="danger" onClick={onConfirm}>
            Proceed
          </NeonButton>
        </div>
      </div>
    </div>
  );
};
