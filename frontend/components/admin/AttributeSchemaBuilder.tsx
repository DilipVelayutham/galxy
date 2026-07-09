"use client";

import React, { useState } from "react";
import { Plus, Trash, ArrowUp, ArrowDown, Settings, Save, Edit3, X } from "lucide-react";
import { AttributeField, AttributeOption } from "../configurator/AttributeRenderer";
import { useToast } from "@/context/ToastContext";

interface AttributeSchemaBuilderProps {
  initialSchema: AttributeField[];
  onSave: (schema: AttributeField[]) => Promise<void>;
}

export const AttributeSchemaBuilder: React.FC<AttributeSchemaBuilderProps> = ({
  initialSchema,
  onSave,
}) => {
  const [schema, setSchema] = useState<AttributeField[]>(initialSchema || []);
  const [editingFieldIdx, setEditingFieldIdx] = useState<number | null>(null);
  const [saving, setSaving] = useState<boolean>(false);
  const { showToast } = useToast();

  const handleAddField = () => {
    const newField: AttributeField = {
      key: `field_${Date.now().toString().slice(-4)}`,
      label: "New Configuration Option",
      type: "select",
      options: [
        { value: "option_1", label: "Option 1", price_delta: 0 }
      ],
      min: null,
      max: null,
      step: null,
      required: true,
      display_order: schema.length + 1,
      affects_ai_preview: true
    };
    
    setSchema((prev) => [...prev, newField]);
    setEditingFieldIdx(schema.length);
  };

  const handleRemoveField = (idx: number) => {
    setSchema((prev) => {
      const filtered = prev.filter((_, i) => i !== idx);
      // Recalculate display orders
      return filtered.map((field, i) => ({ ...field, display_order: i + 1 }));
    });
    if (editingFieldIdx === idx) {
      setEditingFieldIdx(null);
    } else if (editingFieldIdx !== null && editingFieldIdx > idx) {
      setEditingFieldIdx(editingFieldIdx - 1);
    }
  };

  const handleMoveField = (idx: number, direction: "up" | "down") => {
    if (direction === "up" && idx === 0) return;
    if (direction === "down" && idx === schema.length - 1) return;
    
    const targetIdx = direction === "up" ? idx - 1 : idx + 1;
    const nextSchema = [...schema];
    
    // Swap items
    const temp = nextSchema[idx];
    nextSchema[idx] = nextSchema[targetIdx];
    nextSchema[targetIdx] = temp;
    
    // Recalculate display orders
    const reordered = nextSchema.map((field, i) => ({ ...field, display_order: i + 1 }));
    
    setSchema(reordered);
    if (editingFieldIdx === idx) setEditingFieldIdx(targetIdx);
    else if (editingFieldIdx === targetIdx) setEditingFieldIdx(idx);
  };

  const handleFieldChange = (idx: number, keyName: keyof AttributeField, value: any) => {
    setSchema((prev) => {
      const next = [...prev];
      next[idx] = { ...next[idx], [keyName]: value };
      return next;
    });
  };

  // Option updates for list-type attributes
  const handleAddOption = (fieldIdx: number) => {
    const field = schema[fieldIdx];
    const opts = field.options ? [...field.options] : [];
    
    opts.push({
      value: `value_${Date.now().toString().slice(-4)}`,
      label: "New Option Item",
      price_delta: 0
    });
    
    handleFieldChange(fieldIdx, "options", opts);
  };

  const handleRemoveOption = (fieldIdx: number, optIdx: number) => {
    const field = schema[fieldIdx];
    const opts = field.options ? field.options.filter((_, i) => i !== optIdx) : [];
    handleFieldChange(fieldIdx, "options", opts);
  };

  const handleOptionChange = (fieldIdx: number, optIdx: number, optionKey: keyof AttributeOption, value: any) => {
    const field = schema[fieldIdx];
    if (!field.options) return;
    
    const nextOpts = [...field.options];
    nextOpts[optIdx] = { ...nextOpts[optIdx], [optionKey]: value };
    
    handleFieldChange(fieldIdx, "options", nextOpts);
  };

  const handleSaveSchema = async () => {
    // Validate uniqueness of field keys
    const keys = schema.map((f) => f.key.trim().toLowerCase());
    const uniqueKeys = new Set(keys);
    if (uniqueKeys.size !== keys.length) {
      showToast("Option keys must be unique. Check for duplicate keys.", "error");
      return;
    }

    setSaving(true);
    try {
      await onSave(schema);
      showToast("Configuration schema saved!", "success");
      setEditingFieldIdx(null);
    } catch (err: any) {
      showToast(err.message || "Failed to save schema changes", "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Sidebar: Option Fields list */}
      <div className="flex-1 p-5 rounded-xl bg-panel-charcoal/30 border border-panel-charcoal flex flex-col gap-4">
        <div className="flex items-center justify-between border-b border-panel-charcoal pb-3">
          <h3 className="text-base font-bold text-text-primary">Attribute Schema List</h3>
          <button
            type="button"
            onClick={handleAddField}
            className="p-1.5 rounded-lg bg-neon-violet/10 text-neon-violet border border-neon-violet/20 hover:bg-neon-violet/20 transition-all flex items-center gap-1 text-xs font-bold cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" /> Add Option
          </button>
        </div>

        {schema.length === 0 ? (
          <div className="py-8 text-center text-xs text-text-muted">
            No configurable options defined. Add one above.
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {schema.map((field, idx) => {
              const isEditing = editingFieldIdx === idx;
              return (
                <div
                  key={idx}
                  className={`p-3 rounded-lg border transition-all flex items-center justify-between gap-4 ${
                    isEditing 
                      ? "border-neon-violet bg-neon-violet/5" 
                      : "border-panel-charcoal/50 bg-void-black/20 hover:border-text-muted/30"
                  }`}
                >
                  <div className="flex-1 flex flex-col min-w-0" onClick={() => setEditingFieldIdx(idx)}>
                    <span className="text-xs font-bold text-text-primary truncate cursor-pointer">
                      {field.label}
                    </span>
                    <span className="text-[10px] text-text-muted mt-0.5">
                      Key: <code className="text-neon-blue">{field.key}</code> · Type: <span className="capitalize">{field.type.replace("_", " ")}</span>
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 flex-shrink-0">
                    <button
                      type="button"
                      disabled={idx === 0}
                      onClick={() => handleMoveField(idx, "up")}
                      className="p-1 text-text-muted hover:text-text-primary disabled:opacity-20 cursor-pointer"
                    >
                      <ArrowUp className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      disabled={idx === schema.length - 1}
                      onClick={() => handleMoveField(idx, "down")}
                      className="p-1 text-text-muted hover:text-text-primary disabled:opacity-20 cursor-pointer"
                    >
                      <ArrowDown className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditingFieldIdx(isEditing ? null : idx)}
                      className="p-1 text-neon-blue hover:text-text-primary cursor-pointer"
                    >
                      <Settings className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleRemoveField(idx)}
                      className="p-1 text-neon-pink hover:text-text-primary cursor-pointer"
                    >
                      <Trash className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <button
          type="button"
          disabled={saving}
          onClick={handleSaveSchema}
          className="mt-4 p-3.5 rounded-lg bg-neon-violet hover:bg-neon-violet/80 text-void-black font-extrabold text-sm glow-violet-hover transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
        >
          <Save className="w-4 h-4" /> SAVE SCHEMA CONFIG
        </button>
      </div>

      {/* Editor Details Section */}
      {editingFieldIdx !== null && schema[editingFieldIdx] && (
        <div className="flex-1 p-5 rounded-xl bg-panel-charcoal border border-panel-charcoal flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-panel-charcoal pb-3">
            <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
              <Settings className="w-4 h-4 text-neon-blue" /> Option Detail Editor
            </h3>
            <button
              type="button"
              onClick={() => setEditingFieldIdx(null)}
              className="text-text-muted hover:text-text-primary cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Form details */}
          <div className="flex flex-col gap-4">
            {/* Label input */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Display Label</label>
              <input
                type="text"
                value={schema[editingFieldIdx].label}
                onChange={(e) => handleFieldChange(editingFieldIdx!, "label", e.target.value)}
                className="p-2.5 rounded bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none focus:border-neon-violet/50"
              />
            </div>

            {/* Key input */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">System Identifier Key</label>
              <input
                type="text"
                value={schema[editingFieldIdx].key}
                onChange={(e) => handleFieldChange(editingFieldIdx!, "key", e.target.value)}
                className="p-2.5 rounded bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none focus:border-neon-violet/50"
              />
            </div>

            {/* Input Type */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Input Control Type</label>
              <select
                value={schema[editingFieldIdx].type}
                onChange={(e) => handleFieldChange(editingFieldIdx!, "type", e.target.value)}
                className="p-2.5 rounded bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none focus:border-neon-violet/50 cursor-pointer"
              >
                <option value="select">Dropdown Select</option>
                <option value="color_swatch">Color Swatch Circles</option>
                <option value="image_swatch">Image Thumbnail Swatches</option>
                <option value="toggle">Boolean Switch Toggler</option>
                <option value="slider">Numerical Range Slider</option>
                <option value="text_input">Text Field</option>
                <option value="number">Number Box</option>
              </select>
            </div>

            {/* Required and AI Preview toggles */}
            <div className="flex items-center gap-6 mt-1">
              <label className="flex items-center gap-2 text-xs font-bold text-text-primary cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={schema[editingFieldIdx].required}
                  onChange={(e) => handleFieldChange(editingFieldIdx!, "required", e.target.checked)}
                  className="accent-neon-violet"
                />
                Required Attribute
              </label>

              <label className="flex items-center gap-2 text-xs font-bold text-text-primary cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={schema[editingFieldIdx].affects_ai_preview}
                  onChange={(e) => handleFieldChange(editingFieldIdx!, "affects_ai_preview", e.target.checked)}
                  className="accent-neon-violet"
                />
                Affects AI Preview
              </label>
            </div>

            {/* Slider / Number settings */}
            {["slider", "number"].includes(schema[editingFieldIdx].type) && (
              <div className="grid grid-cols-3 gap-3 mt-1">
                <div className="flex flex-col gap-1">
                  <label className="text-[9px] text-text-muted font-bold">Min</label>
                  <input
                    type="number"
                    value={schema[editingFieldIdx].min ?? ""}
                    onChange={(e) => handleFieldChange(editingFieldIdx!, "min", e.target.value === "" ? null : parseFloat(e.target.value))}
                    className="p-2 rounded bg-void-black border border-panel-charcoal text-xs text-text-primary"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-[9px] text-text-muted font-bold">Max</label>
                  <input
                    type="number"
                    value={schema[editingFieldIdx].max ?? ""}
                    onChange={(e) => handleFieldChange(editingFieldIdx!, "max", e.target.value === "" ? null : parseFloat(e.target.value))}
                    className="p-2 rounded bg-void-black border border-panel-charcoal text-xs text-text-primary"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-[9px] text-text-muted font-bold">Step</label>
                  <input
                    type="number"
                    value={schema[editingFieldIdx].step ?? ""}
                    onChange={(e) => handleFieldChange(editingFieldIdx!, "step", e.target.value === "" ? null : parseFloat(e.target.value))}
                    className="p-2 rounded bg-void-black border border-panel-charcoal text-xs text-text-primary"
                  />
                </div>
              </div>
            )}

            {/* Select options builder */}
            {["select", "color_swatch", "image_swatch"].includes(schema[editingFieldIdx].type) && (
              <div className="flex flex-col gap-2 mt-2">
                <div className="flex items-center justify-between border-b border-panel-charcoal pb-1.5">
                  <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Swatches / Selection Options</label>
                  <button
                    type="button"
                    onClick={() => handleAddOption(editingFieldIdx!)}
                    className="text-[10px] font-bold text-neon-blue hover:text-text-primary cursor-pointer"
                  >
                    + Add Option Item
                  </button>
                </div>

                <div className="max-h-60 overflow-y-auto flex flex-col gap-3 pr-1">
                  {(schema[editingFieldIdx].options || []).map((opt, optIdx) => (
                    <div key={optIdx} className="p-3 rounded-lg bg-void-black/40 border border-panel-charcoal/50 flex flex-col gap-2 relative">
                      <button
                        type="button"
                        onClick={() => handleRemoveOption(editingFieldIdx!, optIdx)}
                        className="absolute top-2 right-2 text-neon-pink hover:text-text-primary text-[10px] font-bold cursor-pointer"
                        title="Remove Option Item"
                      >
                        Remove
                      </button>
                      
                      <div className="grid grid-cols-2 gap-2 pr-12">
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[9px] text-text-muted font-bold">Label</span>
                          <input
                            type="text"
                            value={opt.label}
                            onChange={(e) => handleOptionChange(editingFieldIdx!, optIdx, "label", e.target.value)}
                            className="p-1.5 rounded bg-void-black border border-panel-charcoal text-xs text-text-primary"
                            placeholder="e.g. Electric Blue"
                          />
                        </div>
                        
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[9px] text-text-muted font-bold">Value Key</span>
                          <input
                            type="text"
                            value={opt.value}
                            onChange={(e) => handleOptionChange(editingFieldIdx!, optIdx, "value", e.target.value)}
                            className="p-1.5 rounded bg-void-black border border-panel-charcoal text-xs text-text-primary"
                            placeholder="e.g. blue"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-2 mt-1">
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[9px] text-text-muted font-bold">Price Delta (₹)</span>
                          <input
                            type="number"
                            value={opt.price_delta || 0}
                            onChange={(e) => handleOptionChange(editingFieldIdx!, optIdx, "price_delta", parseFloat(e.target.value) || 0)}
                            className="p-1.5 rounded bg-void-black border border-panel-charcoal text-xs text-text-primary"
                          />
                        </div>
                        
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[9px] text-text-muted font-bold">Preview Image URL</span>
                          <input
                            type="text"
                            value={opt.preview_image || ""}
                            onChange={(e) => handleOptionChange(editingFieldIdx!, optIdx, "preview_image", e.target.value)}
                            className="p-1.5 rounded bg-void-black border border-panel-charcoal text-xs text-text-primary"
                            placeholder="Cloudinary URL"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
