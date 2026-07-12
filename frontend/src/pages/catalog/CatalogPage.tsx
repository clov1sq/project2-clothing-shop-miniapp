import { previewCategories, previewProducts } from '../../shared/data/mockCatalog';
import { AppHeader } from '../../shared/ui/AppHeader';
import { CategoryChip } from '../../shared/ui/CategoryChip';
import { SlidersIcon } from '../../shared/ui/Icons';
import { ProductPreviewCard } from '../../shared/ui/ProductPreviewCard';
import { StatusBadge } from '../../shared/ui/StatusBadge';

type Props = {
  shopName: string;
  onPreviewAction: () => void;
};

export function CatalogPage({ shopName, onPreviewAction }: Props) {
  return (
    <main className="page">
      <AppHeader onPreviewAction={onPreviewAction} shopName={shopName} />
      <header className="catalog-header">
        <div>
          <p className="page-kicker">Колекція · Preview</p>
          <h1>Каталог</h1>
        </div>
        <button className="filter-button" onClick={onPreviewAction} type="button">
          <SlidersIcon size={20} />
          <span>Фільтри</span>
          <StatusBadge tone="neutral">SOON</StatusBadge>
        </button>
      </header>

      <div className="category-strip category-strip--catalog">
        {previewCategories.map((category, index) => (
          <CategoryChip key={category.id} label={category.label} active={index === 0} onClick={onPreviewAction} />
        ))}
      </div>

      <div className="catalog-toolbar">
        <span>6 товарів</span>
        <button onClick={onPreviewAction} type="button">Спочатку нові</button>
      </div>

      <section className="product-grid" aria-label="Демонстраційний каталог">
        {previewProducts.map((product) => (
          <ProductPreviewCard key={product.id} onPreviewAction={onPreviewAction} product={product} />
        ))}
      </section>
    </main>
  );
}
