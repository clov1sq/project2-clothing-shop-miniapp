export function SaleBadge({ value }: { value: number | null }) { return value ? <span className="badge badge--sale">−{value}%</span> : null; }
export function NewBadge() { return <span className="badge badge--new">NEW</span>; }
export function StatusBadge({ status }: { status: string }) {
  const labels: Record<string, string> = { draft: 'Чернетка', active: 'Опубліковано', archived: 'Архів' };
  return <span className={`status-badge status-badge--${status}`}>{labels[status] || status}</span>;
}
