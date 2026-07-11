'use client';

import React, { useEffect, useRef } from 'react';
import { AboutContent } from '@/lib/types/site-content';
import Image from 'next/image';

interface AboutSectionProps {
  about: AboutContent;
}

export default function AboutSection({ about }: AboutSectionProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check user preference for animations
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target); // Trigger only once
          }
        });
      },
      { threshold: 0.15, rootMargin: '0px 0px -50px 0px' }
    );

    const revealItems = containerRef.current?.querySelectorAll('.reveal-item');
    revealItems?.forEach((item) => observer.observe(item));

    return () => observer.disconnect();
  }, [about]);

  if (!about) return null;

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
      {/* Background glow */}
      <div className="cosmic-glow-1" style={{ top: '30%', left: '-10%', opacity: 0.35 }}></div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '4rem',
        alignItems: 'center',
      }}>
        {/* Text Area */}
        <div className="reveal-item" style={{
          opacity: 0,
          transform: 'translateY(30px)',
          transition: 'opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
        }}>
          <h1 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(2rem, 4vw, 3rem)',
            fontWeight: 700,
            marginBottom: '1.5rem',
            lineHeight: '1.2',
            background: 'linear-gradient(90deg, #fff, var(--text-secondary))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            {about.title}
          </h1>

          
          <div style={{
            color: 'var(--text-secondary)',
            lineHeight: '1.8',
            fontSize: '1.05rem',
            fontWeight: 300,
            marginBottom: '2.5rem',
            whiteSpace: 'pre-line',
          }}>
            {about.body_text}
          </div>

          {/* Founder Profile */}
          {about.founder_name && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1.25rem',
              padding: '1.25rem',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              borderRadius: '16px',
              maxWidth: '400px',
            }}>
              {about.founder_photo && (
                <Image
                  src={about.founder_photo}
                  alt={about.founder_name}
                  width={60}
                  height={60}
                  style={{
                    borderRadius: '50%',
                    objectFit: 'cover',
                    border: '2px solid var(--color-pink)',
                  }}
                />
              )}
              <div>
                <p style={{
                  fontSize: '0.85rem',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                }}>
                  Founder
                </p>
                <p style={{
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  fontFamily: 'var(--font-display)',
                }}>
                  {about.founder_name}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Gallery / Images Grid */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '1.5rem',
          }}>
            {about.images?.slice(0, 4).map((imgUrl, index) => (
              <div 
                key={index} 
                className="reveal-item"
                style={{
                  opacity: 0,
                  transform: 'translateY(40px)',
                  transition: `opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1) ${0.1 * index}s, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1) ${0.1 * index}s`,
                  borderRadius: '16px',
                  overflow: 'hidden',
                  position: 'relative',
                  aspectRatio: '1',
                  border: '1px solid rgba(255, 255, 255, 0.05)',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
                }}
              >
                <Image
                  src={imgUrl}
                  alt={`Gallery image ${index + 1}`}
                  fill
                  sizes="(max-width: 768px) 50vw, 25vw"
                  style={{
                    objectFit: 'cover',
                    transition: 'transform 0.6s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.08)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)';
                  }}
                />
              </div>
            ))}
          </div>
        </div>
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
