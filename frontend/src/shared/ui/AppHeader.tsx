import type { ReactNode } from 'react';
import { BrandMark } from './BrandMark';

export function AppHeader({ title, eyebrow, action }: { title?: string; eyebrow?: string; action?: ReactNode }) {
  return <header className="app-header"><div>{title ? <><p className="app-header__eyebrow">{eyebrow}</p><h1 className="app-header__title">{title}</h1></> : <BrandMark />}</div>{action}</header>;
}
