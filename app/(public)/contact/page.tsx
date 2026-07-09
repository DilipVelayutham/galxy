import React from 'react';
import { getSection } from '@/lib/api/site-content';
import { ContactContent } from '@/lib/types/site-content';
import ContactSection from '@/components/site-content/ContactSection';

export default async function ContactPage() {
  let contact: ContactContent | null = null;

  try {
    contact = await getSection<ContactContent>('contact');
  } catch (error) {
    console.error('Error fetching contact page content:', error);
  }

  return (
    <div style={{ backgroundColor: 'var(--bg-space)', minHeight: '80vh', position: 'relative' }}>
      {contact ? (
        <ContactSection contact={contact} />
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
