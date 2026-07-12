import type { ButtonHTMLAttributes, ReactNode } from 'react';

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  label: string;
  children: ReactNode;
  badge?: string;
};

export function IconButton({ label, children, badge, className = '', ...props }: Props) {
  return (
    <button aria-label={label} className={`icon-button ${className}`.trim()} type="button" {...props}>
      {children}
      {badge ? <span className="icon-button__badge">{badge}</span> : null}
    </button>
  );
}
