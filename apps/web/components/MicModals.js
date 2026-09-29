'use client';
import Modal from './Modal';

// where: 'room' | 'call'
export default function MicModals({ flow, where = 'room' }) {
  if (flow.modal === 'ask') {
    return (
      <Modal label="Microphone" onEscape={flow.decline}>
        <div className="head">
          <span>{where === 'room' ? 'BEFORE YOU GO ON STAGE' : 'BEFORE VOICE STARTS'}</span>
          <span>ONE-TIME</span>
        </div>
        <h1>
          NOTRACE NEEDS YOUR MICROPHONE.<span className="cursor">_</span>
        </h1>
        <dl className="kv" style={{ gridTemplateColumns: '160px 1fr', rowGap: 12 }}>
          <dt>NEXT</dt>
          <dd>YOUR BROWSER WILL ASK. PICK ALLOW.</dd>
          <dt>YOUR AUDIO</dt>
          <dd>{where === 'room' ? 'GOES STRAIGHT TO THE PEOPLE IN THIS ROOM. NEVER THROUGH US.' : 'GOES STRAIGHT TO THE OTHER PERSON. NEVER THROUGH US.'}</dd>
          <dt>RECORDED</dt>
          <dd>NEVER.</dd>
        </dl>
        <div className="two">
          <button type="button" className="btn solid tall" onClick={flow.allow}>
            [ Y ] ALLOW MIC →
          </button>
          <button type="button" className="btn tall" onClick={flow.decline}>
            {where === 'room' ? '[ N ] STAY A LISTENER' : '[ N ] STAY IN TEXT'}
          </button>
        </div>
      </Modal>
    );
  }
  if (flow.modal === 'blocked') {
    return (
      <Modal label="Microphone blocked" onEscape={flow.decline}>
        <div className="head" style={{ justifyContent: 'flex-start', alignItems: 'center', gap: 12 }}>
          <span className="tagbox">[ MIC BLOCKED ]</span>
          <span>{where === 'room' ? 'YOU CAN STILL LISTEN AND TYPE' : 'YOU CAN STILL TEXT'}</span>
        </div>
        <h1>YOUR BROWSER BLOCKED THE MIC.</h1>
        <ol style={{ padding: 0, listStyle: 'none', display: 'grid', gridTemplateColumns: '40px 1fr', rowGap: 14, fontSize: 13, lineHeight: 1.5 }}>
          <li style={{ display: 'contents' }}><span className="dim3">01</span><span>TAP THE LOCK ICON LEFT OF THE ADDRESS BAR.</span></li>
          <li style={{ display: 'contents' }}><span className="dim3">02</span><span>SET MICROPHONE TO ALLOW.</span></li>
          <li style={{ display: 'contents' }}><span className="dim3">03</span><span>COME BACK HERE AND TRY AGAIN.</span></li>
        </ol>
        <div className="two">
          <button type="button" className="btn solid tall" onClick={flow.allow}>
            [ TRY AGAIN ]
          </button>
          <button type="button" className="btn tall" onClick={flow.decline}>
            {where === 'room' ? '[ KEEP LISTENING ]' : '[ STAY IN TEXT ]'}
          </button>
        </div>
      </Modal>
    );
  }
  return null;
}
