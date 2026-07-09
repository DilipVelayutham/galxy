import { BulkSiteContent } from '../types/site-content';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';

export async function getSection<T>(section: string): Promise<T> {
  const res = await fetch(`${BASE_URL}/api/site-content/${section}`, {
    next: { revalidate: 60 }
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch section ${section}: ${res.statusText}`);
  }

  const json = await res.json();
  if (!json.success) {
    throw new Error(`API error fetching section ${section}: ${json.message || 'Unknown error'}`);
  }

  return (json.data?.content ?? json.data) as T;
}

export async function getBulkSections(sections: string[]): Promise<BulkSiteContent> {
  const query = sections.join(',');
  const res = await fetch(`${BASE_URL}/api/site-content?sections=${query}`, {
    next: { revalidate: 60 }
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch bulk sections: ${res.statusText}`);
  }

  const json = await res.json();
  if (!json.success) {
    throw new Error(`API error fetching bulk sections: ${json.message || 'Unknown error'}`);
  }

  return json.data as BulkSiteContent;
}

export function formatWhatsAppLink(whatsappNumber: string | null | undefined): string {
  if (!whatsappNumber) return '';
  const clean = whatsappNumber.replace(/[^\d]/g, '');
  return `https://wa.me/${clean}`;
}


