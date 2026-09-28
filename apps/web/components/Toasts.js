'use client';
import { useWisp, dismiss } from '@/lib/wisp';

export default function Toasts() {
  const toasts = useWisp((s) => s.toasts);
  return (
    <div className="toast-slot" aria-live="polite">
      {toasts.map((t) => (
        <div key={t.id} role="status" className={`toast ${t.kind}`}>
          <span className="tag">
            {t.pulse && <span className="dot pulse" style={{ background: '#000' }} />}
            {t.tag}
          </span>
          <span className="txt">{t.text}</span>
          {t.sticky ? <span /> : (
            <button type="button" aria-label="Dismiss" onClick={() => dismiss(t.id)}>
              [ X ]
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
