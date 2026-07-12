import type { PreviewProduct } from '../data/mockCatalog';
import { formatPrice } from '../data/mockCatalog';
import { HeartIcon } from './Icons';
import { IconButton } from './IconButton';
import { StatusBadge } from './StatusBadge';

type Props = {
  product: PreviewProduct;
  onPreviewAction?: () => void;
};

export function ProductPreviewCard({ product, onPreviewAction }: Props) {
  const tone = product.badge === 'SALE' ? 'warning' : product.badge === 'NEW' ? 'info' : 'neutral';
  return (
    <article className="preview-product-card">
      <div className="preview-product-card__media">
        <img alt={product.title} loading="lazy" src={product.image} />
        {product.badge ? <StatusBadge tone={tone}>{product.badge}</StatusBadge> : null}
        <IconButton className="preview-product-card__favorite" label="Додати в улюблене — preview" onClick={onPreviewAction}>
          <HeartIcon size={19} />
        </IconButton>
      </div>
      <div className="preview-product-card__body">
        <p className="preview-product-card__category">{product.category}</p>
        <h3>{product.title}</h3>
        <div className="preview-product-card__footer">
          <div className="preview-product-card__price">
            <strong>{formatPrice(product.price)}</strong>
            {product.oldPrice ? <del>{formatPrice(product.oldPrice)}</del> : null}
          </div>
          <div className="preview-product-card__swatches" aria-label="Доступні кольори — preview">
            {product.colors.map((color) => <span key={color} style={{ backgroundColor: color }} />)}
          </div>
        </div>
      </div>
    </article>
  );
}
