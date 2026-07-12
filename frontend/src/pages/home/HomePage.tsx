import type { AppRoute } from '../../app/routes';
import { previewCategories, previewProducts } from '../../shared/data/mockCatalog';
import { AppHeader } from '../../shared/ui/AppHeader';
import { Button } from '../../shared/ui/Button';
import { CategoryChip } from '../../shared/ui/CategoryChip';
import { ArrowRightIcon, ShieldIcon, SparklesIcon, TruckIcon } from '../../shared/ui/Icons';
import { ProductPreviewCard } from '../../shared/ui/ProductPreviewCard';
import { SectionHeader } from '../../shared/ui/SectionHeader';

type Props = {
  shopName: string;
  onNavigate: (route: AppRoute) => void;
  onPreviewAction: () => void;
};

export function HomePage({ shopName, onNavigate, onPreviewAction }: Props) {
  return (
    <main className="page page--home">
      <AppHeader onPreviewAction={onPreviewAction} shopName={shopName} />

      <section className="fashion-hero">
        <div className="fashion-hero__content">
          <p className="fashion-hero__eyebrow">New season · Preview</p>
          <h1>Міський стиль без зайвого шуму</h1>
          <p>Нова самостійна fashion-концепція для Telegram Mini App.</p>
          <div className="fashion-hero__actions">
            <Button icon={<ArrowRightIcon size={18} />} onClick={() => onNavigate('catalog')}>Дивитися колекцію</Button>
            <Button onClick={onPreviewAction} variant="ghost">Про preview</Button>
          </div>
        </div>
        <div className="fashion-hero__visual" aria-hidden="true">
          <div className="fashion-hero__circle" />
          <div className="fashion-hero__model-card">
            <img alt="" src="/mock/hero-look.svg" />
          </div>
          <span className="fashion-hero__season">SS<br />26</span>
        </div>
      </section>

      <section className="category-section" aria-label="Категорії preview">
        <div className="category-strip">
          {previewCategories.map((category, index) => (
            <CategoryChip key={category.id} label={category.label} active={index === 0} onClick={onPreviewAction} />
          ))}
        </div>
      </section>

      <section className="section-block">
        <SectionHeader actionLabel="Усі товари" eyebrow="CURATED FOR YOU" onAction={() => onNavigate('catalog')} title="Нові надходження" />
        <div className="product-grid">
          {previewProducts.slice(0, 4).map((product) => (
            <ProductPreviewCard key={product.id} onPreviewAction={onPreviewAction} product={product} />
          ))}
        </div>
      </section>

      <section className="editorial-banner">
        <div className="editorial-banner__copy">
          <p>EDITOR'S PICK</p>
          <h2>Синій як головний акцент сезону</h2>
          <button onClick={() => onNavigate('catalog')} type="button">Переглянути preview <ArrowRightIcon size={18} /></button>
        </div>
        <img alt="Стилізований fashion preview" loading="lazy" src="/mock/editorial.svg" />
      </section>

      <section className="service-grid" aria-label="Переваги магазину — preview">
        <article>
          <span><TruckIcon /></span>
          <div><strong>Швидка доставка</strong><p>Нова Пошта по Україні</p></div>
        </article>
        <article>
          <span><ShieldIcon /></span>
          <div><strong>Безпечна оплата</strong><p>Захищений checkout</p></div>
        </article>
        <article>
          <span><SparklesIcon /></span>
          <div><strong>Добірки стилістів</strong><p>Актуальні поєднання</p></div>
        </article>
      </section>
    </main>
  );
}
