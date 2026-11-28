import Link from 'next/link';
import { notFound } from 'next/navigation';
import { CHANNELS } from '@wisp/shared';
import Rabbit from '@/components/Rabbit';
import { LANDING, LANDING_BY_SLUG } from '@/lib/landing';
import { SITE_URL, SITE_NAME } from '@/lib/site';
import './landing.css';

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
    <div className="lp">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify([faqLd, crumbsLd]) }} />

      <header className="lp-top">
        <Link href="/" className="lp-brand" aria-label="N0TRACE home">
          <Rabbit className="lp-rab" />
          <span className="lp-word">N0TRACE</span>
        </Link>
        <Link href="/help" className="lp-help">need help now?</Link>
      </header>

      <main className="lp-main">
        <section className="lp-hero">
          <div className="lp-crumb rise" style={{ '--w': '.1s' }}>{p.slug.replace(/-/g, ' ')}</div>
          <h1 className="lp-h1 rise" style={{ '--w': '.2s' }}>{p.h1}</h1>
          <p className="lp-lead rise" style={{ '--w': '.35s' }}>{p.lead}</p>
          <div className="lp-cta rise" style={{ '--w': '.5s' }}>
            <Link href="/talk" className="lp-btn">talk to someone <span className="arr">→</span></Link>
            <Link href="/rooms" className="lp-btn ghost">browse voice rooms <span className="arr">→</span></Link>
          </div>
          <p className="lp-meta rise" style={{ '--w': '.6s' }}>
            free · no sign-up · 18+ · <span className="hrs">pods open 10pm–2am</span>
          </p>
        </section>

        <div className="lp-body">
          {p.sections.map((s) => (
            <section key={s.h}>
              <h2 className="lp-h2">{s.h}</h2>
              <p className="lp-p">{s.body}</p>
            </section>
          ))}

          <div className="lp-faq paper hi">
            <h2 className="lp-faq-h">Questions</h2>
            <dl>
              {p.faq.map((f) => (
                <div key={f.q}>
                  <dt>{f.q}</dt>
                  <dd>{f.a}</dd>
                </div>
              ))}
            </dl>
          </div>

          <section className="lp-links">
            <h2 className="lp-h2">Rooms open tonight</h2>
            <p>
              {CHANNELS.slice(0, 12).map((c, i) => (
                <span key={c.id}>
                  {i > 0 && <span className="lp-sep">·</span>}
                  <Link href={`/rooms/${c.id}`} className="lp-ln">{c.name}</Link>
                </span>
              ))}
              <span className="lp-sep">·</span>
              <Link href="/rooms" className="lp-ln">all 25 rooms →</Link>
            </p>
          </section>

          <section className="lp-links">
            <h2 className="lp-h2">More ways in</h2>
            <p>
              {LANDING.filter((o) => o.slug !== p.slug).map((o, i) => (
                <span key={o.slug}>
                  {i > 0 && <span className="lp-sep">·</span>}
                  <Link href={`/${o.slug}`} className="lp-ln">{o.slug.replace(/-/g, ' ')}</Link>
                </span>
              ))}
            </p>
          </section>
        </div>
      </main>

      <footer className="lp-foot">
        <nav aria-label="N0TRACE">
          <Link href="/privacy">what we keep</Link>
          <Link href="/terms">terms</Link>
          <Link href="/help">need help</Link>
        </nav>
        <span>dug up by <span className="nc">Damn_It_Rabbit</span> · 18+</span>
      </footer>
    </div>
  );
}
