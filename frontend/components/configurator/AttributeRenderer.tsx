'use client';

import React from 'react';

export interface AttributeOption {
  value: string;
  label: string;
  price_delta: number;
  preview_image?: string;
  color_code?: string; // Hex code for color swatches
}

export interface AttributeSchema {
  key: string;
  label: string;
  type: 'select' | 'color_swatch' | 'image_swatch' | 'toggle' | 'slider' | 'text_input' | 'number';
  options?: AttributeOption[];
  min?: number | null;
  max?: number | null;
  step?: number | null;
  required?: boolean;
  display_order?: number;
}

interface AttributeRendererProps {
  schema: AttributeSchema;
  selectedValue: string | number | boolean | null | undefined;
  onChange: (value: string | number | boolean) => void;
  error?: string;
}

export default function AttributeRenderer({
  schema,
  selectedValue,
  onChange,
  error,
}: AttributeRendererProps) {
  const { label, type, options = [], min = 0, max = 100, step = 1 } = schema;

  return (
    <div className="flex flex-col gap-2 mb-6">
      <div className="flex justify-between items-center">
        <label className="text-sm font-semibold text-text-primary uppercase tracking-wider">
          {label}
        </label>
        {error && (
          <span className="text-xs font-semibold text-neon-yellow animate-pulse">
            {error}
          </span>
        )}
      </div>

      {/* RENDER BY TYPE */}
      {type === 'select' && (
        <select
          value={selectedValue !== undefined && selectedValue !== null ? String(selectedValue) : ''}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-4 py-2.5 rounded-lg bg-surface-panel border border-white/10 text-text-primary focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue transition-colors duration-200"
        >
          <option value="" disabled>Select an option</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label} {opt.price_delta > 0 ? `(+₹${opt.price_delta})` : ''}
            </option>
          ))}
        </select>
      )}

      {type === 'color_swatch' && (
        <div className="flex flex-wrap gap-3">
          {options.map((opt) => {
            const isSelected = selectedValue === opt.value;
            // Generate some colors if not provided
            const colorBg = opt.color_code || (
              opt.value.toLowerCase().includes('pink') ? '#FF2E8A' :
              opt.value.toLowerCase().includes('blue') ? '#18E7FF' :
              opt.value.toLowerCase().includes('violet') ? '#9B5CFF' :
              opt.value.toLowerCase().includes('yellow') ? '#FFD84D' : '#ffffff'
            );
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => onChange(opt.value)}
                className={`group relative flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-200 ${
                  isSelected ? 'border-text-primary scale-110 shadow-md' : 'border-transparent hover:scale-105'
                }`}
                style={{
                  backgroundColor: colorBg,
                  boxShadow: isSelected ? `0 0 12px ${colorBg}` : 'none',
                }}
                title={`${opt.label} (${opt.price_delta > 0 ? `+₹${opt.price_delta}` : 'Free'})`}
              >
                {/* Visual Dot in Center of Selected Swatch */}
                {isSelected && (
                  <div className="w-2.5 h-2.5 rounded-full bg-void-black" style={{ backgroundColor: '#0B0B0F' }} />
                )}
                {/* Tooltip on Hover */}
                <span className="absolute bottom-full mb-2 hidden group-hover:block z-10 bg-surface-panel text-text-primary text-xs py-1 px-2 rounded border border-white/10 whitespace-nowrap">
                  {opt.label} {opt.price_delta > 0 ? `(+₹${opt.price_delta})` : ''}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {type === 'image_swatch' && (
        <div className="grid grid-cols-3 gap-3">
          {options.map((opt) => {
            const isSelected = selectedValue === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => onChange(opt.value)}
                className={`relative flex flex-col items-center justify-between p-2 rounded-lg border bg-surface-panel transition-all duration-200 ${
                  isSelected ? 'border-neon-pink shadow-glow-pink scale-[1.02]' : 'border-white/10 hover:border-white/20'
                }`}
              >
                {opt.preview_image ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={opt.preview_image}
                    alt={opt.label}
                    className="w-full h-16 object-cover rounded-md mb-2"
                  />
                ) : (
                  <div className="w-full h-16 rounded-md bg-void-black/50 border border-white/5 flex items-center justify-center text-xs text-text-muted mb-2">
                    No Preview
                  </div>
                )}
                <span className="text-xs font-medium text-text-primary text-center truncate w-full">
                  {opt.label}
                </span>
                <span className="text-[10px] text-neon-blue mt-1">
                  {opt.price_delta > 0 ? `+₹${opt.price_delta}` : 'Included'}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {type === 'toggle' && (
        <div className="flex gap-2">
          {options.map((opt) => {
            const isSelected = selectedValue === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => onChange(opt.value)}
                className={`flex-1 py-2.5 px-4 rounded-lg border text-sm font-semibold transition-all duration-200 ${
                  isSelected
                    ? 'bg-neon-violet/10 border-neon-violet text-neon-violet shadow-glow-violet'
                    : 'bg-surface-panel border-white/10 text-text-muted hover:border-white/20 hover:text-text-primary'
                }`}
              >
                {opt.label} {opt.price_delta > 0 ? `(+₹${opt.price_delta})` : ''}
              </button>
            );
          })}
        </div>
      )}

      {type === 'slider' && (
        <div className="flex flex-col gap-1 py-2">
          <input
            type="range"
            min={min || 0}
            max={max || 100}
            step={step || 1}
            value={typeof selectedValue === 'number' ? selectedValue : (min || 0)}
            onChange={(e) => onChange(Number(e.target.value))}
            className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-neon-pink"
          />
          <div className="flex justify-between text-xs text-text-muted mt-1">
            <span>{min}</span>
            <span className="text-neon-pink font-semibold">{typeof selectedValue === 'number' ? selectedValue : min}</span>
            <span>{max}</span>
          </div>
        </div>
      )}

      {type === 'text_input' && (
        <input
          type="text"
          value={typeof selectedValue === 'string' ? selectedValue : ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder={`Enter custom text (e.g. your name)`}
          className="w-full px-4 py-2.5 rounded-lg bg-surface-panel border border-white/10 text-text-primary focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue transition-colors duration-200 placeholder-white/20"
        />
      )}

      {type === 'number' && (
        <input
          type="number"
          min={min || 1}
          max={max || 999}
          value={typeof selectedValue === 'number' ? selectedValue : ''}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full px-4 py-2.5 rounded-lg bg-surface-panel border border-white/10 text-text-primary focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue transition-colors duration-200"
        />
      )}
    </div>
  );
}
