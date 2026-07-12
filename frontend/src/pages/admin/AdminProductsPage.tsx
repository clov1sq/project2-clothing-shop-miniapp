import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from '../../shared/router';

import { adminApi } from '../../shared/api/client';
import { AppHeader } from '../../shared/ui/AppHeader';
import { EditIcon, PlusIcon } from '../../shared/ui/Icons';
import { SearchInput } from '../../shared/ui/SearchInput';
import { StatusBadge } from '../../shared/ui/Badges';
import { Price } from '../../shared/ui/Price';
import { StateScreen } from '../../shared/ui/StateScreen';

export function AdminProductsPage() {
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const params = new URLSearchParams(); if (search.trim().length >= 2) params.set('q', search.trim()); if (status) params.set('status', status);
  const query = useQuery({ queryKey: ['admin-products', params.toString()], queryFn: () => adminApi.products(params) });
  return <main className="page admin-page"><AppHeader title="Товари" eyebrow="Каталог" action={<Link to="/admin/products/new" className="header-action" aria-label="Новий товар"><PlusIcon/></Link>}/><SearchInput value={search} onChange={setSearch} placeholder="Назва, код або SKU"/><div className="admin-status-tabs">{[['','Усі'],['draft','Чернетки'],['active','Активні'],['archived','Архів']].map(([value,label]) => <button type="button" key={value} onClick={() => setStatus(value)} className={status === value ? 'active' : ''}>{label}</button>)}</div>{query.isError ? <StateScreen title="Товари не завантажились" description="Повторіть запит." actionLabel="Повторити" onAction={() => query.refetch()}/> : <div className="admin-product-list">{query.data?.items.map((product) => <article className="admin-product-card" key={product.id}><div className="admin-product-card__image">{product.image_url ? <img src={product.image_url} alt=""/> : <span>BW</span>}</div><div className="admin-product-card__body"><div><p>{product.brand.name}</p><h3>{product.name}</h3></div><div className="admin-product-card__meta"><Price price={product.price} compareAt={product.compare_at_price} compact/><StatusBadge status={product.status}/></div><p className="admin-product-card__stock">{product.variants.reduce((sum,item)=>sum+item.available_quantity,0)} од. доступно · {product.variants.length} варіантів</p></div><Link className="icon-button" to={`/admin/products/${product.id}`} aria-label="Редагувати"><EditIcon/></Link></article>)}</div>}</main>;
}
