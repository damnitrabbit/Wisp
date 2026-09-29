import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="l">
        <span>LOGS: OFF</span>
        <span>18+ ONLY</span>
        <nav aria-label="Legal">
          <Link href="/privacy">PRIVACY</Link>
          <Link href="/terms">TERMS</Link>
          <Link href="/privacy#contact">
            CONTACT <span className="who nc">Damn_It_Rabbit</span>
          </Link>
        </nav>
      </div>
      <div className="r">
        <span>© 2026 N0TRACE</span>
        <span>
          DUG UP BY <span className="nc" style={{ color: 'var(--fg)' }}>Damn_It_Rabbit</span>
        </span>
      </div>
      <span className="m">
        © 2026 N0TRACE · DUG UP BY <span className="nc" style={{ color: 'var(--fg)' }}>Damn_It_Rabbit</span> · 18+
      </span>
    </footer>
  );
}
