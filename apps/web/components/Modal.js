'use client';
import { useEffect, useRef } from 'react';

export default function Modal({ label, children, onEscape }) {
  const ref = useRef(null);
  useEffect(() => {
    const prev = document.activeElement;
    (ref.current?.querySelector('[data-autofocus]') ?? ref.current?.querySelector('button, a, input'))?.focus();
    const onKey = (e) => {
      if (e.key === 'Escape' && onEscape) onEscape();
      if (e.key === 'Tab' && ref.current) {
        const els = [...ref.current.querySelectorAll('button, a, input')];
        if (!els.length) return;
        const first = els[0], last = els[els.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('keydown', onKey);
      prev?.focus?.();
    };
  }, [onEscape]);
  return (
    <div className="scrim">
      <div ref={ref} className="modal" role="alertdialog" aria-modal="true" aria-label={label}>
        {children}
      </div>
    </div>
  );
}
