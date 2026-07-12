import type { ButtonHTMLAttributes, ReactNode } from 'react';

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  loading?: boolean;
  full?: boolean;
  icon?: ReactNode;
};

export function Button({ variant = 'primary', loading = false, full = false, icon, children, className = '', disabled, ...props }: Props) {
  return <button className={`button button--${variant} ${full ? 'button--full' : ''} ${className}`} disabled={disabled || loading} {...props}>{loading ? <span className="button__spinner" /> : icon}{children}</button>;
}
