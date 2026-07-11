import React from 'react';
import { getSection } from '@/lib/api/site-content';
import { HeroContent } from '@/lib/types/site-content';
import HeroSection from '@/components/site-content/HeroSection';

export default async function HomePage() {
  let hero: HeroContent | null = null;

  try {
    hero = await getSection<HeroContent>('hero');
  } catch (error) {
    console.error('Error fetching homepage content:', error);
  }

  return (
    <div style={{ backgroundColor: 'var(--bg-space)', minHeight: '100vh', position: 'relative' }}>
      {/* Background glow overlay */}
      <div className="cosmic-glow-2" style={{ top: '40%', left: '10%', opacity: 0.25 }}></div>
      
      {/* Hero Section */}
      {hero ? (
        <HeroSection hero={hero} />
      ) : (
        <div style={{ 
          height: '60vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: 'var(--text-secondary)',
          fontFamily: 'var(--font-display)',
          fontSize: '1.25rem'
        }}>
          Connecting to GALXY Studio API...
        </div>
      )}
    </div>
  );
}

