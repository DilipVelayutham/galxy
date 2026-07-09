'use client';

/**
 * components/admin/site-content/FooterForm.tsx
 *
 * Admin form for the footer section.
 * Fields: tagline, quick_links[] (dynamic add/remove/reorder), business_hours
 */

import React, { useEffect, useRef, useState } from 'react';
import type { FooterContent } from '@/lib/types/site-content';

interface QuickLink {
  label: string;
  url: string;
}

// ─── Quick-link row component ────────────────────────────────────────────────
interface LinkRowProps {
  idx: number;
  total: number;
  link: QuickLink;
  fieldErrors: Record<string, string>;
  localErrors: Record<string, string>;
  onUpdate: (idx: number, field: keyof QuickLink, value: string) => void;
  onRemove: (idx: number) => void;
  onMove: (idx: number, dir: 'up' | 'down') => void;
}

function LinkRow({
  idx,
  total,
  link,
  fieldErrors,
  localErrors,
  onUpdate,
  onRemove,
  onMove,
}: LinkRowProps) {
  return (
    <div
      className="quick-link-row"
      role="listitem"
      aria-label={`Quick link ${idx + 1}`}
      style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}
    >
      <div style={{ display: 'flex', gap: '4px' }}>
        <button
          type="button"
          className="btn btn-secondary"
          disabled={idx === 0}
          onClick={() => onMove(idx, 'up')}
          aria-label="Move link up"
          title="Move link up"
          style={{ padding: '2px 6px', fontSize: '11px', height: '26px' }}
        >
          ▲
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          disabled={idx === total - 1}
          onClick={() => onMove(idx, 'down')}
          aria-label="Move link down"
          title="Move link down"
          style={{ padding: '2px 6px', fontSize: '11px', height: '26px' }}
        >
          ▼
        </button>
      </div>

      <input
        type="text"
        className={`field-input field-input--sm${(fieldErrors[`quick_links.${idx}.label`] || localErrors[`quick_links.${idx}.label`]) ? ' field-input--error' : ''}`}
        value={link.label}
        onChange={(e) => onUpdate(idx, 'label', e.target.value)}
        placeholder="Label (e.g. Portfolio)"
        aria-label={`Quick link ${idx + 1} label`}
        style={{ flex: 1 }}
      />

      <input
        type="text"
        className={`field-input field-input--sm${(fieldErrors[`quick_links.${idx}.url`] || localErrors[`quick_links.${idx}.url`]) ? ' field-input--error' : ''}`}
        value={link.url}
        onChange={(e) => onUpdate(idx, 'url', e.target.value)}
        placeholder="URL (e.g. https://...)"
        aria-label={`Quick link ${idx + 1} URL`}
        style={{ flex: 2 }}
      />

      <button
        type="button"
        className="btn btn-ghost btn-danger-text btn-icon"
        onClick={() => onRemove(idx)}
        aria-label={`Remove quick link ${idx + 1}`}
      >
        ✕
      </button>
    </div>
  );
}

// ─── FooterForm ───────────────────────────────────────────────────────────────
interface FooterFormProps {
  initialData: FooterContent;
  onSave: (data: FooterContent) => Promise<void>;
  saving: boolean;
  fieldErrors: Record<string, string>;
  onDirtyChange?: (isDirty: boolean) => void;
}

