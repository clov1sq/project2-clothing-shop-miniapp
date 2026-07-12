import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

import { ApiError, adminApi } from '../../shared/api/client';
import type { ProductVariant } from '../../shared/api/types';
import { AppHeader } from '../../shared/ui/AppHeader';
import { Button } from '../../shared/ui/Button';
import { SearchInput } from '../../shared/ui/SearchInput';

function InventoryLine({ productName, variant, onMessage }: { productName:string; variant:ProductVariant; onMessage:(message:string)=>void }) {
  const [quantity,setQuantity]=useState(String(variant.quantity_on_hand ?? variant.available_quantity));
  const mutation=useMutation({mutationFn:()=>adminApi.adjustInventory(variant.id,{quantity_on_hand:Number(quantity),movement_type:'correction',reason:'Коригування на екрані залишків'}),onSuccess:()=>onMessage('Залишок оновлено'),onError:(e)=>onMessage(e instanceof ApiError?e.message:'Не вдалося оновити')});
  return <article className="inventory-line"><div><strong>{productName}</strong><span>{variant.color_code} · {variant.size_code} · {variant.sku}</span></div><div><input inputMode="numeric" value={quantity} onChange={(e)=>setQuantity(e.target.value)}/><Button variant="ghost" loading={mutation.isPending} onClick={()=>mutation.mutate()}>Зберегти</Button></div></article>;
}

export function AdminInventoryPage() {
  const [search,setSearch]=useState(''); const [message,setMessage]=useState<string|null>(null);
  const params=new URLSearchParams(); if(search.trim().length>=2) params.set('q',search.trim()); params.set('limit','100');
  const query=useQuery({queryKey:['admin-inventory',params.toString()],queryFn:()=>adminApi.products(params)});
  return <main className="page admin-page"><AppHeader title="Залишки" eyebrow="Склад"/><SearchInput value={search} onChange={setSearch} placeholder="Пошук товару або SKU"/>{message?<div className="form-message">{message}</div>:null}<div className="inventory-list">{query.data?.items.flatMap((product)=>product.variants.map((variant)=><InventoryLine key={variant.id} productName={product.name} variant={variant} onMessage={setMessage}/>))}</div></main>;
}
