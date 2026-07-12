export function BrandMark({ compact = false }: { compact?: boolean }) {
  const name = import.meta.env.VITE_SHOP_NAME || 'BlueWear';
  return <div className={`brand-mark ${compact ? 'brand-mark--compact' : ''}`}><span className="brand-mark__symbol">B</span><span className="brand-mark__name">{name}</span></div>;
}
