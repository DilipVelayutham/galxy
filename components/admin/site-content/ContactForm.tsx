'use client';

/**
 * components/admin/site-content/ContactForm.tsx
 *
 * Admin form for the contact section.
 * Fields: email, phone, address, map_embed_url, whatsapp_number
 */

import React, { useEffect, useRef, useState } from 'react';
import type { ContactContent } from '@/lib/types/site-content';

interface ContactFormProps {
  initialData: ContactContent;
  onSave: (data: ContactContent) => Promise<void>;
  saving: boolean;
  fieldErrors: Record<string, string>;
  onDirtyChange?: (isDirty: boolean) => void;
}

export default function ContactForm({
  initialData,
  onSave,
  saving,
  fieldErrors,
  onDirtyChange,
}: ContactFormProps) {
  const [form, setForm] = useState<ContactContent>(initialData);
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});
  const initialRef = useRef(initialData);
  const onDirtyChangeRef = useRef(onDirtyChange);
  useEffect(() => { onDirtyChangeRef.current = onDirtyChange; }, [onDirtyChange]);

  useEffect(() => {
    const isDirty = JSON.stringify(form) !== JSON.stringify(initialRef.current);
    onDirtyChangeRef.current?.(isDirty);
  }, [form]);

  const set = <K extends keyof ContactContent>(key: K, value: ContactContent[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (localErrors[key]) setLocalErrors((prev) => { const n = { ...prev }; delete n[key]; return n; });
  };

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.email.trim()) errs.email = 'Email is required.';
    if (!form.phone.trim()) errs.phone = 'Phone number is required.';
    if (!form.whatsapp_number.trim()) errs.whatsapp_number = 'WhatsApp number is required.';
    if (!form.address.trim()) errs.address = 'Address is required.';
    if (form.map_embed_url && !/^(https?:\/\/)/.test(form.map_embed_url)) errs.map_embed_url = 'Enter a valid URL (https://...).';
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

        {/* Email */}
        <div className="field-group">
          <label className="field-label" htmlFor="contact-email">
            Email Address <span className="required">*</span>
          </label>
          <input
            id="contact-email"
            type="email"
            className={`field-input${err('email') ? ' field-input--error' : ''}`}
            value={form.email}
            onChange={(e) => set('email', e.target.value)}
            placeholder="e.g. hello@galxy.studio"
          />
          {err('email') && <p className="field-error">{err('email')}</p>}
        </div>

        {/* Phone */}
        <div className="field-group">
          <label className="field-label" htmlFor="contact-phone">
            Phone Number <span className="required">*</span>
          </label>
          <input
            id="contact-phone"
            type="tel"
            className={`field-input${err('phone') ? ' field-input--error' : ''}`}
            value={form.phone}
            onChange={(e) => set('phone', e.target.value)}
            placeholder="e.g. +91 98765 43210"
          />
          {err('phone') && <p className="field-error">{err('phone')}</p>}
        </div>

        {/* WhatsApp Number */}
        <div className="field-group">
          <label className="field-label" htmlFor="contact-whatsapp">
            WhatsApp Number <span className="required">*</span>
          </label>
          <input
            id="contact-whatsapp"
            type="tel"
            className={`field-input${err('whatsapp_number') ? ' field-input--error' : ''}`}
            value={form.whatsapp_number}
            onChange={(e) => set('whatsapp_number', e.target.value)}
            placeholder="e.g. +91 98765 43210"
          />
          {err('whatsapp_number') && <p className="field-error">{err('whatsapp_number')}</p>}
        </div>

        {/* Address */}
        <div className="field-group field-group--full">
          <label className="field-label" htmlFor="contact-address">
            Physical Address <span className="required">*</span>
          </label>
          <textarea
            id="contact-address"
            className={`field-textarea${err('address') ? ' field-input--error' : ''}`}
            rows={3}
            value={form.address}
            onChange={(e) => set('address', e.target.value)}
            placeholder="e.g. 12 Light District, Chennai, Tamil Nadu 600001"
          />
          {err('address') && <p className="field-error">{err('address')}</p>}
        </div>

        {/* Map Embed URL */}
        <div className="field-group field-group--full">
          <label className="field-label" htmlFor="contact-map">
            Google Maps Embed URL
          </label>
          <input
            id="contact-map"
            type="url"
            className={`field-input${err('map_embed_url') ? ' field-input--error' : ''}`}
            value={form.map_embed_url || ''}
            onChange={(e) => set('map_embed_url', e.target.value || null)}
            placeholder="https://www.google.com/maps/embed?pb=…"
          />
          {err('map_embed_url') && (
            <p className="field-error">{err('map_embed_url')}</p>
          )}
          {form.map_embed_url && (
            <div className="map-preview">
              <iframe
                src={form.map_embed_url}
                width="100%"
                height="200"
                style={{ border: 0, borderRadius: 8 }}
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                title="Map preview"
              />
            </div>
          )}
        </div>

      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? <span className="btn-spinner" aria-label="Saving…" /> : null}
          {saving ? 'Saving…' : 'Save Contact Section'}
        </button>
      </div>
    </form>
  );
}
