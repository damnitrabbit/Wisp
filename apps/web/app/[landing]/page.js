import Link from 'next/link';
import { notFound } from 'next/navigation';
import { CHANNELS } from '@wisp/shared';
import TopBar from '@/components/TopBar';
import Footer from '@/components/Footer';
import { LANDING, LANDING_BY_SLUG } from '@/lib/landing';
import { SITE_URL, SITE_NAME } from '@/lib/site';

// Only these pages exist; any other top-level path is a 404.
export const dynamicParams = false;
export function generateStaticParams() {
  return LANDING.map((p) => ({ landing: p.slug }));
}

export async function generateMetadata({ params }) {
  const { landing } = await params;
  const p = LANDING_BY_SLUG.get(landing);
  if (!p) return {};
  return {
    title: p.title,
    description: p.description,
    alternates: { canonical: `/${p.slug}` },
    // Setting openGraph here replaces the site-wide one, so the preview image has to be named again.
    openGraph: { title: `${p.title} · ${SITE_NAME}`, description: p.description, url: `/${p.slug}`, images: [{ url: '/opengraph-image', width: 1200, height: 630, alt: 'N0TRACE' }] },
    twitter: { card: 'summary_large_image', images: ['/opengraph-image'] }
  };
}

export default async function Landing({ params }) {
  const { landing } = await params;
  const p = LANDING_BY_SLUG.get(landing);
  if (!p) notFound();

  const faqLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: p.faq.map((f) => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } }))
  };
  const crumbsLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: SITE_NAME, item: SITE_URL },
      { '@type': 'ListItem', position: 2, name: p.title, item: `${SITE_URL}/${p.slug}` }
    ]
  };

  return (
    <div className="page">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify([faqLd, crumbsLd]) }} />
      <TopBar crumb={`/${p.slug.toUpperCase()}`} back={{ label: '← LOBBY', href: '/' }} />
      <main className="main landing">
        <div className="lead">
          <h1>{p.h1}</h1>
          <p className="intro">{p.lead}</p>
          <div className="ctas">
            <Link href="/chat" className="btn solid tall spread">
              <span>[ START A 1:1 CHAT ]</span>
              <span>→</span>
            </Link>
            <Link href="/rooms" className="btn tall spread">
              <span>[ BROWSE VOICE ROOMS ]</span>
              <span>→</span>
            </Link>
          </div>
          <p className="dim3" style={{ fontSize: 11 }}>FREE · NO SIGN-UP · 18+ ONLY</p>
        </div>
        <div className="body">
          {p.sections.map((s) => (
            <section key={s.h}>
              <h2>{s.h}</h2>
              <p>{s.body}</p>
            </section>
          ))}
          <section>
            <h2>Questions</h2>
            <dl className="faq">
              {p.faq.map((f) => (
                <div key={f.q}>
                  <dt>{f.q}</dt>
                  <dd>{f.a}</dd>
                </div>
              ))}
            </dl>
          </section>
          <section>
            <h2>Rooms right now</h2>
            <p>
              {CHANNELS.slice(0, 12).map((c, i) => (
                <span key={c.id}>
                  {i > 0 && ' · '}
                  <Link href={`/rooms/${c.id}`} className="inline">{c.name}</Link>
                </span>
              ))}
              {' · '}
              <Link href="/rooms" className="inline">all 25 rooms →</Link>
            </p>
          </section>
          <section>
            <h2>More</h2>
            <p>
              {LANDING.filter((o) => o.slug !== p.slug).map((o, i) => (
                <span key={o.slug}>
                  {i > 0 && ' · '}
                  <Link href={`/${o.slug}`} className="inline">{o.title}</Link>
                </span>
              ))}
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
