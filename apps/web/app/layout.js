// Font files ship with the site: visitors never hit Google.
import '@fontsource/ibm-plex-mono/latin-300.css';
import '@fontsource/ibm-plex-mono/latin-400.css';
import '@fontsource/ibm-plex-mono/latin-500.css';
import './globals.css';
import Shell from '@/components/Shell';
import { SITE_URL, SITE_NAME, TAGLINE, DESCRIPTION, KEYWORDS } from '@/lib/site';

export const metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: `${SITE_NAME} · Talk to strangers`, template: `%s · ${SITE_NAME}` },
  description: DESCRIPTION,
  keywords: KEYWORDS,
  applicationName: SITE_NAME,
  creator: 'Damn_It_Rabbit',
  alternates: { canonical: '/' },
  robots: { index: true, follow: true, googleBot: { index: true, follow: true, 'max-image-preview': 'large', 'max-snippet': -1 } },
  icons: { icon: '/icon.svg' },
  // Search Console / Bing ownership, if you verify by meta tag instead of DNS.
  verification: {
    google: process.env.NEXT_PUBLIC_GOOGLE_VERIFICATION || undefined,
    other: process.env.NEXT_PUBLIC_BING_VERIFICATION ? { 'msvalidate.01': process.env.NEXT_PUBLIC_BING_VERIFICATION } : undefined
  },
  openGraph: { type: 'website', siteName: SITE_NAME, title: `${SITE_NAME} · ${TAGLINE}`, description: DESCRIPTION, url: '/', locale: 'en_US' },
  twitter: { card: 'summary_large_image', title: `${SITE_NAME} · ${TAGLINE}`, description: DESCRIPTION }
};

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'WebApplication',
  name: SITE_NAME,
  url: SITE_URL,
  description: DESCRIPTION,
  applicationCategory: 'CommunicationApplication',
  operatingSystem: 'Any (web browser)',
  offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
  creator: { '@type': 'Person', name: 'Damn_It_Rabbit' }
};

export const viewport = {
  themeColor: '#000000',
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover'
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
