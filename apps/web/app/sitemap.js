import { SITE_URL } from '@/lib/site';
import { LANDING } from '@/lib/landing';

export default function sitemap() {
  const now = new Date();
  return [
    { url: `${SITE_URL}/`, lastModified: now, changeFrequency: 'weekly', priority: 1 },
    { url: `${SITE_URL}/rooms`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
    { url: `${SITE_URL}/chat`, lastModified: now, changeFrequency: 'weekly', priority: 0.9 },
    { url: `${SITE_URL}/echoes`, lastModified: now, changeFrequency: 'weekly', priority: 0.8 },
    ...LANDING.map((p) => ({ url: `${SITE_URL}/${p.slug}`, lastModified: now, changeFrequency: 'monthly', priority: 0.8 })),
    { url: `${SITE_URL}/privacy`, lastModified: now, changeFrequency: 'yearly', priority: 0.3 },
    { url: `${SITE_URL}/terms`, lastModified: now, changeFrequency: 'yearly', priority: 0.3 }
  ];
}
