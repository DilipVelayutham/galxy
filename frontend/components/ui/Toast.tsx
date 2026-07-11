// components/ui/Toast.tsx
'use client';

import { useEffect } from 'react';

type Props = {
  message: string;
  onClose: () => void;
  duration?: number;
};

export const Toast = ({ message, onClose, duration = 3000 }: Props) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration]);

  return (
    <div
      role="status"
      aria-live="polite"
      className={[
        'fixed bottom-6 right-6 z-50',
        'flex items-center gap-3 px-5 py-3 rounded-lg',
        'bg-panelCharcoal border border-primaryNeon',
        'text-textPrimary text-sm font-medium',
        'shadow-[0_0_16px_4px_#FF2E8A55]',
        'animate-[fadeInUp_0.3s_ease-out_forwards]',
      ].join(' ')}
    >
      <span className="w-2 h-2 rounded-full bg-primaryNeon animate-pulse" />
      {message}
      <button
        onClick={onClose}
        aria-label="Dismiss notification"
        className="ml-2 text-textMuted hover:text-primaryNeon transition-colors"
      >
        ✕
      </button>
    </div>
  );
};
