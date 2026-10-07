// Font files ship with the site: visitors never hit Google.
import '@fontsource/courier-prime/latin-400.css';
import '@fontsource/courier-prime/latin-700.css';
import '@fontsource/covered-by-your-grace/latin-400.css';
import '@fontsource/nothing-you-could-do/latin-400.css';
import '@fontsource/newsreader/latin-300.css';
import '@fontsource/newsreader/latin-400.css';
import '@fontsource/newsreader/latin-300-italic.css';
import '@fontsource/newsreader/latin-400-italic.css';
import '@/v5/base.css';
import './v5.css';
import Script from 'next/script';
import Shell from '@/components/Shell';
import { SITE_URL, SITE_NAME, TITLE, ALT_NAMES, DESCRIPTION, KEYWORDS } from '@/lib/site';

export const metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: TITLE, template: `%s · ${SITE_NAME}` },
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
  openGraph: { type: 'website', siteName: SITE_NAME, title: TITLE, description: DESCRIPTION, url: '/', locale: 'en_US' },
  twitter: { card: 'summary_large_image', title: TITLE, description: DESCRIPTION }
};

// WebSite is what Google reads for the site name shown above results; alternateName covers N0TRACE.
const jsonLd = [
  { '@context': 'https://schema.org', '@type': 'WebSite', name: SITE_NAME, alternateName: ALT_NAMES, url: `${SITE_URL}/` },
  {
  '@context': 'https://schema.org',
  '@type': 'WebApplication',
  name: SITE_NAME,
  alternateName: ALT_NAMES,
  url: SITE_URL,
  description: DESCRIPTION,
  applicationCategory: 'CommunicationApplication',
  operatingSystem: 'Any (web browser)',
  offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
  creator: { '@type': 'Person', name: 'Damn_It_Rabbit' }
  }
];

export const viewport = {
  themeColor: '#0D0D0E',
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
        {/* the paper sounds: synthesised in the browser, nothing fetched; muted with the pill or M */}
        <Script src="/sound.js" strategy="afterInteractive" />
      </body>
    </html>
  );
}
