'use client';

/**
 * app/(admin)/site-content/page.tsx
 *
 * Admin CMS Panel — /admin/site-content
 * Tab/nav shell across all 6 site-content sections.
 * Fetches section data on first tab visit (GET), saves via PUT.
 * Maps 400 field errors inline. Shows toast for success/error.
 *
 * Fix 3: Moved from (admin)/admin/site-content/ → (admin)/site-content/
 *         to eliminate the double-admin routing bug.
 * Fix 5: Dirty-state tracking per tab + confirmation dialog before switching
 *         away from an unsaved tab.
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import type {
  SectionName,
  HeroContent,
  AboutContent,
  FooterContent,
  ContactContent,
  SeoHomeContent,
  SocialLinksContent,
  SectionContent,
} from '@/lib/types/site-content';
import { fetchSectionContent, saveSectionContent } from '@/lib/api/admin-site-content';

import HeroForm from '@/components/admin/site-content/HeroForm';
import AboutForm from '@/components/admin/site-content/AboutForm';
import FooterForm from '@/components/admin/site-content/FooterForm';
import ContactForm from '@/components/admin/site-content/ContactForm';
import SeoHomeForm from '@/components/admin/site-content/SeoHomeForm';
import SocialLinksForm from '@/components/admin/site-content/SocialLinksForm';

import './admin-cms.css';

// ─── Tab configuration ───────────────────────────────────────────────────────
const TABS: { key: SectionName; label: string; icon: string }[] = [
  { key: 'hero',         label: 'Hero',         icon: '🌟' },
  { key: 'about',        label: 'About',        icon: '👤' },
  { key: 'footer',       label: 'Footer',       icon: '🔗' },
  { key: 'contact',      label: 'Contact',      icon: '📬' },
  { key: 'seo_home',     label: 'SEO',          icon: '🔍' },
  { key: 'social_links', label: 'Social Links', icon: '📱' },
];

// ─── Default empty states (used while loading / for new sections) ─────────────
const DEFAULTS: Record<SectionName, SectionContent> = {
  hero:         { headline: '', subheadline: '', background_video_url: null, background_image_url: '', cta_text: '', cta_link: '' },
  about:        { title: '', body_text: '', images: [], founder_photo: null, founder_name: '' },
  footer:       { tagline: '', quick_links: [], business_hours: '' },
  contact:      { phone: '', whatsapp_number: '', email: '', address: '', map_embed_url: null },
  seo_home:     { meta_title: '', meta_description: '', og_image: null },
  social_links: { instagram: '', facebook: null, youtube: null },
};

// ─── Toast ───────────────────────────────────────────────────────────────────
type ToastType = 'success' | 'error' | 'info';
interface Toast { id: number; type: ToastType; message: string }
let toastCounter = 0;

// ─── Page component ──────────────────────────────────────────────────────────
export default function SiteContentPage() {
  const [activeTab, setActiveTab] = useState<SectionName>('hero');
  const [sectionData, setSectionData] = useState<Partial<Record<SectionName, SectionContent>>>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Fix 5: Track dirty state per tab (true = has unsaved changes)
  const [dirtyTabs, setDirtyTabs] = useState<Partial<Record<SectionName, boolean>>>({});

  // Ref so the confirm dialog can read the latest dirty state without
  // being captured in a stale closure
  const dirtyTabsRef = useRef(dirtyTabs);
  useEffect(() => { dirtyTabsRef.current = dirtyTabs; }, [dirtyTabs]);

  // ── Toast helpers ──────────────────────────────────────────────────────────
  const addToast = useCallback((type: ToastType, message: string) => {
    const id = ++toastCounter;
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  // ── Fetch section data on first tab visit ─────────────────────────────────
  // Fix 5: Do NOT reset form state after a GET — only populate if not already loaded.
  useEffect(() => {
    if (sectionData[activeTab]) return; // already fetched — preserve form state

    let cancelled = false;

    (async () => {
      setLoading(true);
      setFieldErrors({});

      try {
        const data = await fetchSectionContent(activeTab);
        if (!cancelled) setSectionData((prev) => ({ ...prev, [activeTab]: data }));
      } catch (err: unknown) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Unknown error';
          addToast('error', `Failed to load ${activeTab}: ${message}`);
          // Fall back to empty defaults so the form still renders
          setSectionData((prev) => ({ ...prev, [activeTab]: DEFAULTS[activeTab] }));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => { cancelled = true; };
  }, [activeTab, sectionData, addToast]);

  // ── Dirty-state handler ───────────────────────────────────────────────────
  const handleDirtyChange = useCallback((tab: SectionName, isDirty: boolean) => {
    setDirtyTabs((prev) => ({ ...prev, [tab]: isDirty }));
  }, []);

  // ── Save handler ──────────────────────────────────────────────────────────
  const handleSave = useCallback(
    async (data: SectionContent) => {
      setSaving(true);
      setFieldErrors({});

      const result = await saveSectionContent(activeTab, data).catch((err: Error) => {
        addToast('error', `Save failed: ${err.message}`);
        return null;
      });

      if (!result) { setSaving(false); return; }

      if (result.ok) {
        // Update cache so re-switching tab doesn't refetch stale data
        setSectionData((prev) => ({ ...prev, [activeTab]: data }));
        // Fix 5: Mark tab as clean after successful save
        setDirtyTabs((prev) => ({ ...prev, [activeTab]: false }));
        addToast('success', `${TABS.find((t) => t.key === activeTab)?.label} section saved!`);
      } else {
        // 400: map field errors inline — do NOT reset form state, preserve user's input
        setFieldErrors(result.errors);
        addToast('error', 'Some fields have errors — please review and try again.');
      }

      setSaving(false);
    },
    [activeTab, addToast]
  );

  // ── Tab switch with dirty-state guard ─────────────────────────────────────
  // Fix 5: Show confirmation dialog if current tab has unsaved changes.
  const handleTabChange = useCallback((tab: SectionName) => {
    if (tab === activeTab) return;

    if (dirtyTabsRef.current[activeTab]) {
      const confirmed = window.confirm(
        `You have unsaved changes in the "${TABS.find((t) => t.key === activeTab)?.label}" tab.\n\nLeave anyway? Your changes will be lost.`
      );
      if (!confirmed) return;
    }

    setActiveTab(tab);
    setFieldErrors({});
  }, [activeTab]);

  // ── Stable onDirtyChange callbacks per tab ───────────────────────────────
  const onHeroDirty = useCallback((isDirty: boolean) => handleDirtyChange('hero', isDirty), [handleDirtyChange]);
  const onAboutDirty = useCallback((isDirty: boolean) => handleDirtyChange('about', isDirty), [handleDirtyChange]);
  const onFooterDirty = useCallback((isDirty: boolean) => handleDirtyChange('footer', isDirty), [handleDirtyChange]);
  const onContactDirty = useCallback((isDirty: boolean) => handleDirtyChange('contact', isDirty), [handleDirtyChange]);
  const onSeoDirty = useCallback((isDirty: boolean) => handleDirtyChange('seo_home', isDirty), [handleDirtyChange]);
  const onSocialDirty = useCallback((isDirty: boolean) => handleDirtyChange('social_links', isDirty), [handleDirtyChange]);

  // ── Current section data ──────────────────────────────────────────────────
  const currentData = sectionData[activeTab] ?? DEFAULTS[activeTab];

  return (
    <div className="cms-page">

      {/* ── Page header ── */}
      <div className="cms-header">
        <div className="cms-header-inner">
          <h1 className="cms-title">
            <span className="cms-title-icon">✦</span>
            Site Content
          </h1>
          <p className="cms-subtitle">
            Edit homepage, about page, footer, contact, SEO and social links.
          </p>
        </div>
      </div>

      {/* ── Tab navigation ── */}
      <nav className="cms-tabs" aria-label="Content sections">
        {TABS.map(({ key, label, icon }) => (
          <button
            key={key}
            type="button"
            role="tab"
            aria-selected={activeTab === key}
            className={`cms-tab${activeTab === key ? ' cms-tab--active' : ''}`}
            onClick={() => handleTabChange(key)}
          >
            <span className="cms-tab-icon" aria-hidden="true">{icon}</span>
            <span className="cms-tab-label">{label}</span>
            {/* Fix 5: amber dot indicator when tab has unsaved changes */}
            {dirtyTabs[key] && (
              <span className="cms-tab-dirty-dot" aria-label="Unsaved changes" title="Unsaved changes" />
            )}
          </button>
        ))}
      </nav>

      {/* ── Section panel ── */}
      <div className="cms-panel" role="tabpanel">
        {loading ? (
          <div className="cms-loading" role="status" aria-live="polite">
            <span className="cms-spinner" />
            <span>Loading {activeTab} content…</span>
          </div>
        ) : (
          <>
            {activeTab === 'hero' && (
              <HeroForm
                initialData={currentData as HeroContent}
                onSave={(d) => handleSave(d)}
                saving={saving}
                fieldErrors={fieldErrors}
                onDirtyChange={onHeroDirty}
              />
            )}
            {activeTab === 'about' && (
              <AboutForm
                initialData={currentData as AboutContent}
                onSave={(d) => handleSave(d)}
                saving={saving}
                fieldErrors={fieldErrors}
                onDirtyChange={onAboutDirty}
              />
            )}
            {activeTab === 'footer' && (
              <FooterForm
                initialData={currentData as FooterContent}
                onSave={(d) => handleSave(d)}
                saving={saving}
                fieldErrors={fieldErrors}
                onDirtyChange={onFooterDirty}
              />
            )}
            {activeTab === 'contact' && (
              <ContactForm
                initialData={currentData as ContactContent}
                onSave={(d) => handleSave(d)}
                saving={saving}
                fieldErrors={fieldErrors}
                onDirtyChange={onContactDirty}
              />
            )}
            {activeTab === 'seo_home' && (
              <SeoHomeForm
                initialData={currentData as SeoHomeContent}
                onSave={(d) => handleSave(d)}
                saving={saving}
                fieldErrors={fieldErrors}
                onDirtyChange={onSeoDirty}
              />
            )}
            {activeTab === 'social_links' && (
              <SocialLinksForm
                initialData={currentData as SocialLinksContent}
                onSave={(d) => handleSave(d)}
                saving={saving}
                fieldErrors={fieldErrors}
                onDirtyChange={onSocialDirty}
              />
            )}
          </>
        )}
      </div>

      {/* ── Toast container ── */}
      <div className="toast-container" aria-live="assertive" aria-atomic="true">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast toast--${toast.type}`} role="alert">
            <span className="toast-icon">
              {toast.type === 'success' ? '✓' : toast.type === 'error' ? '✕' : 'ℹ'}
            </span>
            <span className="toast-message">{toast.message}</span>
            <button
              className="toast-dismiss"
              onClick={() => setToasts((prev) => prev.filter((t) => t.id !== toast.id))}
              aria-label="Dismiss notification"
            >
              ×
            </button>
          </div>
        ))}
      </div>

    </div>
  );
}
