'use client';

import React, { useState, useEffect } from 'react';
import { HeroContent } from '@/lib/types/site-content';

interface HeroSectionProps {
  hero: HeroContent;
}

export default function HeroSection({ hero }: HeroSectionProps) {
  const [isMobile, setIsMobile] = useState(true);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    handleResize(); // Initial check
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (!hero) return null;

  return (
    <section style={{
      position: 'relative',
      height: '90vh',
      minHeight: '600px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      overflow: 'hidden',
      backgroundColor: 'var(--bg-space)',
      textAlign: 'center',
      padding: '0 1.5rem',
    }}>
      {/* Background Media */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 1,
      }}>
        {!isMobile && hero.background_video_url ? (
          /* Desktop Background Video */
          <video
            autoPlay
            loop
            muted
            playsInline
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: 0.35,
            }}
          >
            <source src={hero.background_video_url} type="video/mp4" />
          </video>
        ) : (
          /* Mobile Background Image (Static image only for performance/battery) */
          <div
            style={{
              width: '100%',
              height: '100%',
              backgroundImage: `radial-gradient(circle at center, rgba(88, 86, 214, 0.2) 0%, transparent 60%), url(${hero.background_image_url})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              opacity: 0.35,
            }}
          />
        )}
      </div>

      {/* Grain / Noise Overlay */}
      <div className="grain-overlay"></div>

      {/* Ambient background glows */}
      <div className="cosmic-glow-1"></div>
      
      {/* Hero Content */}
      <div style={{
        position: 'relative',
        zIndex: 3,
        maxWidth: '800px',
        margin: '0 auto',
      }}>
        <h1
          className="power-on-flicker"
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(2.5rem, 6vw, 4.5rem)',
            fontWeight: 800,
            lineHeight: 1.1,
            marginBottom: '1.5rem',
            color: 'var(--text-primary)',
            letterSpacing: '-1px',
          }}
        >
          {hero.headline}
        </h1>
        
        <p style={{
          fontFamily: 'var(--font-sans)',
          fontSize: 'clamp(1rem, 2.5vw, 1.25rem)',
          color: 'var(--text-secondary)',
          lineHeight: '1.6',
          maxWidth: '600px',
          margin: '0 auto 2.5rem',
          fontWeight: 300,
        }}>
          {hero.subheadline}
        </p>
        
        {hero.cta_text && hero.cta_link && (
          <div>
            <a href={hero.cta_link} className="gradient-border-btn" style={{ textDecoration: 'none', display: 'inline-block' }}>
              {hero.cta_text}
            </a>
          </div>
        )}
      </div>
    </section>
  );
}

