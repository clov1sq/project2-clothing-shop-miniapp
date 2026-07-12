import { useQuery } from '@tanstack/react-query';
import { Link } from '../../shared/router';

import { adminApi } from '../../shared/api/client';
import { AppHeader } from '../../shared/ui/AppHeader';
import { ArrowRightIcon, BoxIcon, GridIcon, ImageIcon } from '../../shared/ui/Icons';
import { StateScreen } from '../../shared/ui/StateScreen';

export function AdminDashboardPage() {
  const query = useQuery({ queryKey: ['admin-dashboard'], queryFn: adminApi.dashboard });
  return <main className="page admin-page"><AppHeader title="Керування" eyebrow="BlueWear Admin"/><div className="admin-metrics">{query.isError ? <StateScreen title="Статистика недоступна" description="Спробуйте ще раз." actionLabel="Повторити" onAction={() => query.refetch()}/> : <><article><span>Активні</span><strong>{query.data?.products_by_status.active ?? '—'}</strong></article><article><span>Чернетки</span><strong>{query.data?.products_by_status.draft ?? '—'}</strong></article><article><span>Низький залишок</span><strong>{query.data?.low_stock_variants ?? '—'}</strong></article></>}</div><nav className="admin-menu"><Link to="/admin/products"><GridIcon/><div><strong>Товари</strong><span>Створення, публікація, варіанти</span></div><ArrowRightIcon/></Link><Link to="/admin/inventory"><BoxIcon/><div><strong>Залишки</strong><span>Коригування з журналом рухів</span></div><ArrowRightIcon/></Link><Link to="/admin/categories"><ImageIcon/><div><strong>Категорії</strong><span>Структура каталогу</span></div><ArrowRightIcon/></Link><Link to="/admin/brands"><ImageIcon/><div><strong>Бренди</strong><span>Demo-бренди магазину</span></div><ArrowRightIcon/></Link></nav></main>;
}
