import { useState } from 'react';
import { Trash2, AlertTriangle, ChevronDown, ChevronUp, Edit3 } from 'lucide-react';
import QuantityStepper from './QuantityStepper';

export default function CartItemRow({ item, isMutating, onUpdateQty, onRemove, layout = 'full', onFixSelection }) {
  const [expanded, setExpanded] = useState(false);
  const isCompact = layout === 'compact';

  const unitPrice = isNaN(Number(item.unit_price_estimate)) || Number(item.unit_price_estimate) < 0 ? 0 : Number(item.unit_price_estimate);
  const lineTotal = isNaN(Number(item.line_total_estimate)) || Number(item.line_total_estimate) < 0 ? 0 : Number(item.line_total_estimate);

  const hasAttributes = item.selected_attributes && item.selected_attributes.length > 0;
  const isAvailable = item.is_available !== false;
  const needsAttention = item.needs_attention === true;

  return (
    <div 
      className={`glass-card rounded-xl p-4 mb-4 border transition-all duration-300 ${
        !isAvailable 
          ? 'opacity-65 grayscale bg-black/40 border-red-500/10' 
          : needsAttention
            ? 'border-amber-500/30 bg-amber-500/[0.02]' 
            : 'border-white/5 hover:border-white/10'
      }`}
    >
      {/* Needs Attention Alert Banner */}
      {needsAttention && isAvailable && (
        <div className="flex items-center gap-2 mb-3 bg-amber-500/10 border border-amber-500/20 text-amber-400 p-2.5 rounded-lg text-xs font-medium">
          <AlertTriangle size={14} className="flex-shrink-0" />
          <div className="flex-grow">
            <span className="font-semibold">Requires Attention:</span> {item.error_message || "This option has changed."}
          </div>
          {onFixSelection && (
            <button
              onClick={() => onFixSelection(item)}
              className="flex items-center gap-1 bg-amber-500/20 hover:bg-amber-500/35 text-amber-200 px-2.5 py-1 rounded border border-amber-500/30 font-semibold transition-colors"
            >
              <Edit3 size={11} />
              Fix
            </button>
          )}
        </div>
      )}

      {/* Unavailable Alert Banner */}
      {!isAvailable && (
        <div className="flex items-center gap-2 mb-3 bg-red-500/10 border border-red-500/20 text-red-400 p-2.5 rounded-lg text-xs font-medium">
          <AlertTriangle size={14} className="flex-shrink-0" />
          <div className="flex-grow">
            <span className="font-semibold">No longer available:</span> This item or option configuration is out of stock.
          </div>
        </div>
      )}

      <div className="flex gap-4">
        {/* Thumbnail Image */}
        <div className="relative w-16 h-16 sm:w-20 sm:h-20 bg-tertiary rounded-lg overflow-hidden border border-white/5 flex-shrink-0">
          <img 
            src={item.thumbnail} 
            alt={item.product_title} 
            className="w-full h-full object-cover"
          />
          {!isAvailable && (
            <div className="absolute inset-0 bg-black/60 flex items-center justify-center text-[10px] font-bold text-red-400 tracking-wider uppercase">
              Sold Out
            </div>
          )}
        </div>

        {/* Product Details Column */}
        <div className="flex-grow min-w-0 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-start gap-2">
              <div>
                <span className="text-[10px] font-bold tracking-wider text-accent-pink uppercase opacity-80">
                  {item.category_name}
                </span>
                <h4 className="text-sm sm:text-base font-semibold text-text-primary truncate mt-0.5">
                  {item.product_title}
                </h4>
              </div>
              
              {/* Unit Price (Rendered exactly as returned) */}
              <div className="text-right">
                <span className="text-sm font-semibold text-text-primary">
                  ${unitPrice}
                </span>
                {!isCompact && (
                  <div className="text-[10px] text-text-muted">each</div>
                )}
              </div>
            </div>

            {/* Selected Attributes Summary */}
            {hasAttributes && (
              <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
                {isCompact ? (
                  <p className="text-[11px] text-text-secondary truncate max-w-full">
                    {item.selected_attributes.map(attr => `${attr.name}: ${attr.value}`).join(', ')}
                  </p>
                ) : (
                  <button 
                    onClick={() => setExpanded(!expanded)}
                    className="text-[11px] text-accent-cyan flex items-center gap-0.5 hover:underline"
                  >
                    {expanded ? "Hide Configuration" : "Show Configuration"} 
                    {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  </button>
                )}
              </div>
            )}

            {/* Custom Engraving/Text Requests */}
            {item.custom_text && !isCompact && (
              <div className="mt-2 text-xs bg-white/[0.02] border border-white/5 p-2 rounded-lg text-text-secondary italic">
                <span className="text-[10px] font-bold tracking-wide uppercase text-text-muted not-italic block mb-0.5">
                  Custom Request
                </span>
                "{item.custom_text}"
              </div>
            )}
          </div>

          {/* Sub-attributes Expanded Panel */}
          {expanded && !isCompact && hasAttributes && (
            <div className="mt-3 p-3 bg-tertiary rounded-lg border border-white/5 text-xs animate-fade-in">
              <div className="font-semibold text-text-secondary border-b border-white/5 pb-1.5 mb-2 uppercase text-[10px] tracking-wider">
                Configuration Details
              </div>
              <ul className="space-y-1.5">
                {item.selected_attributes.map((attr, index) => (
                  <li key={index} className="flex justify-between items-center text-text-secondary">
                    <span>{attr.name}: <strong className="text-text-primary">{attr.value}</strong></span>
                    {attr.price_modifier > 0 && (
                      <span className="text-accent-green font-medium">
                        +${attr.price_modifier}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Stepper + Total Price Row */}
          <div className="flex justify-between items-center mt-3 pt-2 border-t border-white/5">
            <div className="flex items-center gap-2">
              <QuantityStepper 
                quantity={item.quantity}
                onIncrement={() => onUpdateQty(item._id, item.quantity + 1)}
                onDecrement={() => onUpdateQty(item._id, item.quantity - 1)}
                isMutating={isMutating}
                disabled={!isAvailable}
              />
              
              <button 
                onClick={() => onRemove(item._id)}
                className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-red-500/10 text-text-secondary hover:text-red-400 border border-white/5 hover:border-red-500/20 transition-all"
                title="Remove item"
              >
                <Trash2 size={16} />
              </button>
            </div>

            {/* Line Total Estimate (Rendered exactly as returned) */}
            <div className="text-right">
              <div className="text-[10px] text-text-secondary">Total</div>
              <div className="text-base sm:text-lg font-bold text-accent-cyan glow-text-cyan">
                ${lineTotal}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
