'use client';

/**
 * components/admin/site-content/SeoHomeForm.tsx
 *
 * Admin form for the seo_home section.
 * Fields: meta_title, meta_description, og_image (via MediaUploadField)
 */

import React, { useEffect, useRef, useState } from 'react';
import type { SeoHomeContent } from '@/lib/types/site-content';
import MediaUploadField from '@/components/admin/MediaUploadField';

interface SeoHomeFormProps {
  initialData: SeoHomeContent;
  onSave: (data: SeoHomeContent) => Promise<void>;
  saving: boolean;
  fieldErrors: Record<string, string>;
  onDirtyChange?: (isDirty: boolean) => void;
}

export default function SeoHomeForm({
  initialData,
  onSave,
  saving,
  fieldErrors,
  onDirtyChange,
}: SeoHomeFormProps) {
  const [form, setForm] = useState<SeoHomeContent>(initialData);
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});
  const initialRef = useRef(initialData);
  const onDirtyChangeRef = useRef(onDirtyChange);
  useEffect(() => { onDirtyChangeRef.current = onDirtyChange; }, [onDirtyChange]);

  useEffect(() => {
    const isDirty = JSON.stringify(form) !== JSON.stringify(initialRef.current);
    onDirtyChangeRef.current?.(isDirty);
  }, [form]);

  const set = <K extends keyof SeoHomeContent>(key: K, value: SeoHomeContent[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (localErrors[key]) setLocalErrors((prev) => { const n = { ...prev }; delete n[key]; return n; });
  };

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.meta_title.trim()) errs.meta_title = 'Meta title is required.';
    if (!form.meta_description.trim()) errs.meta_description = 'Meta description is required.';
    setLocalErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    await onSave(form);
    initialRef.current = form;
    onDirtyChange?.(false);
  };

  const err = (key: string) => localErrors[key] || fieldErrors[key];

  // Character count helpers
  const titleLen = form.meta_title.length;
  const descLen = form.meta_description.length;

  return (
    <form className="cms-form" onSubmit={handleSubmit} noValidate>
      <div className="form-grid">

        {/* Meta Title */}
        <div className="field-group field-group--full">
          <label className="field-label" htmlFor="seo-title">
            Page Title (meta title) <span className="required">*</span>
          </label>
          <input
            id="seo-title"
            type="text"
            className={`field-input${err('meta_title') ? ' field-input--error' : ''}`}
            value={form.meta_title}
            onChange={(e) => set('meta_title', e.target.value)}
            placeholder="e.g. GALXY | Custom Lighting & Craft Studio"
            maxLength={70}
          />
          <p className={`char-count${titleLen > 60 ? ' char-count--warn' : ''}`}>
            {titleLen}/70 characters {titleLen > 60 ? '⚠ Google typically shows ≤60' : ''}
          </p>
          {err('meta_title') && <p className="field-error">{err('meta_title')}</p>}
        </div>

        {/* Meta Description */}
        <div className="field-group field-group--full">
          <label className="field-label" htmlFor="seo-description">
            Meta Description <span className="required">*</span>
          </label>
          <textarea
            id="seo-description"
            className={`field-textarea${err('meta_description') ? ' field-input--error' : ''}`}
            rows={3}
            value={form.meta_description}
            onChange={(e) => set('meta_description', e.target.value)}
            placeholder="Short description used by search engines (≤160 chars recommended)"
            maxLength={200}
          />
          <p className={`char-count${descLen > 160 ? ' char-count--warn' : ''}`}>
            {descLen}/200 characters {descLen > 160 ? '⚠ Google typically shows ≤160' : ''}
          </p>
          {err('meta_description') && <p className="field-error">{err('meta_description')}</p>}
        </div>

        {/* OG Image */}
        <div className="field-group field-group--full">
          <MediaUploadField
            label="Open Graph Image (og:image)"
            value={form.og_image}
            folder="galxy/site-content"
            onChange={(url) => set('og_image', url || null)}
            error={err('og_image')}
          />
          <p className="field-hint">Recommended: 1200×630px JPG/PNG for social sharing previews.</p>
        </div>

      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? <span className="btn-spinner" aria-label="Saving…" /> : null}
          {saving ? 'Saving…' : 'Save SEO Settings'}
        </button>
      </div>
    </form>
  );
}
