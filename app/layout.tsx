import './globals.css';
import React from 'react';
import Link from 'next/link';
import Footer from '@/components/site-content/Footer';
import { getBulkSections, getSection } from '@/lib/api/site-content';
import { SeoHomeContent } from '@/lib/types/site-content';
import { Metadata } from 'next';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const seo = await getSection<SeoHomeContent>('seo_home');
    return {
      title: seo?.meta_title || '',
      description: seo?.meta_description || '',
      openGraph: {
        title: seo?.meta_title || '',
        description: seo?.meta_description || '',
        images: seo?.og_image ? [{ url: seo.og_image }] : [],
      },
    };
  } catch (error) {
    console.error('Error fetching global metadata:', error);
    return {}; // No hardcoded fallback copy
  }
}


export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  let footer = null;
  let socialLinks = null;
  let contact = null;

  try {
    const data = await getBulkSections(['footer', 'social_links', 'contact']);
    footer = data.footer;
    socialLinks = data.social_links;
    contact = data.contact;
  } catch (error) {
    console.error('Error fetching global layout content:', error);
  }

  return (
    <html lang="en">
      <head>
      </head>
      <body>
        {/* Navigation Bar */}
        <header style={{
          position: 'sticky',
          top: 0,
          background: 'rgba(3, 3, 3, 0.75)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
          zIndex: 50,
        }}>
          <nav className="navbar">
            <Link href="/" className="nav-logo">
              GALXY
            </Link>
            <ul className="nav-links">
              <li>
                <Link href="/" className="nav-link">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/about" className="nav-link">
                  About
                </Link>
              </li>
              <li>
                <Link href="/contact" className="nav-link">
                  Contact
                </Link>
              </li>
            </ul>
          </nav>
        </header>

        {/* Global Page Content */}
        <main>{children}</main>

        {/* Global Footer */}
        {footer && <Footer footer={footer} socialLinks={socialLinks} />}


      </body>
    </html>
  );
}
