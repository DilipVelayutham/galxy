/**
 * Smoke tests for lib/api/admin-site-content.ts
 *
 * Audit §5.3 recommendation: verify saveSectionContent's error-mapping
 * (success → { ok: true }, 400 → field errors with user input preserved,
 *  unexpected errors → thrown).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { saveSectionContent, fetchSectionContent } from './admin-site-content';

const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
});

describe('saveSectionContent', () => {
  const heroData = {
    headline: 'Test Headline',
    subheadline: '',
    background_video_url: null,
    background_image_url: 'https://example.com/image.jpg',
    cta_text: '',
    cta_link: '',
  };

  it('returns { ok: true } on 200', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ success: true, data: { section: 'hero', content: heroData } }),
    });

    const result = await saveSectionContent('hero', heroData);
    expect(result).toEqual({ ok: true });
    expect(mockFetch).toHaveBeenCalledWith('http://127.0.0.1:5000/api/admin/site-content/hero', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: heroData }),
    });
  });

  it('maps 400 field errors without throwing', async () => {
    const serverErrors = { title: 'Title is too short', cta_link: 'Must be a valid URL' };

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({
        success: false,
        message: 'Validation failed',
        errors: serverErrors,
      }),
    });

    const result = await saveSectionContent('hero', heroData);
    expect(result).toEqual({ ok: false, errors: serverErrors });
  });

  it('returns empty errors object when 400 response has no errors field', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({
        success: false,
        message: 'Bad request',
      }),
    });

    const result = await saveSectionContent('hero', heroData);
    expect(result).toEqual({ ok: false, errors: {} });
  });

  it('throws on unexpected status (500)', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      text: async () => 'Internal Server Error',
    });

    await expect(saveSectionContent('hero', heroData)).rejects.toThrow(
      /Unexpected error saving section hero: 500 — Internal Server Error/
    );
  });

  it('throws on network failure', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Failed to fetch'));

    await expect(saveSectionContent('hero', heroData)).rejects.toThrow('Failed to fetch');
  });
});

describe('fetchSectionContent', () => {
  it('returns content on successful GET', async () => {
    const content = { headline: 'Hero', subheadline: 'Welcome', background_video_url: null, background_image_url: 'https://example.com/image.jpg', cta_text: 'Go', cta_link: '/' };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: { section: 'hero', content },
      }),
    });

    const result = await fetchSectionContent('hero');
    expect(result).toEqual(content);
  });

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({
        success: false,
        message: 'Section not found',
        errors: {},
      }),
    });

    await expect(fetchSectionContent('hero')).rejects.toThrow('Section not found');
  });
});
