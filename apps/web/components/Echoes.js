'use client';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { LIMITS, ECHO_TAGS, ECHO_REACTIONS } from '@wisp/shared';
import TopBar from './TopBar';
import Footer from './Footer';
import ReportConfirm from './ReportConfirm';
import { emit, on, toast, useWisp } from '@/lib/wisp';
import { useNow } from '@/lib/time';
import { heard, mine, newTicket, timeLeft, secs, useRecorder, usePlayer } from '@/lib/echoes';

const TAG_LABEL = { confession: 'CONFESSION', question: 'QUESTION', rant: 'RANT', advice: 'NEED ADVICE' };
const REACTION_LABEL = { felt: 'FELT THIS', same: 'SAME', strength: 'SENDING STRENGTH' };
const MAX_S = LIMITS.ECHO_MAX_SECONDS;

const ERROR_COPY = {
  cooldown: (r) => `ONE NOTE EVERY FEW MINUTES. TRY AGAIN IN ${secsOrMins(r?.retryInMs)}.`,
  too_long: () => 'THAT’S TOO LONG.',
  empty: () => 'NOTHING RECORDED. TRY AGAIN.',
  full: () => 'THIS NOTE HAS BEEN HEARD ENOUGH. NO MORE REPLIES.',
  not_found: () => 'THAT NOTE HAS FADED.',
  not_allowed: () => 'THIS ONE IS JUST FOR LISTENING.',
  offline: () => 'YOU’RE OFFLINE. TRY AGAIN IN A MOMENT.',
  timeout: () => 'THAT TOOK TOO LONG. TRY AGAIN.'
};
const secsOrMins = (ms = 0) => (ms > 60_000 ? `${Math.ceil(ms / 60_000)} MIN` : `${Math.ceil(ms / 1000)}S`);
const errText = (r) => (ERROR_COPY[r?.error] ?? (() => 'SOMETHING WENT WRONG. TRY AGAIN.'))(r);

// Order for one viewer: notes you haven't heard, then notes nobody has answered yet, then newest.
function order(notes, heardIds, mineIds) {
  const rank = (n) => (!heardIds.has(n.id) && !mineIds.has(n.id) ? 0 : n.replyCount === 0 && !n.listenOnly ? 1 : 2);
  return [...notes].sort((a, b) => rank(a) - rank(b) || b.createdAt - a.createdAt);
}