export default function FooterForm({
  initialData,
  onSave,
  saving,
  fieldErrors,
  onDirtyChange,
}: FooterFormProps) {
  const [form, setForm] = useState<FooterContent>(initialData);
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});
  const initialRef = useRef(initialData);
  const onDirtyChangeRef = useRef(onDirtyChange);
  useEffect(() => { onDirtyChangeRef.current = onDirtyChange; }, [onDirtyChange]);

  useEffect(() => {
    const isDirty = JSON.stringify(form) !== JSON.stringify(initialRef.current);
    onDirtyChangeRef.current?.(isDirty);
  }, [form]);

  const set = <K extends keyof FooterContent>(key: K, value: FooterContent[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (localErrors[key]) setLocalErrors((prev) => { const n = { ...prev }; delete n[key]; return n; });
  };

  // ── Quick-links helpers ────────────────────────────────────────────────────
  const addLink = () => {
    setForm((prev) => ({
      ...prev,
      quick_links: [...prev.quick_links, { label: '', url: '' }],
    }));
  };

  const removeLink = (idx: number) => {
    setForm((prev) => ({
      ...prev,
      quick_links: prev.quick_links.filter((_, i) => i !== idx),
    }));
  };

  const updateLink = (idx: number, field: keyof QuickLink, value: string) => {
    setForm((prev) => ({
      ...prev,
      quick_links: prev.quick_links.map((link, i) =>
        i === idx ? { ...link, [field]: value } : link
      ),
    }));
  };

  const moveLink = (idx: number, dir: 'up' | 'down') => {
    const targetIdx = dir === 'up' ? idx - 1 : idx + 1;
    if (targetIdx < 0 || targetIdx >= form.quick_links.length) return;

    setForm((prev) => {
      const list = [...prev.quick_links];
      const temp = list[idx];
      list[idx] = list[targetIdx];
      list[targetIdx] = temp;
      return { ...prev, quick_links: list };
    });
  };

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.tagline.trim()) errs.tagline = 'Tagline is required.';
    if (!form.business_hours.trim()) errs.business_hours = 'Business hours are required.';
    form.quick_links.forEach((link, i) => {
      if (!link.label.trim()) {
        errs[`quick_links.${i}.label`] = 'Label is required.';
      }
      if (!link.url.trim()) {
        errs[`quick_links.${i}.url`] = 'URL is required.';
      } else if (!/^(https?:\/\/)/.test(link.url)) {
        errs[`quick_links.${i}.url`] = 'Enter a valid URL (https://...).';
      }
    });
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

        {/* Tagline */}
        <div className="field-group">
          <label className="field-label" htmlFor="footer-tagline">
            Tagline <span className="required">*</span>
          </label>
          <input
            id="footer-tagline"
            type="text"
            className={`field-input${err('tagline') ? ' field-input--error' : ''}`}
            value={form.tagline}
            onChange={(e) => set('tagline', e.target.value)}
            placeholder="e.g. Illuminating spaces, crafting memories."
          />
          {err('tagline') && <p className="field-error">{err('tagline')}</p>}
        </div>

        {/* Business Hours */}
        <div className="field-group">
          <label className="field-label" htmlFor="footer-hours">
            Business Hours <span className="required">*</span>
          </label>
          <textarea
            id="footer-hours"
            className={`field-textarea${err('business_hours') ? ' field-input--error' : ''}`}
            rows={4}
            value={form.business_hours}
            onChange={(e) => set('business_hours', e.target.value)}
            placeholder={`Mon – Fri: 9am – 6pm\nSat: 10am – 4pm\nSun: Closed`}
          />
          {err('business_hours') && (
            <p className="field-error">{err('business_hours')}</p>
          )}
        </div>

        {/* Quick Links */}
        <div className="field-group field-group--full">
          <div className="field-label">
            Quick Links
            <span className="field-hint">(use arrows to reorder)</span>
          </div>

          <div className="quick-links-list" role="list">
            {form.quick_links.map((link, idx) => (
              <LinkRow
                key={idx}
                idx={idx}
                total={form.quick_links.length}
                link={link}
                fieldErrors={fieldErrors}
                localErrors={localErrors}
                onUpdate={updateLink}
                onRemove={removeLink}
                onMove={moveLink}
              />
            ))}
          </div>

          {err('quick_links') && (
            <p className="field-error">{err('quick_links')}</p>
          )}

          <button type="button" className="btn btn-secondary btn-sm" onClick={addLink}>
            + Add Quick Link
          </button>
        </div>

      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? <span className="btn-spinner" aria-label="Saving…" /> : null}
          {saving ? 'Saving…' : 'Save Footer Section'}
        </button>
      </div>
    </form>
  );
}
