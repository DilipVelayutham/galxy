'use client';

import React from 'react';
import { SocialLinksContent } from '@/lib/types/site-content';

interface SocialLinksProps {
  socialLinks: SocialLinksContent | null | undefined;
}

export default function SocialLinks({ socialLinks }: SocialLinksProps) {
  if (!socialLinks) return null;

  const links = [
    {
      name: 'Instagram',
      url: socialLinks.instagram,
      icon: (
        <svg viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 4m0 4a4 4 0 0 1 4 -4h8a4 4 0 0 1 4 4v8a4 4 0 0 1 -4 4h-8a4 4 0 0 1 -4 -4z" />
          <path d="M12 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0" />
          <path d="M16.5 7.5l0 .01" />
        </svg>
      ),
      hoverGlow: 'rgba(255, 45, 85, 0.4)',
    },
    {
      name: 'Facebook',
      url: socialLinks.facebook,
      icon: (
        <svg viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
          <path d="M7 10v4h3v7h4v-7h3l1 -4h-4v-2a1 1 0 0 1 1 -1h3v-4h-3a5 5 0 0 0 -5 5v2h-3" />
        </svg>
      ),
      hoverGlow: 'rgba(0, 122, 255, 0.4)',
    },
    {
      name: 'YouTube',
      url: socialLinks.youtube,
      icon: (
        <svg viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 4m0 4a4 4 0 0 1 4 -4h8a4 4 0 0 1 4 4v8a4 4 0 0 1 -4 4h-8a4 4 0 0 1 -4 -4z" />
          <path d="M10 9l5 3l-5 3z" />
        </svg>
      ),
      hoverGlow: 'rgba(255, 0, 0, 0.4)',
    },
  ].filter(link => link.url);

  return (
    <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'center' }}>
      {links.map((link) => (
        <a
          key={link.name}
          href={link.url || '#'}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={link.name}
          className="social-icon-link"
          style={{
            color: 'var(--text-secondary)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '42px',
            height: '42px',
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            transition: 'var(--transition-smooth)',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = 'var(--text-primary)';
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)';
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = `0 4px 15px ${link.hoverGlow}`;
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--text-secondary)';
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
          }}
        >
          <span style={{ width: '20px', height: '20px', display: 'block' }}>{link.icon}</span>
        </a>
      ))}
    </div>
  );
}
