"use client";

import React from "react";

export interface AttributeOption {
  value: string;
  label: string;
  price_delta?: number;
  preview_image?: string;
}

export interface AttributeField {
  key: string;
  label: string;
  type: "select" | "color_swatch" | "image_swatch" | "toggle" | "slider" | "text_input" | "number";
  options?: AttributeOption[];
  min?: number | null;
  max?: number | null;
  step?: number | null;
  required?: boolean;
  display_order?: number;
  affects_ai_preview?: boolean;
}

interface AttributeRendererProps {
  field: AttributeField;
  value: any;
  onChange: (value: any) => void;
  error?: string;
}

export const AttributeRenderer: React.FC<AttributeRendererProps> = ({
  field,
  value,
  onChange,
  error,
}) => {
  const { key, label, type, options = [], min, max, step } = field;

  // Swatch color mapping helper
  const getSwatchBg = (valStr: string) => {
    const v = valStr.toLowerCase();
    if (v.includes("pink") || v.includes("magenta")) return "bg-[#FF2E8A]";
    if (v.includes("blue") || v.includes("electric")) return "bg-[#18E7FF]";
    if (v.includes("violet") || v.includes("purple")) return "bg-[#9B5CFF]";
    if (v.includes("yellow") || v.includes("gold")) return "bg-[#FFD84D]";
    return "bg-panel-charcoal";
  };

  const renderInput = () => {
    switch (type) {
      case "select":
        return (
          <select
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            className="w-full p-3 rounded-lg bg-panel-charcoal border border-panel-charcoal focus:border-neon-blue/40 text-text-primary text-sm focus:outline-none transition-colors cursor-pointer"
          >
            <option value="" disabled>Select {label}</option>
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label} {opt.price_delta ? `(+₹${opt.price_delta})` : ""}
              </option>
            ))}
          </select>
        );

      case "color_swatch":
        return (
          <div className="flex flex-wrap gap-3">
            {options.map((opt) => {
              const isSelected = value === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => onChange(opt.value)}
                  className={`w-9 h-9 rounded-full ${getSwatchBg(opt.value)} border-2 transition-all cursor-pointer ${
                    isSelected
                      ? "border-text-primary scale-110 drop-shadow-[0_0_8px_rgba(255,255,255,0.4)]"
                      : "border-transparent opacity-75 hover:opacity-100 hover:scale-105"
                  }`}
                  title={`${opt.label} (+₹${opt.price_delta || 0})`}
                />
              );
            })}
          </div>
        );

      case "image_swatch":
        return (
          <div className="grid grid-cols-3 gap-3">
            {options.map((opt) => {
              const isSelected = value === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => onChange(opt.value)}
                  className={`p-1.5 rounded-lg border bg-panel-charcoal/40 transition-all flex flex-col items-center gap-1 cursor-pointer hover:border-neon-violet/30 ${
                    isSelected
                      ? "border-neon-violet glow-violet scale-[1.03]"
                      : "border-panel-charcoal opacity-70 hover:opacity-100"
                  }`}
                >
                  {opt.preview_image ? (
                    <img
                      src={opt.preview_image}
                      alt={opt.label}
                      className="w-full h-12 object-cover rounded"
                    />
                  ) : (
                    <div className="w-full h-12 bg-void-black rounded flex items-center justify-center text-[10px] text-text-muted">
                      No Preview
                    </div>
                  )}
                  <span className="text-[10px] font-bold text-center truncate w-full text-text-primary">
                    {opt.label}
                  </span>
                  {opt.price_delta ? (
                    <span className="text-[9px] text-neon-violet font-bold">+₹{opt.price_delta}</span>
                  ) : null}
                </button>
              );
            })}
          </div>
        );

      case "toggle":
        const isChecked = value === true || value === "true";
        return (
          <label className="flex items-center gap-3 cursor-pointer select-none">
            <button
              type="button"
              onClick={() => onChange(!isChecked)}
              className={`w-11 h-6 rounded-full p-0.5 transition-colors duration-200 focus:outline-none flex items-center ${
                isChecked ? "bg-neon-blue" : "bg-panel-charcoal"
              }`}
            >
              <div
                className={`w-5 h-5 rounded-full bg-text-primary shadow transform duration-200 ease-out ${
                  isChecked ? "translate-x-5" : "translate-x-0"
                }`}
              />
            </button>
            <span className="text-sm text-text-primary">
              {options[0]?.label || "Enable Option"} {options[0]?.price_delta ? `(+₹${options[0].price_delta})` : ""}
            </span>
          </label>
        );

      case "slider":
        const sliderMin = min !== null && min !== undefined ? min : 1;
        const sliderMax = max !== null && max !== undefined ? max : 5;
        const sliderStep = step !== null && step !== undefined ? step : 1;
        return (
          <div className="flex flex-col gap-1 w-full">
            <div className="flex justify-between text-xs text-text-muted font-semibold">
              <span>Min: {sliderMin}</span>
              <span className="text-neon-pink font-bold">Value: {value !== undefined ? value : sliderMin}</span>
              <span>Max: {sliderMax}</span>
            </div>
            <input
              type="range"
              min={sliderMin}
              max={sliderMax}
              step={sliderStep}
              value={value !== undefined ? value : sliderMin}
              onChange={(e) => onChange(parseFloat(e.target.value))}
              className="w-full accent-neon-pink cursor-pointer h-1 bg-panel-charcoal rounded-lg appearance-none"
            />
          </div>
        );

      case "text_input":
        return (
          <input
            type="text"
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder={`Enter ${label}...`}
            className="w-full p-3 rounded-lg bg-panel-charcoal border border-panel-charcoal focus:border-neon-blue/40 text-text-primary text-sm focus:outline-none transition-colors"
          />
        );

      case "number":
        return (
          <input
            type="number"
            min={min !== null ? min : undefined}
            max={max !== null ? max : undefined}
            step={step !== null ? step : undefined}
            value={value === undefined ? "" : value}
            onChange={(e) => onChange(e.target.value === "" ? "" : parseFloat(e.target.value))}
            placeholder={`Enter number...`}
            className="w-full p-3 rounded-lg bg-panel-charcoal border border-panel-charcoal focus:border-neon-blue/40 text-text-primary text-sm focus:outline-none transition-colors"
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col gap-2.5">
      <label className="text-xs text-text-muted uppercase tracking-wider font-bold">
        {label} {field.required && <span className="text-neon-pink">*</span>}
      </label>
      {renderInput()}
      {error && (
        <span className="text-[10px] text-neon-pink font-bold mt-0.5">{error}</span>
      )}
    </div>
  );
};
