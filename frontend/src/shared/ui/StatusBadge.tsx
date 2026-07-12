type Props = {
  children: string;
  tone?: 'neutral' | 'success' | 'warning' | 'info';
};

export function StatusBadge({ children, tone = 'neutral' }: Props) {
  return <span className={`status-badge status-badge--${tone}`}>{children}</span>;
}
