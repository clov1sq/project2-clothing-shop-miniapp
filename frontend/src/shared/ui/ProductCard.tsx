import { Link } from '../router';
import type { ProductCardData } from '../api/types';
import { haptic } from '../telegram/telegram';
import { NewBadge, SaleBadge } from './Badges';
import { FavoriteButton } from './FavoriteButton';
import { Price } from './Price';

export function ProductCard({ product, onOpen }: { product: ProductCardData; onOpen?: () => void }) {
  return <article className={`product-card ${!product.is_available ? 'product-card--unavailable' : ''}`}><Link to={`/products/${product.slug}`} className="product-card__link" onClick={() => { haptic(); onOpen?.(); }}><div className="product-card__media">{product.image_url ? <img src={product.image_url} alt={product.name} loading="lazy" /> : <div className="product-card__fallback">BW</div>}<div className="product-card__badges">{product.is_new ? <NewBadge /> : null}<SaleBadge value={product.discount_percent} /></div>{!product.is_available ? <span className="product-card__stock">Немає в наявності</span> : null}</div><div className="product-card__body"><p className="product-card__brand">{product.brand.name}</p><h3 className="product-card__name">{product.name}</h3><Price price={product.price} compareAt={product.compare_at_price} currency={product.currency} compact /></div></Link><FavoriteButton productId={product.id} initial={product.is_favorite}/></article>;
}
