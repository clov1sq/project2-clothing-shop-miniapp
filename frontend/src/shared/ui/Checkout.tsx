import type { ReactNode } from 'react';
import type { CheckoutContact, CheckoutDelivery, OrderItemData } from '../api/types';
import { Link } from '../router';
import { formatPrice, Price } from './Price';
import { CheckIcon, ClockIcon } from './Icons';

const steps = ['Контакти', 'Отримання', 'Перевірка', 'Готово'];

export function CheckoutHeader({ step, title, subtitle }: { step: number; title: string; subtitle?: string }) {
  return <header className="checkout-header"><p className="page-kicker">Оформлення замовлення</p><h1>{title}</h1>{subtitle ? <p>{subtitle}</p> : null}<div className="checkout-progress" aria-label={`Крок ${step} з 4`}>{steps.map((label,index)=><div key={label} className={index + 1 <= step ? 'checkout-progress__step checkout-progress__step--active' : 'checkout-progress__step'}><span>{index + 1 < step ? <CheckIcon size={14}/> : index + 1}</span><small>{label}</small></div>)}</div></header>;
}

export function CheckoutActions({ backLabel = 'Назад', nextLabel = 'Далі', loading, disabled, onBack, onNext }: { backLabel?: string; nextLabel?: string; loading?: boolean; disabled?: boolean; onBack: () => void; onNext: () => void }) {
  return <div className="checkout-actions"><button type="button" className="button button--secondary" onClick={onBack}>{backLabel}</button><button type="button" className="button button--primary" disabled={disabled || loading} onClick={onNext}>{loading ? <span className="button__spinner"/> : null}{nextLabel}</button></div>;
}

export function Field({ label, error, children }: { label: string; error?: string; children: ReactNode }) {
  return <label className={`checkout-field ${error ? 'checkout-field--error' : ''}`}><span>{label}</span>{children}{error ? <small>{error}</small> : null}</label>;
}

export function DeliveryMethodCard({ value, selected, title, description, onSelect }: { value: CheckoutDelivery['method']; selected: boolean; title: string; description: string; onSelect: (value: CheckoutDelivery['method']) => void }) {
  return <button type="button" className={selected ? 'delivery-method delivery-method--selected' : 'delivery-method'} onClick={() => onSelect(value)} aria-pressed={selected}><span className="delivery-method__radio">{selected ? <CheckIcon size={16}/> : null}</span><span><strong>{title}</strong><small>{description}</small></span></button>;
}

export function CheckoutOrderItems({ items, currency = 'UAH' }: { items: Array<OrderItemData | { id: string; product_slug: string; product_name: string; brand: string; color: {name:string}; size:{name:string}; image_url:string|null; quantity:number; unit_price:string; old_price:string|null; subtotal:string }>; currency?: string }) {
  return <div className="checkout-order-items">{items.map((item) => {
    const color = 'color' in item && typeof item.color === 'object' ? item.color.name : String(item.color);
    const size = 'size' in item && typeof item.size === 'object' ? item.size.name : String(item.size);
    const compare = 'compare_at_price' in item ? item.compare_at_price : item.old_price;
    return <article className="checkout-order-item" key={item.id}><Link to={`/products/${item.product_slug}`} className="checkout-order-item__image">{item.image_url ? <img src={item.image_url} alt={item.product_name}/> : <div>BW</div>}</Link><div><p>{item.brand}</p><h3>{item.product_name}</h3><span>{color} · {size} · {item.quantity} шт.</span><Price price={item.unit_price} compareAt={compare} currency={currency} compact/></div><strong>{formatPrice(item.subtotal, currency)}</strong></article>;
  })}</div>;
}

export function ContactSummary({ contact }: { contact: CheckoutContact }) {
  return <section className="checkout-summary-card"><h2>Контактні дані</h2><dl><div><dt>Отримувач</dt><dd>{contact.first_name} {contact.last_name}</dd></div><div><dt>Телефон</dt><dd>{contact.phone}</dd></div>{contact.email ? <div><dt>Email</dt><dd>{contact.email}</dd></div> : null}{contact.comment ? <div><dt>Коментар</dt><dd>{contact.comment}</dd></div> : null}</dl></section>;
}

export function DeliverySummary({ delivery }: { delivery: CheckoutDelivery }) {
  const title = delivery.method === 'pickup' ? 'Самовивіз' : delivery.method === 'branch' ? 'Доставка у відділення' : 'Адресна доставка';
  const details = delivery.method === 'pickup' ? 'BlueWear, пункт видачі' : delivery.method === 'branch' ? `${delivery.city}, ${delivery.branch}` : `${delivery.city}, ${delivery.address}`;
  return <section className="checkout-summary-card"><h2>Спосіб отримання</h2><strong>{title}</strong><p>{details}</p></section>;
}

export function ReservationNotice({ expiresAt }: { expiresAt?: string }) {
  return <div className="reservation-notice"><ClockIcon size={19}/><div><strong>Резерв на 15 хвилин</strong><span>{expiresAt ? `Активний до ${new Date(expiresAt).toLocaleTimeString('uk-UA',{hour:'2-digit',minute:'2-digit'})}` : 'Після підтвердження товари буде зарезервовано на 15 хвилин.'}</span></div></div>;
}
