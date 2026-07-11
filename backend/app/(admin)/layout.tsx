/**
 * app/(admin)/layout.tsx
 *
 * Admin section layout — wraps all /admin/* routes.
 * - Dark theme only (no light mode toggle — brand-wide rule)
 * - Uses next/font/local to self-host Inter, removing the
 *   external fonts.googleapis.com dependency that would fail
 *   in air-gapped CI environments (Audit §7.4).
 *
 * Auth guard is handled by Module 12's shared admin layout.
 * This layout provides only the admin shell (topbar, CSS) specific
 * to the Site Content module. Module 12's layout wraps this one.
 */

import type { Metadata } from 'next';
import localFont from 'next/font/local';
import './admin.css';

const inter = localFont({
  src: [
    { path: '../../public/fonts/inter/Inter-Regular.ttf', weight: '400', style: 'normal' },
    { path: '../../public/fonts/inter/Inter-Medium.ttf', weight: '500', style: 'normal' },
    { path: '../../public/fonts/inter/Inter-SemiBold.ttf', weight: '600', style: 'normal' },
    { path: '../../public/fonts/inter/Inter-Bold.ttf', weight: '700', style: 'normal' },
  ],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: { default: 'Admin — GALXY CMS', template: '%s | GALXY Admin' },
  description: 'GALXY Custom Lighting & Craft Studio — Admin Panel',
  robots: { index: false, follow: false },
};

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className={`admin-shell ${inter.variable}`}>
      <header className="admin-topbar">
        <div className="admin-topbar-inner">
          <span className="admin-logo">
            <span className="admin-logo-mark">✦</span>
            GALXY Admin
          </span>
          <nav className="admin-nav" aria-label="Admin navigation">
            <a href="/site-content" className="admin-nav-link">
              Site Content
            </a>
          </nav>
          <div className="admin-topbar-end">
            <span className="admin-badge">Admin</span>
          </div>
        </div>
      </header>

      <main className="admin-main">
        {children}
      </main>
    </div>
  );
}
