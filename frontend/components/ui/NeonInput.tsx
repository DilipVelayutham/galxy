// components/ui/NeonInput.tsx
import { InputHTMLAttributes, forwardRef } from 'react';

type NeonInputProps = InputHTMLAttributes<HTMLInputElement>;

export const NeonInput = forwardRef<HTMLInputElement, NeonInputProps>(
  ({ className = '', ...rest }, ref) => {
    return (
      <input
        ref={ref}
        className={[
          'w-full px-3 py-2 rounded',
          'bg-panelCharcoal text-textPrimary',
          'border border-textMuted/30',
          'placeholder:text-textMuted',
          'focus:outline-none focus:border-primaryNeon focus:shadow-[0_0_8px_2px_#FF2E8A55]',
          'transition-all duration-200',
          className,
        ].join(' ')}
        {...rest}
      />
    );
  }
);

NeonInput.displayName = 'NeonInput';
