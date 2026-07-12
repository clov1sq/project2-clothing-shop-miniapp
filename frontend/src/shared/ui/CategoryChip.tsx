type Props = {
  label: string;
  active?: boolean;
  onClick?: () => void;
};

export function CategoryChip({ label, active = false, onClick }: Props) {
  return (
    <button className={active ? 'category-chip category-chip--active' : 'category-chip'} onClick={onClick} type="button">
      {label}
    </button>
  );
}
