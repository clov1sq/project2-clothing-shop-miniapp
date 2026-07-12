import { useQuery } from '@tanstack/react-query';
import { Link } from '../../shared/router';

import { catalogApi } from '../../shared/api/client';
import { AppHeader } from '../../shared/ui/AppHeader';
import { ArrowRightIcon, SearchIcon } from '../../shared/ui/Icons';
import { ProductCard } from '../../shared/ui/ProductCard';
import { ProductCardSkeleton } from '../../shared/ui/Skeleton';
import { SectionHeader } from '../../shared/ui/SectionHeader';
import { StateScreen } from '../../shared/ui/StateScreen';

function ProductRail({ products }: { products: Awaited<ReturnType<typeof catalogApi.home>>['new_products'] }) {
  return <div className="product-rail">{products.map((product) => <div className="product-rail__item" key={product.id}><ProductCard product={product}/></div>)}</div>;
}

export function HomePage() {
  const query = useQuery({ queryKey: ['home'], queryFn: catalogApi.home, staleTime: 120_000 });
  return <main className="page page--home"><AppHeader/><Link to="/catalog" className="home-search"><SearchIcon size={21}/><span>Знайти одяг, взуття або бренд</span></Link><section className="hero-editorial"><div className="hero-editorial__copy"><p className="hero-editorial__kicker">Нова міська добірка</p><h1>Форма, що рухається разом із вами</h1><p>Чисті силуети, продумані матеріали та речі для щоденного ритму.</p><Link to="/catalog?new=true" className="hero-editorial__link">Переглянути новинки <ArrowRightIcon size={18}/></Link></div><div className="hero-editorial__art"><span/><span/><span/></div></section>{query.isLoading ? <><section className="home-section"><SectionHeader title="Категорії"/><div className="category-rail">{Array.from({length:4},(_,i)=><div className="category-card category-card--skeleton" key={i}/>)}</div></section><section className="home-section"><SectionHeader title="Новинки"/><div className="product-rail">{Array.from({length:3},(_,i)=><div className="product-rail__item" key={i}><ProductCardSkeleton/></div>)}</div></section></> : query.isError ? <StateScreen title="Не вдалося завантажити головну" description="Перевірте з’єднання та повторіть спробу." actionLabel="Повторити" onAction={() => query.refetch()}/> : query.data ? <><section className="home-section"><SectionHeader title="Категорії" link="/catalog"/><div className="category-rail">{query.data.categories.map((category) => <Link key={category.id} to={`/catalog?category=${category.slug}`} className="category-card"><div className="category-card__image">{category.image_url ? <img src={category.image_url} alt="" loading="lazy"/> : null}</div><div><strong>{category.name}</strong><span>{category.description}</span></div></Link>)}</div></section><section className="home-section"><SectionHeader title="Новинки" link="/catalog?new=true"/><ProductRail products={query.data.new_products}/></section><section className="home-section"><SectionHeader title="Знижки" link="/catalog?sale=true"/><ProductRail products={query.data.sale_products}/></section><section className="home-section"><SectionHeader title="Вибір редакції" link="/catalog"/><ProductRail products={query.data.featured_products}/></section></> : null}</main>;
}
