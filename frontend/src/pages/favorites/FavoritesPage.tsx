import { useQuery } from '@tanstack/react-query';
import { useNavigate } from '../../shared/router';
import { favoritesApi } from '../../shared/api/client';
import { HeartIcon } from '../../shared/ui/Icons';
import { EmptyFavorites } from '../../shared/ui/Commerce';
import { ProductCard } from '../../shared/ui/ProductCard';
import { ProductCardSkeleton } from '../../shared/ui/Skeleton';
import { StateScreen } from '../../shared/ui/StateScreen';

export function FavoritesPage() {
  const navigate = useNavigate();
  const query = useQuery({ queryKey: ['favorites'], queryFn: () => favoritesApi.list(), staleTime: 30_000 });
  const items = query.data?.items || [];
  return <main className="page favorites-page"><header className="commerce-page-header"><div><p className="page-kicker">Ваш вибір</p><h1>Обране</h1></div><span>{query.data?.pagination.total ?? 0}</span></header>{query.isLoading ? <div className="product-grid">{Array.from({length:6},(_,index)=><ProductCardSkeleton key={index}/>)}</div> : query.isError ? <StateScreen title="Не вдалося відкрити обране" description="Перевірте з’єднання та повторіть спробу." actionLabel="Повторити" onAction={() => query.refetch()} icon={<HeartIcon/>}/> : items.length === 0 ? <EmptyFavorites onCatalog={() => navigate('/catalog')}/> : <div className="product-grid favorite-grid">{items.map((product) => <div key={product.id} className={!product.is_active ? 'favorite-grid__unavailable' : ''}><ProductCard product={product}/>{!product.is_active ? <p>{product.unavailable_message || 'Товар недоступний'}</p> : null}</div>)}</div>}</main>;
}
