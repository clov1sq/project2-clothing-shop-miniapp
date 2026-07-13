import { useEffect, useState } from 'react';
import { useNavigate } from '../../shared/router';
import type { CheckoutDelivery } from '../../shared/api/types';
import { bindTelegramBack } from '../../shared/telegram/telegram';
import { readCheckoutDraft, writeCheckoutDraft } from '../../shared/checkout/storage';
import { CheckoutActions, CheckoutHeader, DeliveryMethodCard, Field } from '../../shared/ui/Checkout';

function validate(delivery: CheckoutDelivery): Record<string,string> {
  const errors: Record<string,string> = {};
  if (delivery.method === 'branch') {
    if (!delivery.city?.trim()) errors.city = 'Вкажіть місто';
    if (!delivery.branch?.trim()) errors.branch = 'Вкажіть відділення';
  }
  if (delivery.method === 'courier') {
    if (!delivery.city?.trim()) errors.city = 'Вкажіть місто';
    if (!delivery.address?.trim()) errors.address = 'Вкажіть адресу';
  }
  return errors;
}

export function CheckoutDeliveryPage() {
  const navigate = useNavigate();
  const [draft, setDraft] = useState(readCheckoutDraft);
  const [errors, setErrors] = useState<Record<string,string>>({});
  useEffect(() => bindTelegramBack(() => navigate('/checkout/contact')), [navigate]);
  useEffect(() => { writeCheckoutDraft(draft); }, [draft]);
  const update = (key: keyof CheckoutDelivery, value: string | null) => setDraft((current)=>({ ...current, delivery:{...current.delivery,[key]:value} }));
  const select = (method: CheckoutDelivery['method']) => setDraft((current)=>({ ...current, delivery:{...current.delivery,method} }));
  const next = () => {
    const nextErrors = validate(draft.delivery);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;
    writeCheckoutDraft(draft);
    navigate('/checkout/review');
  };
  return <main className="page checkout-page"><CheckoutHeader step={2} title="Спосіб отримання" subtitle="Оберіть зручний варіант. Реальна інтеграція служб доставки з’явиться пізніше."/><section className="delivery-methods"><DeliveryMethodCard value="pickup" selected={draft.delivery.method==='pickup'} title="Самовивіз" description="З пункту видачі BlueWear" onSelect={select}/><DeliveryMethodCard value="branch" selected={draft.delivery.method==='branch'} title="У відділення" description="Введіть місто та номер відділення" onSelect={select}/><DeliveryMethodCard value="courier" selected={draft.delivery.method==='courier'} title="Адресна доставка" description="Кур’єром за вказаною адресою" onSelect={select}/></section>{draft.delivery.method !== 'pickup' ? <section className="checkout-form-card">{draft.delivery.method === 'branch' ? <><Field label="Місто" error={errors.city}><input value={draft.delivery.city || ''} onChange={(event)=>update('city',event.target.value)}/></Field><Field label="Відділення" error={errors.branch}><input placeholder="Наприклад, відділення №3" value={draft.delivery.branch || ''} onChange={(event)=>update('branch',event.target.value)}/></Field></> : <><Field label="Місто" error={errors.city}><input value={draft.delivery.city || ''} onChange={(event)=>update('city',event.target.value)}/></Field><Field label="Адреса" error={errors.address}><input placeholder="Вулиця, будинок, квартира" value={draft.delivery.address || ''} onChange={(event)=>update('address',event.target.value)}/></Field></>}</section> : null}<CheckoutActions onBack={()=>navigate('/checkout/contact')} onNext={next}/></main>;
}
