import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '../../shared/router';
import { ApiError, checkoutApi } from '../../shared/api/client';
import { clearCheckoutDraft, getCheckoutIdempotencyKey, readCheckoutDraft } from '../../shared/checkout/storage';
import { bindTelegramBack, notifyHaptic } from '../../shared/telegram/telegram';
import { CheckoutActions, CheckoutHeader, CheckoutOrderItems, ContactSummary, DeliverySummary, ReservationNotice } from '../../shared/ui/Checkout';
import { formatPrice } from '../../shared/ui/Price';
import { PageSkeleton } from '../../shared/ui/Skeleton';
import { StateScreen } from '../../shared/ui/StateScreen';
import { MutationErrorToast } from '../../shared/ui/Commerce';

export function CheckoutReviewPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [draft] = useState(readCheckoutDraft);
  const [error, setError] = useState<string|null>(null);
  useEffect(() => bindTelegramBack(() => navigate('/checkout/delivery')), [navigate]);
  const validation = useQuery({ queryKey:['checkout-validation',draft], queryFn:()=>checkoutApi.validate(draft), retry:false, staleTime:0 });
  const confirm = useMutation({ mutationFn:()=>checkoutApi.confirm(draft,getCheckoutIdempotencyKey()), onSuccess:(order)=>{ queryClient.setQueryData(['cart'],{id:null,items:[],total_quantity:0,subtotal:'0.00',discount_total:'0.00',grand_total:'0.00',currency:'UAH',has_issues:false}); clearCheckoutDraft(); notifyHaptic('success'); navigate(`/checkout/result/${order.id}`,{replace:true}); }, onError:(reason)=>{ setError(reason instanceof ApiError ? reason.message : 'Не вдалося створити замовлення'); notifyHaptic('error'); } });
  if (validation.isLoading) return <PageSkeleton/>;
  if (validation.isError || !validation.data) return <StateScreen title="Не вдалося перевірити кошик" description={validation.error instanceof ApiError ? validation.error.message : 'Поверніться в кошик і повторіть спробу.'} actionLabel="До кошика" onAction={()=>navigate('/cart')}/>;
  const data=validation.data;
  return <main className="page checkout-page checkout-review"><CheckoutHeader step={3} title="Перевірте замовлення" subtitle="Після підтвердження товари буде зарезервовано на 15 хвилин."/><CheckoutOrderItems items={data.cart.items} currency={data.cart.currency}/><div className="checkout-review__grid"><ContactSummary contact={draft.contact}/><DeliverySummary delivery={draft.delivery}/></div><section className="checkout-total-card"><div><span>Товарів</span><strong>{data.cart.total_quantity}</strong></div><div><span>Сума</span><strong>{formatPrice(data.cart.subtotal,data.cart.currency)}</strong></div><div className="checkout-total-card__grand"><span>Разом</span><strong>{formatPrice(data.cart.grand_total,data.cart.currency)}</strong></div></section><ReservationNotice/><CheckoutActions backLabel="Назад" nextLabel="Підтвердити замовлення" loading={confirm.isPending} onBack={()=>navigate('/checkout/delivery')} onNext={()=>confirm.mutate()}/><MutationErrorToast message={error} onClose={()=>setError(null)}/></main>;
}
