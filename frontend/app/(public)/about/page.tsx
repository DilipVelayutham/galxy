import React from 'react';
import { getSection } from '@/lib/api/site-content';
import { AboutContent } from '@/lib/types/site-content';
import AboutSection from '@/components/site-content/AboutSection';

export default async function AboutPage() {
  let about: AboutContent | null = null;

  try {
    about = await getSection<AboutContent>('about');
  } catch (error) {
    console.error('Error fetching about page content:', error);
  }

  return (
    <div style={{ backgroundColor: 'var(--bg-space)', minHeight: '80vh', position: 'relative' }}>
      {about ? (
        <AboutSection about={about} />
      ) : (
        <div style={{ 
          height: '40vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: 'var(--text-secondary)',
          fontFamily: 'var(--font-display)',
          fontSize: '1.25rem'
        }}>
          Content Unavailable
        </div>
      )}
    </div>
  );
}