export default function Echoes() {
  const status = useWisp((s) => s.status);
  const [notes, setNotes] = useState(null);
  const [skew, setSkew] = useState(0);
  const [heardMap, setHeardMap] = useState({});
  const [mineMap, setMineMap] = useState({});
  const [orderIds, setOrderIds] = useState([]);
  const [open, setOpen] = useState(null);
  const [thread, setThread] = useState(null);
  const [reporting, setReporting] = useState(null); // { id, replyId? }
  const player = usePlayer();
  const now = useNow(true, 30_000) + skew;
  const openRef = useRef(null);
  openRef.current = open;

  const loadThread = useCallback(async (id) => {
    const r = await emit('echoes:thread', { id });
    if (r?.ok) {
      setThread(r);
      if (mine.all()[id]) {
        mine.seen(id, r.replies.length);
        setMineMap(mine.all());
      }
    } else if (r?.error === 'not_found') {
      setThread(null);
      setOpen(null);
    }
  }, []);

  const load = useCallback(async ({ reorder = false } = {}) => {
    const r = await emit('echoes:list');
    if (!r?.ok) return;
    setSkew(r.now - Date.now());
    setNotes(r.notes);
    const h = heard.all();
    const m = mine.all();
    setHeardMap(h);
    setMineMap(m);
    // Keep the order steady while someone is listening; new notes go on top, the rest re-sort on demand.
    setOrderIds((prev) => {
      const sorted = order(r.notes, new Set(Object.keys(h)), new Set(Object.keys(m))).map((n) => n.id);
      if (reorder || prev.length === 0) return sorted;
      const known = new Set(prev);
      const fresh = sorted.filter((id) => !known.has(id));
      const alive = new Set(sorted);
      return [...fresh, ...prev.filter((id) => alive.has(id))];
    });
    if (openRef.current) loadThread(openRef.current);
  }, [loadThread]);

  useEffect(() => {
    if (status === 'online') load({ reorder: true });
  }, [status, load]);

  useEffect(() => {
    let t = null;
    const off = on('echoes:changed', () => {
      clearTimeout(t);
      t = setTimeout(() => load(), 300);
    });
    return () => {
      off();
      clearTimeout(t);
    };
  }, [load]);

  const byId = useMemo(() => new Map((notes ?? []).map((n) => [n.id, n])), [notes]);
  const list = orderIds.map((id) => byId.get(id)).filter(Boolean);
  const newCount = list.filter((n) => !heardMap[n.id] && !mineMap[n.id]).length;

  const playNote = async (n) => {
    const started = await player.toggle(n.id, () => emit('echoes:audio', { id: n.id }, 15000));
    if (started && !heardMap[n.id]) {
      heard.add(n.id, n.expiresAt);
      setHeardMap(heard.all());
    }
  };

  const toggleThread = (id) => {
    if (open === id) {
      setOpen(null);
      setThread(null);
      return;
    }
    setOpen(id);
    setThread(null);
    loadThread(id);
  };

  const react = async (n, reaction) => {
    const r = await emit('echoes:react', { id: n.id, reaction });
    if (r?.ok) setNotes((all) => all.map((x) => (x.id === n.id ? r.note : x)));
  };

  const confirmReport = async () => {
    const target = reporting;
    setReporting(null);
    const r = await emit('echoes:report', target);
    if (r?.ok) {
      toast({ tag: '[ REPORTED ]', text: r.removed ? 'THANK YOU. IT’S BEEN TAKEN DOWN.' : 'THANK YOU. ENOUGH REPORTS TAKE IT DOWN FOR EVERYONE.', ttl: 5000, key: 'echo-report' });
      load();
    }
  };

  const removeNote = async (n) => {
    const t = mine.all()[n.id];
    if (!t) return;
    const r = await emit('echoes:delete', { id: n.id, ticket: t.ticket });
    if (r?.ok || r?.error === 'not_found') {
      mine.remove(n.id);
      if (open === n.id) toggleThread(n.id);
      load();
    }
  };

  const removeReply = async (noteId, replyId) => {
    const t = mine.all()[noteId];
    if (!t) return;
    const r = await emit('echoes:deleteReply', { id: noteId, replyId, ticket: t.ticket });
    if (r?.ok) loadThread(noteId);
  };

  const posted = (id, ticket, exp) => {
    mine.add(id, ticket, exp);
    heard.add(id, exp);
    load();
  };

  return (
    <div className="page">
      <TopBar crumb="/ECHOES" back={{ label: '← LOBBY', href: '/' }} />
      <main className="main echoes">
        <section className="ec-intro" aria-label="Leave a note">
          <h1 className="h-30">
            SAY IT OUT LOUD. NOBODY KNOWS IT&apos;S YOU.<span className="cursor">_</span>
          </h1>
          <p className="p-16">
            LEAVE A VOICE NOTE ON THE WALL. STRANGERS CAN LISTEN, REACT AND, IF YOU LET THEM, ANSWER. SAY IT, THEN LEAVE. EVERYTHING FADES IN 24 HOURS.
          </p>
          <dl className="kv" style={{ gridTemplateColumns: '150px 1fr' }}>
            <dt>YOUR NAME</dt>
            <dd>NONE. NOT EVEN A FAKE ONE.</dd>
            <dt>LENGTH</dt>
            <dd>UP TO {MAX_S} SECONDS.</dd>
            <dt>KEPT</dt>
            <dd>24 HOURS, IN MEMORY. THEN GONE.</dd>
          </dl>
          <Recorder onPosted={posted} />
          <p className="ec-support">
            NOT OKAY RIGHT NOW? TALK TO A PERSON. IN INDIA: TELE-MANAS <a href="tel:14416">14416</a> (FREE, 24/7). ANYWHERE ELSE:{' '}
            <a href="https://findahelpline.com" target="_blank" rel="noopener noreferrer" className="nc">findahelpline.com</a>
          </p>
        </section>

        <section className="ec-wall" aria-label="The wall">
          <div className="ec-head">
            <span>
              THE WALL · {notes ? list.length : '—'} {list.length === 1 ? 'NOTE' : 'NOTES'}
              {newCount > 0 && <> · <span style={{ color: 'var(--fg)' }}>{newCount} NEW FOR YOU</span></>}
            </span>
            <button type="button" className="linkish" onClick={() => load({ reorder: true })}>
              ↻ REFRESH
            </button>
          </div>
          {notes && list.length === 0 && (
            <div className="quiet" role="status">
              <span>THE WALL IS EMPTY. BE THE FIRST TO SAY SOMETHING.</span>
            </div>
          )}
          {list.map((n) => (
            <Note
              key={n.id}
              n={n}
              now={now}
              isNew={!heardMap[n.id] && !mineMap[n.id]}
              mineInfo={mineMap[n.id]}
              open={open === n.id}
              thread={open === n.id ? thread : null}
              player={player}
              onPlay={() => playNote(n)}
              onToggle={() => toggleThread(n.id)}
              onReact={(r) => react(n, r)}
              onReport={(replyId) => setReporting(replyId ? { id: n.id, replyId } : { id: n.id })}
              onRemove={() => removeNote(n)}
              onRemoveReply={(replyId) => removeReply(n.id, replyId)}
              onReplied={() => loadThread(n.id)}
            />
          ))}
        </section>
      </main>
      <Footer />
      {reporting && (
        <ReportConfirm name={reporting.replyId ? 'THIS REPLY' : 'THIS NOTE'} where="echo" onConfirm={confirmReport} onCancel={() => setReporting(null)} />
      )}
    </div>
  );
}

