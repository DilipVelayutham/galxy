import React from 'react';
import Link from 'next/link';
import { FooterContent, SocialLinksContent } from '@/lib/types/site-content';
import SocialLinks from './SocialLinks';

interface FooterProps {
  footer: FooterContent;
  socialLinks: SocialLinksContent | null | undefined;
}

export default function Footer({ footer, socialLinks }: FooterProps) {
  if (!footer) return null;

  return (
    <footer style={{
      background: 'linear-gradient(to top, #06060a, var(--bg-space))',
      borderTop: '1px solid rgba(255, 255, 255, 0.05)',
      padding: '4rem 2rem 2.5rem',
      position: 'relative',
      zIndex: 5,
    }}>
      <div className="cosmic-glow-2" style={{ bottom: '0', right: '5%', opacity: 0.5 }}></div>
      
      <div style={{
        maxWidth: 'var(--max-width)',
        margin: '0 auto',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '3rem',
        marginBottom: '3rem',
      }}>
        {/* Brand Section */}
        <div>
          <Link href="/" className="nav-logo" style={{ marginBottom: '1.25rem', display: 'inline-flex' }}>
            GALXY
          </Link>
          <p style={{
            color: 'var(--text-secondary)',
            fontSize: '1rem',
            lineHeight: '1.6',
            maxWidth: '300px',
            marginBottom: '1.5rem'
          }}>
            {footer.tagline}
          </p>
          <SocialLinks socialLinks={socialLinks} />
        </div>

        {/* Quick Links */}
        <div>
          <h4 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.1rem',
            fontWeight: '600',
            marginBottom: '1.25rem',
            letterSpacing: '1px',
            textTransform: 'uppercase',
            color: 'var(--text-primary)'
          }}>
            Quick Links
          </h4>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
            {footer.quick_links?.map((link, idx) => {
              // Check if URL is local or external
              const isExternal = link.url.startsWith('http');
              if (isExternal) {
                return (
                  <li key={idx}>
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="footer-link"
                    >
                      {link.label}
                    </a>
                  </li>
                );
              }
              return (
                <li key={idx}>
                  <Link href={link.url} className="footer-link">
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Business Hours */}
        <div>
          <h4 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.1rem',
            fontWeight: '600',
            marginBottom: '1.25rem',
            letterSpacing: '1px',
            textTransform: 'uppercase',
            color: 'var(--text-primary)'
          }}>
            Business Hours
          </h4>
          <div style={{
            color: 'var(--text-secondary)',
            fontSize: '0.95rem',
            lineHeight: '1.6',
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            borderRadius: '12px',
            padding: '1rem 1.25rem',
            display: 'inline-block'
          }}>
            {(footer.business_hours?.split('\n') || []).map((line, idx) => (
              <p key={idx} style={{ margin: '0.2rem 0' }}>{line}</p>
            ))}
          </div>
        </div>
      </div>

      {/* Copyright */}
      <div style={{
        maxWidth: 'var(--max-width)',
        margin: '0 auto',
        paddingTop: '2rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem',
        fontSize: '0.85rem',
        color: 'var(--text-muted)'
      }}>
        <p>&copy; {new Date().getFullYear()} GALXY Studio. All rights reserved.</p>
      </div>
    </footer>
  );
}
