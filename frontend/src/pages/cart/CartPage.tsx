import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '../../shared/router';
import { useAuth } from '../../auth/AuthProvider';
import { ApiError, cartApi, checkoutApi } from '../../shared/api/client';
import type { CartData } from '../../shared/api/types';
import { notifyHaptic } from '../../shared/telegram/telegram';
import { CartIcon, TrashIcon } from '../../shared/ui/Icons';
import { CartItemCard, CartSummary, ClearCartDialog, EmptyCart, MutationErrorToast } from '../../shared/ui/Commerce';
import { PageSkeleton } from '../../shared/ui/Skeleton';
import { StateScreen } from '../../shared/ui/StateScreen';

function errorMessage(error: unknown): string { return error instanceof ApiError ? error.message : 'Не вдалося оновити кошик'; }

export function CartPage() {
  const navigate = useNavigate();
  const { status } = useAuth();
  const client = useQueryClient();
  const [clearOpen, setClearOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const query = useQuery({ queryKey: ['cart'], queryFn: cartApi.get, staleTime: 15_000, enabled: status === 'authenticated' });
  const apply = (data: CartData) => client.setQueryData(['cart'], data);
  const update = useMutation({ mutationFn: ({id, quantity}:{id:string;quantity:number}) => cartApi.update(id, quantity), onSuccess: (data) => { apply(data); notifyHaptic('success'); }, onError: (value) => { setError(errorMessage(value)); notifyHaptic('error'); } });
  const remove = useMutation({ mutationFn: cartApi.remove, onSuccess: (data) => { apply(data); notifyHaptic('success'); }, onError: (value) => setError(errorMessage(value)) });
  const refresh = useMutation({ mutationFn: cartApi.refresh, onSuccess: apply, onError: (value) => setError(errorMessage(value)) });
  const clear = useMutation({ mutationFn: cartApi.clear, onSuccess: (data) => { apply(data); setClearOpen(false); notifyHaptic('success'); }, onError: (value) => setError(errorMessage(value)) });
  const checkout = useMutation({ mutationFn: () => checkoutApi.validate({}), onSuccess: () => navigate('/checkout/contact'), onError: (value) => { if (value instanceof ApiError && value.details?.cart) apply(value.details.cart as CartData); setError(errorMessage(value)); notifyHaptic('error'); } });
  if (query.isLoading) return <PageSkeleton/>;
  if (query.isError || !query.data) return <StateScreen title="Кошик не відкрився" description="Перевірте інтернет і повторіть спробу." actionLabel="Повторити" onAction={() => query.refetch()} icon={<CartIcon/>}/>;
  const cart = query.data;
  if (cart.items.length === 0) return <main className="page cart-page"><header className="commerce-page-header"><div><p className="page-kicker">Ваші покупки</p><h1>Кошик</h1></div></header><EmptyCart onCatalog={() => navigate('/catalog')}/><MutationErrorToast message={error} onClose={() => setError(null)}/></main>;
  return <main className="page cart-page"><header className="commerce-page-header"><div><p className="page-kicker">Ваші покупки</p><h1>Кошик</h1></div><button type="button" className="clear-cart-button" onClick={() => setClearOpen(true)}><TrashIcon size={18}/>Очистити</button></header><div className="cart-layout"><section className="cart-items">{cart.items.map((item) => <CartItemCard key={item.id} item={item} busy={update.isPending || remove.isPending || refresh.isPending} onQuantity={(quantity) => update.mutate({id:item.id,quantity})} onRemove={() => remove.mutate(item.id)} onAcceptPrice={() => refresh.mutate()}/>)}</section><CartSummary cart={cart} authenticated={status === 'authenticated'} loading={checkout.isPending} onCheckout={() => checkout.mutate()}/></div><ClearCartDialog open={clearOpen} loading={clear.isPending} onClose={() => setClearOpen(false)} onConfirm={() => clear.mutate()}/><MutationErrorToast message={error} onClose={() => setError(null)}/></main>;
}
