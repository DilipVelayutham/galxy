/**
 * lib/api/admin-site-content.ts
 *
 * Fetch wrapper for Flask admin routes:
 *   GET  /api/admin/site-content/:section
 *   PUT  /api/admin/site-content/:section  → body: { content: {...} }
 *
 * Response envelope:
 *   GET  → { success: true, data: { section, content } }
 *   PUT  → 200 OK or 400 { success: false, message, errors }
 */

import type {
  SectionName,
  SectionContent,
  SiteContentResponse,
  SiteContentErrorResponse,
} from '@/lib/types/site-content';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';

// ─── GET ─────────────────────────────────────────────────────────────────────

export async function fetchSectionContent<T extends SectionContent>(
  section: SectionName
): Promise<T> {
  const res = await fetch(`${BASE_URL}/api/admin/site-content/${section}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    cache: 'no-store',
  });

  if (!res.ok) {
    const err: SiteContentErrorResponse = await res.json();
    throw new Error(err.message ?? `Failed to fetch section: ${section}`);
  }

  const json: SiteContentResponse<T> = await res.json();
  return json.data.content;
}

// ─── PUT ─────────────────────────────────────────────────────────────────────

export type SaveResult =
  | { ok: true }
  | { ok: false; errors: Record<string, string> };

/**
 * Always sends the FULL content object (never a partial patch).
 * Maps 400 field errors back to the caller so the form can display them inline.
 */
export async function saveSectionContent<T extends SectionContent>(
  section: SectionName,
  content: T
): Promise<SaveResult> {
  const res = await fetch(`${BASE_URL}/api/admin/site-content/${section}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });

  if (res.ok) {
    return { ok: true };
  }

  if (res.status === 400) {
    const err: SiteContentErrorResponse = await res.json();
    return { ok: false, errors: err.errors ?? {} };
  }

  // Unexpected error
  const text = await res.text();
  throw new Error(`Unexpected error saving section ${section}: ${res.status} — ${text}`);
}
