import { formatCatalogPrice } from '../catalog/logic.js';

type Props = { price: string; compareAt?: string | null; currency?: string; compact?: boolean };

export const formatPrice = formatCatalogPrice;

export function Price({ price, compareAt, currency = 'UAH', compact = false }: Props) {
  return <div className={`price ${compact ? 'price--compact' : ''}`}><span className="price__current">{formatPrice(price, currency)}</span>{compareAt ? <span className="price__old">{formatPrice(compareAt, currency)}</span> : null}</div>;
}
