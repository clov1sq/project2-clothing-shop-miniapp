import type { ReactNode } from 'react';
import { Button } from './Button';

type Props = {
  icon: ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function EmptyState({ icon, title, description, actionLabel, onAction }: Props) {
  return (
    <section className="empty-state">
      <div className="empty-state__icon">{icon}</div>
      <h1>{title}</h1>
      <p>{description}</p>
      {actionLabel ? <Button onClick={onAction}>{actionLabel}</Button> : null}
    </section>
  );
}
