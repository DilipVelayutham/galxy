'use client';

/**
 * components/admin/site-content/HeroForm.tsx
 *
 * Admin form for the hero section.
 * Fields: headline, subheadline, cta_text, cta_link, background_image_url, background_video_url
 */

import React, { useEffect, useRef, useState } from 'react';
import type { HeroContent } from '@/lib/types/site-content';
import MediaUploadField from '@/components/admin/MediaUploadField';

interface HeroFormProps {
  initialData: HeroContent;
  onSave: (data: HeroContent) => Promise<void>;
  saving: boolean;
  fieldErrors: Record<string, string>;
  onDirtyChange?: (isDirty: boolean) => void;
}

export default function HeroForm({
  initialData,
  onSave,
  saving,
  fieldErrors,
  onDirtyChange,
}: HeroFormProps) {
  const [form, setForm] = useState<HeroContent>(initialData);
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});
  const initialRef = useRef(initialData);
  const onDirtyChangeRef = useRef(onDirtyChange);
  useEffect(() => { onDirtyChangeRef.current = onDirtyChange; }, [onDirtyChange]);

  useEffect(() => {
    const isDirty = JSON.stringify(form) !== JSON.stringify(initialRef.current);
    onDirtyChangeRef.current?.(isDirty);
  }, [form]);

  const set = <K extends keyof HeroContent>(key: K, value: HeroContent[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (localErrors[key]) setLocalErrors((prev) => { const n = { ...prev }; delete n[key]; return n; });
  };

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.headline.trim()) errs.headline = 'Headline is required.';
    if (!form.background_image_url.trim()) errs.background_image_url = 'Background image is required.';
    if (form.cta_link && !/^(https?:\/\/|\/)/.test(form.cta_link)) errs.cta_link = 'Enter a valid URL (e.g. https://... or /path).';
    if (form.background_video_url && !/^(https?:\/\/)/.test(form.background_video_url)) errs.background_video_url = 'Enter a valid absolute video URL (e.g. https://...).';
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

        {/* Headline */}
        <div className="field-group">
          <label className="field-label" htmlFor="hero-headline">
            Hero Headline <span className="required">*</span>
          </label>
          <input
            id="hero-headline"
            type="text"
            className={`field-input${err('headline') ? ' field-input--error' : ''}`}
            value={form.headline}
            onChange={(e) => set('headline', e.target.value)}
            placeholder="e.g. Custom Lighting & Craft Studio"
          />
          {err('headline') && <p className="field-error">{err('headline')}</p>}
        </div>

        {/* Subheadline */}
        <div className="field-group">
          <label className="field-label" htmlFor="hero-subheadline">
            Subheadline <span className="required">*</span>
          </label>
          <textarea
            id="hero-subheadline"
            className={`field-textarea${err('subheadline') ? ' field-input--error' : ''}`}
            rows={3}
            value={form.subheadline}
            onChange={(e) => set('subheadline', e.target.value)}
            placeholder="Short tagline shown below the hero title"
          />
          {err('subheadline') && <p className="field-error">{err('subheadline')}</p>}
        </div>

        {/* CTA Text */}
        <div className="field-group">
          <label className="field-label" htmlFor="hero-cta-text">
            CTA Button Text <span className="required">*</span>
          </label>
          <input
            id="hero-cta-text"
            type="text"
            className={`field-input${err('cta_text') ? ' field-input--error' : ''}`}
            value={form.cta_text}
            onChange={(e) => set('cta_text', e.target.value)}
            placeholder="e.g. Explore Our Work"
          />
          {err('cta_text') && <p className="field-error">{err('cta_text')}</p>}
        </div>

        {/* CTA Link */}
        <div className="field-group">
          <label className="field-label" htmlFor="hero-cta-link">
            CTA Button Link <span className="required">*</span>
          </label>
          <input
            id="hero-cta-link"
            type="url"
            className={`field-input${err('cta_link') ? ' field-input--error' : ''}`}
            value={form.cta_link}
            onChange={(e) => set('cta_link', e.target.value)}
            placeholder="e.g. /portfolio"
          />
          {err('cta_link') && <p className="field-error">{err('cta_link')}</p>}
        </div>

        {/* Background Image */}
        <div className="field-group field-group--full">
          <MediaUploadField
            label="Hero Background Image"
            value={form.background_image_url}
            folder="galxy/site-content"
            onChange={(url) => set('background_image_url', url || '')}
            error={err('background_image_url')}
          />
        </div>

        {/* Background Video URL */}
        <div className="field-group field-group--full">
          <label className="field-label" htmlFor="hero-video-url">
            Background Video URL (Optional)
          </label>
          <input
            id="hero-video-url"
            type="url"
            className={`field-input${err('background_video_url') ? ' field-input--error' : ''}`}
            value={form.background_video_url || ''}
            onChange={(e) => set('background_video_url', e.target.value || null)}
            placeholder="e.g. https://res.cloudinary.com/...mp4"
          />
          {err('background_video_url') && <p className="field-error">{err('background_video_url')}</p>}
        </div>

      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? <span className="btn-spinner" aria-label="Saving…" /> : null}
          {saving ? 'Saving…' : 'Save Hero Section'}
        </button>
      </div>
    </form>
  );
}
