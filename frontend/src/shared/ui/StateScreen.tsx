import type { ReactNode } from 'react';
import { Button } from './Button';

export function StateScreen({ title, description, actionLabel, onAction, icon }: { title: string; description: string; actionLabel?: string; onAction?: () => void; icon?: ReactNode }) {
  return <div className="state-screen">{icon ? <div className="state-screen__icon">{icon}</div> : null}<h2>{title}</h2><p>{description}</p>{actionLabel && onAction ? <Button variant="secondary" onClick={onAction}>{actionLabel}</Button> : null}</div>;
}
