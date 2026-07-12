import { useEffect, type ReactNode } from 'react';
import { CloseIcon } from './Icons';
import { IconButton } from './IconButton';

export function Sheet({ open, title, onClose, children, footer }: { open: boolean; title: string; onClose: () => void; children: ReactNode; footer?: ReactNode }) {
  useEffect(() => {
    document.body.classList.toggle('sheet-open', open);
    return () => document.body.classList.remove('sheet-open');
  }, [open]);
  if (!open) return null;
  return <div className="sheet-layer" role="dialog" aria-modal="true" aria-label={title}><button className="sheet-layer__backdrop" onClick={onClose} aria-label="Закрити"/><section className="sheet"><header><h2>{title}</h2><IconButton onClick={onClose} aria-label="Закрити"><CloseIcon/></IconButton></header><div className="sheet__content">{children}</div>{footer ? <footer className="sheet__footer">{footer}</footer> : null}</section></div>;
}
