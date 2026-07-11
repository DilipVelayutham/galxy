'use client';

import React, { useEffect, useRef } from 'react';
import { ContactContent } from '@/lib/types/site-content';
import { formatWhatsAppLink } from '@/lib/api/site-content';

interface ContactSectionProps {
  contact: ContactContent;
}

export default function ContactSection({ contact }: ContactSectionProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: '0px 0px -50px 0px' }
    );

    const revealItems = containerRef.current?.querySelectorAll('.reveal-item');
    revealItems?.forEach((item) => observer.observe(item));

    return () => observer.disconnect();
  }, [contact]);

  if (!contact) return null;

  return (
    <section
      ref={containerRef}
      style={{
        padding: '8rem 2rem',
        position: 'relative',
        zIndex: 3,
        maxWidth: 'var(--max-width)',
        margin: '0 auto',
      }}
    >
      <div className="cosmic-glow-2" style={{ top: '10%', right: '-15%', opacity: 0.3 }}></div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '4rem',
        alignItems: 'stretch',
      }}>
        {/* Contact Details Card */}
        <div 
          className="glass-card reveal-item"
          style={{
            opacity: 0,
            transform: 'translateY(30px)',
            transition: 'opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}
        >


          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {/* Phone */}
            {contact.phone && (
              <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start' }}>
                <div style={{
                  color: 'var(--color-pink)',
                  background: 'rgba(255, 45, 85, 0.08)',
                  padding: '0.75rem',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <svg style={{ width: '24px', height: '24px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-2.824-1.802-5.18-4.156-6.98-6.98l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
                  </svg>
                </div>
                <div>
                  <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '0.25rem' }}>Phone</h4>
                  <a href={`tel:${contact.phone}`} style={{ color: 'var(--text-primary)', fontSize: '1.1rem', textDecoration: 'none', transition: 'var(--transition-smooth)' }} className="footer-link">
                    {contact.phone}
                  </a>
                </div>
              </div>
            )}

            {/* WhatsApp */}
            {contact.whatsapp_number && (
              <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start' }}>
                <div style={{
                  color: '#25d366',
                  background: 'rgba(37, 211, 102, 0.08)',
                  padding: '0.75rem',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <svg style={{ width: '24px', height: '24px' }} viewBox="0 0 24 24" fill="currentColor">
                    <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946C.06 5.348 5.397.01 12.008.01c3.202.001 6.212 1.246 8.477 3.514 2.266 2.268 3.507 5.28 3.505 8.484-.004 6.657-5.34 11.997-11.953 11.997-2.005-.001-3.973-.502-5.73-1.455L0 24zm6.59-4.846c1.6.95 3.188 1.449 4.825 1.451 5.436 0 9.86-4.37 9.864-9.799.002-2.63-1.023-5.101-2.885-6.97C16.49 1.966 14.023.94 11.412.94C5.975.94 1.55 5.31 1.546 10.74c-.002 1.733.456 3.42 1.326 4.927L1.87 20.317l4.777-1.163z"/>
                  </svg>
                </div>
                <div>
                  <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '0.25rem' }}>WhatsApp</h4>
                  <a href={formatWhatsAppLink(contact.whatsapp_number)} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text-primary)', fontSize: '1.1rem', textDecoration: 'none', transition: 'var(--transition-smooth)' }} className="footer-link">
                    {contact.whatsapp_number}
                  </a>
                </div>
              </div>
            )}

            {/* Email */}
            {contact.email && (
              <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start' }}>
                <div style={{
                  color: 'var(--color-blue)',
                  background: 'rgba(0, 122, 255, 0.08)',
                  padding: '0.75rem',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <svg style={{ width: '24px', height: '24px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0l-7.5-4.615a2.25 2.25 0 01-1.07-1.916V6.75" />
                  </svg>
                </div>
                <div>
                  <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '0.25rem' }}>Email</h4>
                  <a href={`mailto:${contact.email}`} style={{ color: 'var(--text-primary)', fontSize: '1.1rem', textDecoration: 'none', transition: 'var(--transition-smooth)' }} className="footer-link">
                    {contact.email}
                  </a>
                </div>
              </div>
            )}

            {/* Address */}
            {contact.address && (
              <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start' }}>
                <div style={{
                  color: 'var(--color-violet)',
                  background: 'rgba(88, 86, 214, 0.08)',
                  padding: '0.75rem',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <svg style={{ width: '24px', height: '24px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25s-7.5-4.108-7.5-11.25A7.5 7.5 0 0112 3a7.5 7.5 0 017.5 7.5z" />
                  </svg>
                </div>
                <div>
                  <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '0.25rem' }}>Address</h4>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', lineHeight: '1.5', fontWeight: 300 }}>
                    {contact.address}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Map Embed Container */}
        {contact.map_embed_url && (
          <div
            className="reveal-item"
            style={{
              opacity: 0,
              transform: 'translateY(40px)',
              transition: 'opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.15s, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.15s',
              borderRadius: '24px',
              overflow: 'hidden',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
              minHeight: '350px',
              position: 'relative',
            }}
          >
            <iframe
              src={contact.map_embed_url}
              width="100%"
              height="100%"
              style={{ border: 0, position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
              allowFullScreen={false}
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              title="GALXY Studio Map Location"
            />
          </div>
        )}
      </div>

      <style jsx global>{`
        .reveal-item.visible {
          opacity: 1 !important;
          transform: translateY(0) !important;
        }
      `}</style>
    </section>
  );
}
