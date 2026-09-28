'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import TopBar from './TopBar';
import Footer from './Footer';
import Rabbit from './Rabbit';
import { onboarding } from '@/lib/wisp';

// First visit: boot → age gate → three slides → pick a mode.
export default function Onboarding({ next, onDone }) {
  const [step, setStep] = useState('boot'); // boot | age | under18 | slides | mode
  const [slide, setSlide] = useState(0);

  useEffect(() => {
    if (onboarding.ageOk()) setStep('slides');
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [step]);

  // After the slides, a deep link skips the mode choice and goes straight where it pointed.
  const afterSlides = () => (next ? onDone(next) : setStep('mode'));

  useEffect(() => {
    const onKey = (e) => {
      if (e.target.tagName === 'INPUT') return;
      const k = e.key.toLowerCase();
      if (step === 'boot' && k === 'enter') setStep('age');
      if (step === 'age' && k === 'y') confirm();
      if (step === 'age' && k === 'n') setStep('under18');
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  const confirm = () => {
    onboarding.confirmAge();
    setStep('slides');
  };

  if (step === 'boot') return <Boot onEnter={() => setStep('age')} />;

  if (step === 'age') {
    return (
      <div className="page">
        <TopBar crumb="FIRST VISIT" showOnline={false} />
        <main className="main split">
          <div className="lead">
            <div className="eyebrow">[ 1/3 ] BEFORE YOU GO IN</div>
            <h1 className="h-30">WISP IS AN ANONYMOUS PLACE FOR ADULTS. YOU&apos;LL TALK TO PEOPLE YOU DON&apos;T KNOW, UNDER NAMES THAT AREN&apos;T REAL.</h1>
            <p className="p-18">
              BE THE KIND OF STRANGER YOU&apos;D WANT TO MEET.<span className="cursor" style={{ color: 'var(--fg)' }}>_</span>
            </p>
          </div>
          <div className="side box age-card">
            <dl className="kv">
              <dt>REQUIRED</dt><dd>18 OR OLDER</dd>
              <dt>CHECKED BY</dt><dd>YOU. WE TAKE YOUR WORD.</dd>
              <dt>ACCOUNT</dt><dd>NONE. NOTHING TO SIGN UP FOR.</dd>
            </dl>
            <div className="ask">
              <div className="eyebrow">HOW OLD ARE YOU?</div>
              <button type="button" className="btn solid tall spread" onClick={confirm}>
                <span>[ Y ] I&apos;M 18 OR OLDER</span><span>→</span>
              </button>
              <button type="button" className="btn tall spread dim" onClick={() => setStep('under18')}>
                <span>[ N ] I&apos;M UNDER 18</span>
              </button>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (step === 'under18') {
    return (
      <div className="page">
        <TopBar crumb="FIRST VISIT" showOnline={false} back={{ label: '← BACK' }} onBack={() => setStep('age')} />
        <main className="main" style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
          <div className="eyebrow">[ 1/3 ] NOT FOR YOU YET</div>
          <h1 className="h-40" style={{ maxWidth: 820, fontSize: 'clamp(26px, 4vw, 40px)', lineHeight: 1.35 }}>
            SORRY. WISP IS ONLY FOR PEOPLE 18 AND OLDER, SO YOU CAN&apos;T CONTINUE.
          </h1>
          <p className="p-16" style={{ maxWidth: 680 }}>NOTHING WAS SAVED ABOUT YOU. YOU CAN CLOSE THIS TAB.</p>
        </main>
        <Footer />
      </div>
    );
  }

  if (step === 'slides') {
    const last = slide === 2;
    return (
      <div className="page">
        <TopBar
          crumb="FIRST VISIT"
          showOnline={false}
          back={{ label: '← BACK' }}
          onBack={() => (slide === 0 ? setStep('age') : setSlide(slide - 1))}
        />
        <main className="main" style={{ display: 'flex', flexDirection: 'column', gap: 48 }}>
          <div className="eyebrow">[ 2/3 ] HOW THIS WORKS · {slide + 1} OF 3</div>
          <Slide i={slide} />
          <div className="slide-foot">
            <div className="dots" aria-hidden="true">
              {[0, 1, 2].map((k) => <span key={k} className={k === slide ? 'on' : ''} />)}
            </div>
            <div style={{ display: 'flex', gap: 12 }}>
              <button type="button" className="btn dim" style={{ width: 140 }} onClick={afterSlides}>
                [ SKIP ]
              </button>
              <button type="button" className="btn solid" style={{ width: 240 }} onClick={() => (last ? afterSlides() : setSlide(slide + 1))}>
                {last ? '[ GET STARTED → ]' : '[ NEXT → ]'}
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // mode
  return (
    <div className="page">
      <TopBar crumb="FIRST VISIT" back={{ label: '← BACK' }} onBack={() => setStep('slides')} />
      <main className="main" style={{ display: 'flex', flexDirection: 'column', gap: 44 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div className="eyebrow">[ 3/3 ] CHOOSE HOW TO ENTER</div>
          <h1 className="h-30">WHAT ARE YOU HERE FOR?<span className="cursor">_</span></h1>
          <p className="dim" style={{ fontSize: 14 }}>YOU CAN SWITCH BETWEEN THESE ANYTIME FROM THE LOBBY.</p>
        </div>
        <div className="modes">
          <ModeCard no="01" meta="25 THEMED ROOMS" title="VOICE ROOMS" onClick={() => onDone('/rooms')}
            text={<>UP TO 10 PEOPLE. YOU JOIN AS A LISTENER.<br />RAISE YOUR HAND WHEN YOU WANT TO SPEAK.</>} />
          <ModeCard no="02" meta="NO FILTERS" title="1:1 CHAT" onClick={() => onDone('/chat')}
            text={<>ONE RANDOM STRANGER. TEXT FIRST.<br />VOICE ONLY IF YOU BOTH SAY YES.</>} />
        </div>
      </main>
      <Footer />
    </div>
  );
}

export function ModeCard({ no, meta, title, text, onClick, href }) {
  const inner = (
    <>
      <div className="top"><span>[{no}]</span><span>{meta}</span></div>
      <div className="title">{title}</div>
      <div className="bottom"><span className="dim">{text}</span><span>ENTER →</span></div>
    </>
  );
  if (href) return <Link href={href} className="mode">{inner}</Link>;
  return (
    <button type="button" className="mode" onClick={onClick} style={{ background: 'transparent', color: 'var(--fg)', textAlign: 'left', font: 'inherit' }}>
      {inner}
    </button>
  );
}

function Slide({ i }) {
  if (i === 0) {
    return (
      <div className="slide">
        <div className="split-lead" style={{ maxWidth: 680, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 28 }}>
          <div className="num">01</div>
          <h1>FULLY ANONYMOUS.</h1>
          <p className="p-18">NO ACCOUNTS. NO LOGIN. NO HISTORY THAT FOLLOWS YOU. YOU GET A NEW DISPOSABLE NAME EVERY TIME YOU JOIN, AND CONVERSATIONS DISAPPEAR WHEN YOU LEAVE.</p>
        </div>
        <div aria-hidden="true" className="names nc">
          <span style={{ color: 'var(--fg-4)' }}>faint_wren_19</span>
          <span style={{ color: 'var(--fg-3)' }}>static_echo_03</span>
          <span>quiet_otter_42 ←</span>
          <span style={{ color: 'var(--fg-3)' }}>rogue_comet_77</span>
          <span style={{ color: 'var(--fg-4)' }}>pale_lynx_11</span>
        </div>
      </div>
    );
  }
  if (i === 1) {
    return (
      <div className="slide">
        <div style={{ maxWidth: 680, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 28 }}>
          <div className="num">02</div>
          <h1>TWO WAYS TO TALK.</h1>
          <p className="p-18">JOIN A THEMED VOICE ROOM WITH UP TO 10 PEOPLE, OR GET MATCHED 1:1 WITH A RANDOM STRANGER FOR A TEXT CHAT. YOU CAN SWITCH ANYTIME.</p>
        </div>
        <dl aria-hidden="true" className="kv" style={{ alignSelf: 'center', gridTemplateColumns: '180px 1fr', rowGap: 18 }}>
          <dt className="dim3">VOICE ROOMS</dt><dd>YOU START AS A LISTENER.<br />RAISE YOUR HAND TO SPEAK.</dd>
          <dt className="dim3">1:1 CHAT</dt><dd>TEXT FIRST. VOICE ONLY IF<br />YOU BOTH SAY YES.</dd>
        </dl>
      </div>
    );
  }
  return (
    <div className="slide">
      <div style={{ maxWidth: 680, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 28 }}>
        <div className="num">03</div>
        <h1>KEEP IT RESPECTFUL.</h1>
        <p className="p-18">A REPORT BUTTON IS ALWAYS ONE CLICK AWAY. WHEN ENOUGH PEOPLE REPORT SOMEONE, THEY&apos;RE REMOVED AUTOMATICALLY. NO WAITING ON A MOD.</p>
      </div>
      <dl aria-hidden="true" className="kv" style={{ alignSelf: 'center', gridTemplateColumns: '200px 1fr' }}>
        <dt className="dim3">FIRST TWO IN A ROOM</dt><dd>BECOME ITS MODS</dd>
        <dt className="dim3">2:30 ON STAGE</dt><dd>MAKES YOU A MOD</dd>
        <dt className="dim3">A MOD LEAVES</dt><dd>NEXT SPEAKER STEPS UP</dd>
        <dt className="dim3">ENOUGH REPORTS</dt><dd>YOU&apos;RE OUT</dd>
      </dl>
    </div>
  );
}

function Boot({ onEnter }) {
  return (
    <div className="boot">
      <h1 className="sr">Wisp: talk to strangers anonymously in voice rooms or random 1:1 chat</h1>
      <div className="wake"><Rabbit className="rabbit-xl" label="Wisp rabbit, waking up" /></div>
      <div role="log" aria-label="Boot sequence" className="log">
        <div className="ln dim" style={{ animationDelay: '1.4s' }}>WISP · WAKING UP FROM NOTHING</div>
        {[
          ['ACCOUNTS', 'NONE', '1.9s'],
          ['HISTORY', 'NONE', '2.3s'],
          ['MEMORY', 'RAM ONLY', '2.7s']
        ].map(([k, v, d]) => (
          <div key={k} className="ln row" style={{ animationDelay: d }}>
            <span className="k">&gt; {k}</span><span className="fill" /><span>{v}</span>
          </div>
        ))}
        <div className="ln row" style={{ animationDelay: '3.1s' }}>
          <span className="k">&gt; KEEPER</span><span className="fill" /><span className="nc">Damn_It_Rabbit</span>
        </div>
        <div className="ln dim" style={{ animationDelay: '3.6s' }}>READY.<span className="cursor" style={{ color: 'var(--fg)' }}>_</span></div>
      </div>
      <button type="button" className="ln enter" style={{ animationDelay: '4s' }} onClick={onEnter}>
        [ ENTER ]
      </button>
      <div className="foot">
        <span>ANONYMOUS VOICE ROOMS + 1:1 CHAT WITH STRANGERS · 18+ ONLY</span>
        <span>© 2026 WISP · <span className="nc">Damn_It_Rabbit</span></span>
      </div>
    </div>
  );
}
