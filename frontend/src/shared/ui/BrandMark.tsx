type Props = {
  compact?: boolean;
  shopName?: string;
};

export function BrandMark({ compact = false, shopName = 'BlueWear' }: Props) {
  return (
    <div className={compact ? 'brand-mark brand-mark--compact' : 'brand-mark'} aria-label={shopName}>
      <span className="brand-mark__symbol" aria-hidden="true">
        <span />
        <span />
      </span>
      <span className="brand-mark__word">{shopName}</span>
    </div>
  );
}
