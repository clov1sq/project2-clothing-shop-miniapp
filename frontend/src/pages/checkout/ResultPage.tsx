import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate, useParams } from '../../shared/router';
import { checkoutApi } from '../../shared/api/client';
import { bindTelegramBack } from '../../shared/telegram/telegram';
import { CheckoutHeader, CheckoutOrderItems, ContactSummary, DeliverySummary, ReservationNotice } from '../../shared/ui/Checkout';
import { CheckCircleIcon } from '../../shared/ui/Icons';
import { formatPrice } from '../../shared/ui/Price';
import { PageSkeleton } from '../../shared/ui/Skeleton';
import { StateScreen } from '../../shared/ui/StateScreen';

export function CheckoutResultPage() {
  const { orderId='' } = useParams();
  const navigate=useNavigate();
  useEffect(()=>bindTelegramBack(()=>navigate('/')),[navigate]);
  const query=useQuery({queryKey:['order',orderId],queryFn:()=>checkoutApi.order(orderId),retry:false});
  if(query.isLoading) return <PageSkeleton/>;
  if(query.isError || !query.data) return <StateScreen title="Замовлення не відкрилося" description="Спробуйте повернутися на головну сторінку." actionLabel="На головну" onAction={()=>navigate('/')}/>;
  const order=query.data;
  return <main className="page checkout-page checkout-result"><CheckoutHeader step={4} title="Замовлення створено"/><section className="order-success"><div><CheckCircleIcon size={36}/></div><p>Номер замовлення</p><h2>{order.order_number}</h2><span className="order-status">Очікує оплату</span><strong>{formatPrice(order.grand_total,order.currency)}</strong></section><ReservationNotice expiresAt={order.reservation_expires_at}/><CheckoutOrderItems items={order.items} currency={order.currency}/><div className="checkout-review__grid"><ContactSummary contact={order.contact}/><DeliverySummary delivery={order.delivery}/></div><section className="payment-preview"><h2>Оплата</h2><p>Тестова оплата буде додана в наступній версії.</p></section><button type="button" className="button button--primary button--full" onClick={()=>navigate('/')}>Повернутися на головну</button></main>;
}
