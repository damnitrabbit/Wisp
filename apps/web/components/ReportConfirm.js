'use client';
import Modal from './Modal';

// A report is a real action against a real person, so it always asks first.
// Cancel has focus, so an accidental Enter or click does nothing.
export default function ReportConfirm({ name, where = 'room', onConfirm, onCancel }) {
  return (
    <Modal label={`Report ${name}`} onEscape={onCancel}>
      <div className="head" style={{ justifyContent: 'flex-start', alignItems: 'center', gap: 12 }}>
        <span className="tagbox">[ REPORT ]</span>
        <span>ANONYMOUS · ONE PER PERSON</span>
      </div>
      <h1>
        REPORT <span className="nc">{name}</span>?
      </h1>
      <dl className="kv" style={{ gridTemplateColumns: '150px 1fr', rowGap: 12 }}>
        <dt>USE IT FOR</dt>
        <dd>HARASSMENT, HATE, UNWANTED SEXUAL STUFF, SPAM. NOT FOR DISAGREEING.</dd>
        <dt>WHAT HAPPENS</dt>
        <dd>
          {where === 'room'
            ? 'WHEN ENOUGH PEOPLE IN THIS ROOM REPORT THEM, THEY’RE REMOVED AUTOMATICALLY. MODS INCLUDED.'
            : where === 'echo'
              ? 'THREE REPORTS FROM DIFFERENT PEOPLE TAKE IT DOWN FOR EVERYONE, RIGHT AWAY.'
              : 'THIS CHAT ENDS RIGHT AWAY. THREE REPORTS FROM DIFFERENT PEOPLE REMOVE SOMEONE FROM MATCHMAKING.'}
        </dd>
        <dt>WHO KNOWS</dt>
        <dd>{where === 'echo' ? 'NOBODY. IT’S ANONYMOUS.' : 'NOBODY. THEY WON’T SEE THAT IT WAS YOU.'}</dd>
      </dl>
      <div className="two">
        <button type="button" className="btn solid tall" onClick={onConfirm}>
          [ ! ] YES, REPORT
        </button>
        <button type="button" className="btn tall" data-autofocus onClick={onCancel}>
          CANCEL
        </button>
      </div>
    </Modal>
  );
}
