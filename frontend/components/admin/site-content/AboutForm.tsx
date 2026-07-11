'use client';

/**
 * components/admin/site-content/AboutForm.tsx
 *
 * Admin form for the about section.
 * Fields: title, body_text, images[] (multi-image via MediaUploadField),
 *         founder_photo (MediaUploadField), founder_name
 */

import React, { useEffect, useRef, useState } from 'react';
import type { AboutContent } from '@/lib/types/site-content';
import MediaUploadField from '@/components/admin/MediaUploadField';

interface AboutFormProps {
  initialData: AboutContent;
  onSave: (data: AboutContent) => Promise<void>;
  saving: boolean;
  fieldErrors: Record<string, string>;
  onDirtyChange?: (isDirty: boolean) => void;
}

export default function AboutForm({
  initialData,
  onSave,
  saving,
  fieldErrors,
  onDirtyChange,
}: AboutFormProps) {
  const [form, setForm] = useState<AboutContent>(initialData);
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});
  const initialRef = useRef(initialData);
  const onDirtyChangeRef = useRef(onDirtyChange);
  useEffect(() => { onDirtyChangeRef.current = onDirtyChange; }, [onDirtyChange]);

  useEffect(() => {
    const isDirty = JSON.stringify(form) !== JSON.stringify(initialRef.current);
    onDirtyChangeRef.current?.(isDirty);
  }, [form]);

  const set = <K extends keyof AboutContent>(key: K, value: AboutContent[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (localErrors[key]) setLocalErrors((prev) => { const n = { ...prev }; delete n[key]; return n; });
  };

  // Images array helpers
  const addImage = (url: string) =>
    setForm((prev) => ({ ...prev, images: [...prev.images, url] }));

  const removeImage = (idx: number) =>
    setForm((prev) => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== idx),
    }));

  const replaceImage = (idx: number, url: string) =>
    setForm((prev) => ({
      ...prev,
      images: prev.images.map((img, i) => (i === idx ? url : img)),
    }));

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.title.trim()) errs.title = 'Title is required.';
    if (!form.body_text.trim()) errs.body_text = 'Body text is required.';
    if (form.body_text.length > 5000) errs.body_text = 'Body text cannot exceed 5000 characters.';
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

  return (
    <form className="cms-form" onSubmit={handleSubmit} noValidate>
      <div className="form-grid">

        {/* Title */}
        <div className="field-group">
          <label className="field-label" htmlFor="about-title">
            Title <span className="required">*</span>
          </label>
          <input
            id="about-title"
            type="text"
            className={`field-input${err('title') ? ' field-input--error' : ''}`}
            value={form.title}
            onChange={(e) => set('title', e.target.value)}
            placeholder="e.g. Our Story"
          />
          {err('title') && <p className="field-error">{err('title')}</p>}
        </div>

        {/* Body Text */}
        <div className="field-group field-group--full">
          <label className="field-label" htmlFor="about-body">
            Body Text <span className="required">*</span>
          </label>
          <textarea
            id="about-body"
            className={`field-textarea${err('body_text') ? ' field-input--error' : ''}`}
            rows={6}
            value={form.body_text}
            onChange={(e) => set('body_text', e.target.value)}
            placeholder="About paragraph displayed on the About page"
          />
          {err('body_text') && <p className="field-error">{err('body_text')}</p>}
        </div>

        {/* Gallery Images */}
        <div className="field-group field-group--full">
          <div className="field-label">Gallery Images</div>
          <div className="image-gallery-editor">
            {form.images.map((imgUrl, idx) => (
              <div key={idx} className="gallery-image-item">
                <MediaUploadField
                  label={`Image ${idx + 1}`}
                  value={imgUrl}
                  folder="galxy/site-content"
                  onChange={(url) => replaceImage(idx, url)}
                  error={err(`images.${idx}`)}
                />
                <button
                  type="button"
                  className="btn btn-ghost btn-danger-text btn-sm"
                  onClick={() => removeImage(idx)}
                >
                  ✕ Remove
                </button>
              </div>
            ))}
            {/* Add new image slot */}
            <MediaUploadField
              label={`+ Add Image ${form.images.length + 1}`}
              value={null}
              folder="galxy/site-content"
              onChange={(url) => { if (url) addImage(url); }}
            />
          </div>
          {err('images') && <p className="field-error">{err('images')}</p>}
        </div>

        {/* Founder Photo */}
        <div className="field-group">
          <MediaUploadField
            label="Founder Photo"
            value={form.founder_photo}
            folder="galxy/site-content"
            onChange={(url) => set('founder_photo', url || null)}
            error={err('founder_photo')}
          />
        </div>

        {/* Founder Name */}
        <div className="field-group">
          <label className="field-label" htmlFor="about-founder-name">
            Founder Name <span className="required">*</span>
          </label>
          <input
            id="about-founder-name"
            type="text"
            className={`field-input${err('founder_name') ? ' field-input--error' : ''}`}
            value={form.founder_name}
            onChange={(e) => set('founder_name', e.target.value)}
            placeholder="e.g. Asil"
          />
          {err('founder_name') && <p className="field-error">{err('founder_name')}</p>}
        </div>

      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? <span className="btn-spinner" aria-label="Saving…" /> : null}
          {saving ? 'Saving…' : 'Save About Section'}
        </button>
      </div>
    </form>
  );
}
