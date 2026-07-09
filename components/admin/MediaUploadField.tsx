'use client';

/**
 * components/admin/MediaUploadField.tsx
 *
 * Shared image-picker used by HeroForm (background_image),
 * AboutForm (images[], founder_photo), and SeoHomeForm (og_image).
 *
 * Calls the media upload endpoint:
 *   POST /api/admin/media/upload
 *   multipart/form-data: { file, folder: "galxy/site-content" }
 *   200 → { data: { url: string } }
 *   400/413 → show inline error, preserve existing value.
 *
 * Auth headers are attached by Module 12's shared fetch wrapper
 * (admin_session cookie is forwarded automatically by the browser).
 */

import React, { useRef, useState } from 'react';

interface MediaUploadFieldProps {
  label: string;
  value: string | null;
  folder?: string;
  onChange: (url: string) => void;
  error?: string;
}

export default function MediaUploadField({
  label,
  value,
  folder = 'galxy/site-content',
  onChange,
  error,
}: MediaUploadFieldProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('folder', folder);

      const res = await fetch('/api/admin/media/upload', {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const json = await res.json();
        onChange(json.data.url);
      } else if (res.status === 413) {
        setUploadError('File too large. Please choose a smaller image.');
      } else if (res.status === 400) {
        const json = await res.json();
        setUploadError(json.message ?? 'Invalid file. Upload rejected.');
      } else if (res.status === 401) {
        setUploadError('Session expired. Please log in again.');
      } else {
        setUploadError('Upload failed. Please try again.');
      }
    } catch {
      setUploadError('Network error. Could not reach upload service.');
    } finally {
      setUploading(false);
      // Reset file input so same file can be re-selected after an error
      if (inputRef.current) inputRef.current.value = '';
    }
  };

  return (
    <div className="media-upload-field">
      <label className="field-label">{label}</label>

      {/* Current image preview */}
      {value && (
        <div className="media-preview">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={value} alt={`${label} preview`} className="media-preview-img" />
          <span className="media-preview-url" title={value}>
            {value.length > 50 ? `…${value.slice(-45)}` : value}
          </span>
        </div>
      )}

      {/* Upload trigger */}
      <div className="media-upload-controls">
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? (
            <span className="btn-spinner" aria-label="Uploading…" />
          ) : (
            value ? '⇄ Replace Image' : '↑ Upload Image'
          )}
        </button>

        {value && !uploading && (
          <button
            type="button"
            className="btn btn-ghost btn-danger-text"
            onClick={() => onChange('')}
          >
            ✕ Remove
          </button>
        )}

        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
      </div>

      {/* Inline errors — upload errors take priority over form validation errors */}
      {(uploadError || error) && (
        <p className="field-error" role="alert">
          {uploadError ?? error}
        </p>
      )}
    </div>
  );
}
