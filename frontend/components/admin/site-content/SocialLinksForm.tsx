'use client';

/**
 * components/admin/site-content/SocialLinksForm.tsx
 *
 * Admin form for the social_links section.
 * Fields: instagram, facebook, youtube (all URL strings, instagram required, facebook and youtube optional)
 */

import React, { useEffect, useRef, useState } from 'react';
import type { SocialLinksContent } from '@/lib/types/site-content';

interface SocialLinksFormProps {
  initialData: SocialLinksContent;
  onSave: (data: SocialLinksContent) => Promise<void>;
  saving: boolean;
  fieldErrors: Record<string, string>;
  onDirtyChange?: (isDirty: boolean) => void;
}

const SOCIAL_FIELDS: {
  key: keyof SocialLinksContent;
  label: string;
  placeholder: string;
  icon: string;
  required: boolean;
}[] = [
  {
    key: 'instagram',
    label: 'Instagram',
    placeholder: 'https://instagram.com/galxy.studio',
    icon: '📷',
    required: true,
  },
  {
    key: 'facebook',
    label: 'Facebook',
    placeholder: 'https://facebook.com/galxystudio',
    icon: '📘',
    required: false,
  },
  {
    key: 'youtube',
    label: 'YouTube',
    placeholder: 'https://youtube.com/@galxy',
    icon: '▶️',
    required: false,
  },
];

export default function SocialLinksForm({
  initialData,
  onSave,
  saving,
  fieldErrors,
  onDirtyChange,
}: SocialLinksFormProps) {
  const [form, setForm] = useState<SocialLinksContent>(initialData);
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});
  const initialRef = useRef(initialData);
  const onDirtyChangeRef = useRef(onDirtyChange);
  useEffect(() => { onDirtyChangeRef.current = onDirtyChange; }, [onDirtyChange]);

  useEffect(() => {
    const isDirty = JSON.stringify(form) !== JSON.stringify(initialRef.current);
    onDirtyChangeRef.current?.(isDirty);
  }, [form]);

  const set = (key: keyof SocialLinksContent, value: string | null) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (localErrors[key]) setLocalErrors((prev) => { const n = { ...prev }; delete n[key]; return n; });
  };

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.instagram.trim()) {
      errs.instagram = 'Instagram URL is required.';
    }
    for (const { key, label, required } of SOCIAL_FIELDS) {
      const val = form[key];
      if (required && (!val || !val.trim())) {
        errs[key] = `${label} URL is required.`;
      } else if (val && !/^(https?:\/\/)/.test(val)) {
        errs[key] = `${label} URL must start with https://`;
      }
    }
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
        {SOCIAL_FIELDS.map(({ key, label, placeholder, icon, required }) => (
          <div className="field-group" key={key}>
            <label className="field-label" htmlFor={`social-${key}`}>
              <span className="social-icon" aria-hidden="true">{icon}</span>
              {label} {required && <span className="required">*</span>}
            </label>
            <input
              id={`social-${key}`}
              type="url"
              className={`field-input${err(key) ? ' field-input--error' : ''}`}
              value={form[key] || ''}
              onChange={(e) => set(key, e.target.value || null)}
              placeholder={placeholder}
            />
            {err(key) && <p className="field-error">{err(key)}</p>}
            {form[key] && !err(key) && (
              <a
                href={form[key]!}
                target="_blank"
                rel="noopener noreferrer"
                className="field-link-preview"
              >
                ↗ Preview link
              </a>
            )}
          </div>
        ))}
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? <span className="btn-spinner" aria-label="Saving…" /> : null}
          {saving ? 'Saving…' : 'Save Social Links'}
        </button>
      </div>
    </form>
  );
}
