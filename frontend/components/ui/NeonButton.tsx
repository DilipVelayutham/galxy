// components/ui/NeonButton.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react';

type Variant = 'primary' | 'secondary' | 'danger';

interface NeonButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const variantClasses: Record<Variant, string> = {
  primary:
    'border-primaryNeon text-primaryNeon shadow-[0_0_8px_2px_#FF2E8A55] hover:bg-primaryNeon hover:text-voidBlack',
  secondary:
    'border-secondaryNeon text-secondaryNeon shadow-[0_0_8px_2px_#18E7FF33] hover:bg-secondaryNeon hover:text-voidBlack',
  danger:
    'border-red-500 text-red-400 shadow-[0_0_8px_2px_#ef444433] hover:bg-red-500 hover:text-white',
};

export const NeonButton = forwardRef<HTMLButtonElement, NeonButtonProps>(
  ({ variant = 'primary', className = '', children, disabled, ...rest }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled}
        className={[
          'inline-flex items-center justify-center gap-2 px-4 py-2 rounded',
          'border font-semibold text-sm tracking-wide',
          'transition-all duration-200 cursor-pointer',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-voidBlack',
          disabled ? 'opacity-40 cursor-not-allowed' : variantClasses[variant],
          className,
        ].join(' ')}
        {...rest}
      >
        {children}
      </button>
    );
  }
);

NeonButton.displayName = 'NeonButton';
