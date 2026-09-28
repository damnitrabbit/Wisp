import Link from 'next/link';
import TopBar from './TopBar';
import Footer from './Footer';

export const CONTACT_EMAIL = 'damnitrabbit.build@gmail.com';
export const UPDATED = '29 SEP 2026';

export default function Legal({ title, blurb, other, children }) {
  return (
    <div className="page">
      <TopBar crumb={`/${title}`} showOnline={false} back={{ label: '← BACK', href: '/' }} />
      <main className="main legal">
        <div className="lead">
          <h1>{title}</h1>
          <p className="dim" style={{ fontSize: 13, lineHeight: 1.6 }}>{blurb}</p>
          <dl className="kv">
            <dt>UPDATED</dt><dd className="dim">{UPDATED}</dd>
            <dt>RUN BY</dt><dd className="dim nc">Damn_It_Rabbit</dd>
            <dt>SEE ALSO</dt><dd><Link href={`/${other.toLowerCase()}`}>{other}</Link></dd>
          </dl>
        </div>
        <div className="body">
          {children}
          <section id="contact">
            <h2>CONTACT</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <p>WISP IS BUILT AND RUN BY ONE PERSON WHO GOES BY <span className="nc" style={{ color: 'var(--fg)' }}>Damn_It_Rabbit</span>. THAT&apos;S THE ONLY NAME YOU&apos;LL SEE HERE.</p>
              <p className="mail">
                WRITE TO <span className="nc">Damn_It_Rabbit</span>: <a className="nc" href={`mailto:${CONTACT_EMAIL}`} style={{ textDecoration: 'underline', textUnderlineOffset: 3 }}>{CONTACT_EMAIL}</a>
              </p>
            </div>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}

export function S({ h, children }) {
  return (
    <section>
      <h2>{h}</h2>
      <div>{children}</div>
    </section>
  );
}
