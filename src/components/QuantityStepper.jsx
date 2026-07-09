import { Plus, Minus, Loader2 } from 'lucide-react';

export default function QuantityStepper({ quantity, onIncrement, onDecrement, isMutating, disabled }) {
  return (
    <div className={`flex items-center bg-tertiary border border-white/5 rounded-lg overflow-hidden h-9 px-1 ${disabled ? 'opacity-40 pointer-events-none' : ''}`}>
      <button
        onClick={onDecrement}
        disabled={isMutating || disabled}
        className="w-7 h-7 flex items-center justify-center rounded-md hover:bg-white/5 text-text-secondary hover:text-text-primary transition-colors disabled:opacity-50"
        aria-label="Decrease quantity"
      >
        <Minus size={14} />
      </button>

      <span className="w-8 text-center text-sm font-semibold select-none flex items-center justify-center">
        {isMutating ? (
          <Loader2 size={12} className="animate-spin text-accent-cyan" />
        ) : (
          quantity
        )}
      </span>

      <button
        onClick={onIncrement}
        disabled={isMutating || disabled}
        className="w-7 h-7 flex items-center justify-center rounded-md hover:bg-white/5 text-text-secondary hover:text-text-primary transition-colors disabled:opacity-50"
        aria-label="Increase quantity"
      >
        <Plus size={14} />
      </button>
    </div>
  );
}