// ---------- posting ----------

function Recorder({ onPosted }) {
  const r = useRecorder(MAX_S);
  const preview = usePlayer();
  const [tag, setTag] = useState(null);
  const [listenOnly, setListenOnly] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);

  const post = async () => {
    if (!r.clip || !tag || listenOnly === null) return;
    setBusy(true);
    setError('');
    const ticket = newTicket();
    const res = await emit(
      'echoes:post',
      { audio: await r.clip.blob.arrayBuffer(), mime: r.clip.mime, duration: r.clip.duration, tag, ticket, listenOnly },
      20000
    );
    setBusy(false);
    if (!res?.ok) return setError(errText(res));
    preview.stopAll();
    onPosted(res.id, ticket, res.expiresAt);
    r.reset();
    setTag(null);
    setListenOnly(null);
    setDone(true);
  };

  const again = () => {
    setDone(false);
    setError('');
    r.start();
  };

  // [ R ] starts and stops a recording, like the other bracketed keys on the site.
  useEffect(() => {
    const onKey = (e) => {
      if (e.key.toLowerCase() !== 'r' || e.metaKey || e.ctrlKey || e.altKey) return;
      if (['INPUT', 'TEXTAREA'].includes(e.target.tagName) || document.querySelector('[role="dialog"]')) return;
      if (r.state === 'recording') r.stop();
      else if (r.state === 'idle') (done ? again() : r.start());
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  return (
    <div className="ec-rec box">
      <div className="eyebrow">[ YOUR NOTE ]</div>

      {done && r.state === 'idle' && (
        <>
          <p className="ec-big">ON THE WALL. IT FADES IN 24 HOURS.</p>
          <p className="dim">YOU CAN LEAVE NOW. IF YOU COME BACK ON THIS BROWSER, YOUR NOTE SAYS HOW MANY PEOPLE ANSWERED.</p>
          <button type="button" className="btn tall" onClick={again}>[ R ] RECORD ANOTHER</button>
        </>
      )}

      {!done && (r.state === 'idle' || r.state === 'asking') && (
        <>
          <button type="button" className="btn solid tall spread" onClick={r.start} disabled={r.state === 'asking'}>
            <span>{r.state === 'asking' ? 'ALLOW THE MIC IN YOUR BROWSER…' : '[ R ] START RECORDING'}</span>
            <span>●</span>
          </button>
          <p className="ec-help">UP TO {MAX_S} SECONDS. YOU&apos;LL HEAR IT BACK BEFORE ANYTHING IS POSTED.</p>
        </>
      )}

      {r.state === 'recording' && (
        <>
          <div className="ec-recording" role="status">
            <span className="dot pulse" /> RECORDING <span className="nc">{secs(r.elapsed)}</span> / {secs(MAX_S)}
          </div>
          <div className="ec-bar"><i style={{ width: `${Math.min(100, (r.elapsed / MAX_S) * 100)}%` }} /></div>
          <button type="button" className="btn solid tall spread" onClick={r.stop}>
            <span>[ ■ ] STOP</span>
            <span>{secs(MAX_S - r.elapsed)} LEFT</span>
          </button>
        </>
      )}

      {(r.state === 'denied' || r.state === 'unsupported') && (
        <>
          <p className="ec-big">
            {r.state === 'denied' ? 'THE MIC IS BLOCKED.' : 'THIS BROWSER CAN’T RECORD AUDIO.'}
          </p>
          <p className="dim">
            {r.state === 'denied'
              ? 'ALLOW MICROPHONE ACCESS FOR THIS SITE IN YOUR BROWSER SETTINGS, THEN TRY AGAIN. YOU CAN STILL LISTEN AND REPLY BY TEXT.'
              : 'TRY A RECENT CHROME, SAFARI OR FIREFOX. YOU CAN STILL LISTEN AND REPLY BY TEXT.'}
          </p>
          <button type="button" className="btn tall" onClick={r.reset}>TRY AGAIN</button>
        </>
      )}

      {r.state === 'done' && r.clip && (
        <>
          <div className="ec-play">
            <button type="button" className="ctl" onClick={() => preview.toggle('preview', r.clip.url)} aria-label="Play your recording">
              {preview.playing === 'preview' ? '[ ■ ]' : '[ ▶ ]'}
            </button>
            <div className="ec-bar"><i style={{ width: `${preview.playing === 'preview' ? preview.progress * 100 : 0}%` }} /></div>
            <span className="dim">{secs(r.clip.duration)}</span>
          </div>
          <button type="button" className="linkish" onClick={() => { preview.stopAll(); r.reset(); }}>
            ↺ SCRAP IT AND RECORD AGAIN
          </button>

          <fieldset className="ec-field">
            <legend>WHAT IS IT?</legend>
            <div className="ec-chips">
              {ECHO_TAGS.map((t) => (
                <button key={t} type="button" className={`ec-chip ${tag === t ? 'on' : ''}`} aria-pressed={tag === t} onClick={() => setTag(t)}>
                  {TAG_LABEL[t]}
                </button>
              ))}
            </div>
          </fieldset>

          <fieldset className="ec-field">
            <legend>WHAT DO YOU WANT BACK?</legend>
            <div className="ec-chips">
              <button type="button" className={`ec-chip tall ${listenOnly === true ? 'on' : ''}`} aria-pressed={listenOnly === true} onClick={() => setListenOnly(true)}>
                JUST LISTEN<span>REACTIONS ONLY</span>
              </button>
              <button type="button" className={`ec-chip tall ${listenOnly === false ? 'on' : ''}`} aria-pressed={listenOnly === false} onClick={() => setListenOnly(false)}>
                OPEN TO REPLIES<span>VOICE OR TEXT, UP TO {LIMITS.ECHO_MAX_REPLIES}</span>
              </button>
            </div>
          </fieldset>

          <button type="button" className="btn solid tall spread" onClick={post} disabled={busy || !tag || listenOnly === null}>
            <span>{busy ? 'POSTING…' : '[ ↑ ] PUT IT ON THE WALL'}</span>
            <span>→</span>
          </button>
          <p className="ec-help">NO NAME IS ATTACHED. THE AUDIO SITS IN SERVER MEMORY FOR 24 HOURS, THEN IT&apos;S DELETED. IT&apos;S NEVER SAVED TO DISK.</p>
        </>
      )}

      {error && <p className="ec-error" role="alert">{error}</p>}
    </div>
  );
}

// ---------- one note on the wall ----------

function Note({ n, now, isNew, mineInfo, open, thread, player, onPlay, onToggle, onReact, onReport, onRemove, onRemoveReply, onReplied }) {
  const [confirmDelete, setConfirmDelete] = useState(false);
  const age = Math.max(0, Math.min(1, (now - n.createdAt) / (n.expiresAt - n.createdAt)));
  const opacity = 1 - age * 0.55; // fades as the day passes
  const playing = player.playing === n.id;
  const unseenReplies = mineInfo ? Math.max(0, n.replyCount - (mineInfo.seen ?? 0)) : 0;
  const repliesLabel = n.listenOnly ? 'JUST LISTENING' : n.replyCount === 0 ? 'NO REPLIES YET' : `${n.replyCount} ${n.replyCount === 1 ? 'REPLY' : 'REPLIES'}`;

  return (
    <article className={`ec-note ${isNew ? 'new' : ''} ${open ? 'open' : ''}`} style={{ opacity }} aria-label={`${TAG_LABEL[n.tag]} note`}>
      <div className="ec-top">
        {isNew && <span className="tagbox ec-new">NEW</span>}
        {mineInfo && <span className="ec-mine">YOURS</span>}
        <span>{TAG_LABEL[n.tag]}</span>
        <span className="grow" />
        <span className="dim3">{timeLeft(n.expiresAt - now)}</span>
      </div>

      <div className="ec-play">
        <button type="button" className={`ctl ${playing ? 'on' : ''}`} onClick={onPlay} aria-label={playing ? 'Stop' : 'Play note'}>
          {playing ? '[ ■ ]' : '[ ▶ ]'}
        </button>
        <div className="ec-bar"><i style={{ width: `${playing ? player.progress * 100 : 0}%` }} /></div>
        <span className="dim">{secs(n.duration)}</span>
      </div>

      <div className="ec-actions">
        {ECHO_REACTIONS.map((r) => (
          <button key={r} type="button" className={`ctl ${n.myReaction === r ? 'on' : ''}`} aria-pressed={n.myReaction === r} onClick={() => onReact(r)}>
            {REACTION_LABEL[r]}
            {n.reactions[r] > 0 && <span className="ec-count">{n.reactions[r]}</span>}
          </button>
        ))}
        <span className="grow" />
        <button type="button" className={`ctl ${open ? 'on' : ''}`} onClick={onToggle} aria-expanded={open}>
          {repliesLabel}
          {unseenReplies > 0 && <span className="ec-count hot">{unseenReplies} NEW</span>}
          <span aria-hidden="true"> {open ? '↑' : '↓'}</span>
        </button>
        {mineInfo ? (
          confirmDelete ? (
            <button type="button" className="ctl on" onClick={onRemove}>SURE? DELETE</button>
          ) : (
            <button type="button" className="ctl" onClick={() => setConfirmDelete(true)}>DELETE</button>
          )
        ) : (
          <button type="button" className="ctl" onClick={() => onReport()} disabled={n.reported} aria-label="Report this note">
            {n.reported ? 'REPORTED' : '[ ! ]'}
          </button>
        )}
      </div>

      {open && (
        <Thread
          n={n}
          thread={thread}
          isMine={!!mineInfo}
          player={player}
          onReport={onReport}
          onRemoveReply={onRemoveReply}
          onReplied={onReplied}
        />
      )}
    </article>
  );
}

function Thread({ n, thread, isMine, player, onReport, onRemoveReply, onReplied }) {
  if (!thread) return <div className="ec-thread dim">LOADING…</div>;
  const replies = thread.replies;
  const canReply = !n.listenOnly && replies.length < LIMITS.ECHO_MAX_REPLIES && !isMine;
  return (
    <div className="ec-thread">
      {replies.length === 0 && (
        <p className="dim3">{n.listenOnly ? 'THEY JUST WANTED TO BE HEARD. A REACTION IS ENOUGH.' : 'NOBODY HAS ANSWERED YET.'}</p>
      )}
      {replies.map((r) => {
        const key = `${n.id}:${r.id}`;
        const playing = player.playing === key;
        return (
          <div key={r.id} className="ec-reply">
            {r.kind === 'voice' ? (
              <div className="ec-play">
                <button type="button" className={`ctl ${playing ? 'on' : ''}`} onClick={() => player.toggle(key, () => emit('echoes:audio', { id: n.id, replyId: r.id }, 15000))} aria-label="Play reply">
                  {playing ? '[ ■ ]' : '[ ▶ ]'}
                </button>
                <div className="ec-bar"><i style={{ width: `${playing ? player.progress * 100 : 0}%` }} /></div>
                <span className="dim">{secs(r.duration)}</span>
              </div>
            ) : (
              <p className="nc ec-text">{r.text}</p>
            )}
            {isMine ? (
              <button type="button" className="ctl" onClick={() => onRemoveReply(r.id)} aria-label="Remove this reply">[ X ]</button>
            ) : (
              <button type="button" className="ctl" onClick={() => onReport(r.id)} disabled={r.reported} aria-label="Report this reply">
                {r.reported ? 'REPORTED' : '[ ! ]'}
              </button>
            )}
          </div>
        );
      })}
      {isMine && replies.length > 0 && <p className="ec-help">IT&apos;S YOUR NOTE: YOU CAN REMOVE ANY REPLY YOU DON&apos;T WANT HERE.</p>}
      {canReply && <ReplyBox id={n.id} onReplied={onReplied} />}
      {!n.listenOnly && !isMine && replies.length >= LIMITS.ECHO_MAX_REPLIES && <p className="dim3">THIS ONE HAS BEEN HEARD. NO MORE REPLIES.</p>}
    </div>
  );
}

function ReplyBox({ id, onReplied }) {
  const r = useRecorder(MAX_S);
  const preview = usePlayer();
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const send = async (payload) => {
    setBusy(true);
    setError('');
    const res = await emit('echoes:reply', { id, ...payload }, 20000);
    setBusy(false);
    if (!res?.ok) return setError(errText(res));
    setText('');
    preview.stopAll();
    r.reset();
    onReplied();
  };

  const sendVoice = async () => r.clip && send({ audio: await r.clip.blob.arrayBuffer(), mime: r.clip.mime, duration: r.clip.duration });
  const sendText = (e) => {
    e.preventDefault();
    if (text.trim()) send({ text });
  };

  return (
    <div className="ec-replybox">
      {r.state === 'recording' ? (
        <div className="ec-play">
          <button type="button" className="ctl on" onClick={r.stop}>[ ■ ] STOP</button>
          <div className="ec-bar"><i style={{ width: `${Math.min(100, (r.elapsed / MAX_S) * 100)}%` }} /></div>
          <span className="dim">{secs(r.elapsed)}</span>
        </div>
      ) : r.state === 'done' && r.clip ? (
        <div className="ec-play">
          <button type="button" className="ctl" onClick={() => preview.toggle('reply-preview', r.clip.url)}>
            {preview.playing === 'reply-preview' ? '[ ■ ]' : '[ ▶ ]'} {secs(r.clip.duration)}
          </button>
          <button type="button" className="ctl" onClick={() => { preview.stopAll(); r.reset(); }}>SCRAP</button>
          <button type="button" className="ctl on" onClick={sendVoice} disabled={busy}>{busy ? 'SENDING…' : 'SEND VOICE REPLY →'}</button>
        </div>
      ) : (
        <form className="ec-compose" onSubmit={sendText}>
          <button type="button" className="ctl" onClick={r.start} disabled={r.state === 'asking'} aria-label="Record a voice reply">
            ● VOICE
          </button>
          <input
            className="ec-input nc"
            value={text}
            maxLength={LIMITS.ECHO_TEXT_MAX}
            onChange={(e) => setText(e.target.value)}
            placeholder="OR TYPE A REPLY"
            aria-label="Reply in text"
          />
          <button type="submit" className="ctl" disabled={busy || !text.trim()}>SEND</button>
        </form>
      )}
      {(r.state === 'denied' || r.state === 'unsupported') && <p className="ec-error">MIC NOT AVAILABLE. YOU CAN STILL REPLY BY TEXT.</p>}
      {error && <p className="ec-error" role="alert">{error}</p>}
    </div>
  );
}
