import { useState } from 'react';
import { Link } from '../router';
import type { CartData, CartItemData } from '../api/types';
import { formatPrice, Price } from './Price';
import { Button } from './Button';
import { CartIcon, HeartIcon, MinusIcon, PlusIcon, TrashIcon } from './Icons';
import { Sheet } from './Sheets';
import { StateScreen } from './StateScreen';


export function AddToCartButton({ enabled, loading, onClick }: { enabled: boolean; loading?: boolean; onClick: () => void }) {
  return <Button full loading={loading} disabled={!enabled} onClick={onClick}>Додати в кошик</Button>;
}

export function RemoveItemButton({ loading, onClick }: { loading?: boolean; onClick: () => void }) {
  return <button type="button" className="remove-item-button" aria-label="Видалити товар" disabled={loading} onClick={onClick}><TrashIcon size={19}/></button>;
}

export function EmptyFavorites({ onCatalog }: { onCatalog: () => void }) {
  return <StateScreen title="Поки що порожньо" description="Збережіть товари, які сподобалися, щоб швидко повернутися до них." actionLabel="Перейти до каталогу" onAction={onCatalog} icon={<HeartIcon/>}/>;
}

export function EmptyCart({ onCatalog }: { onCatalog: () => void }) {
  return <StateScreen title="Кошик порожній" description="Оберіть товар, колір і розмір — позиція з’явиться тут." actionLabel="Перейти до каталогу" onAction={onCatalog} icon={<CartIcon/>}/>;
}

export function CartBadge({ value }: { value: number }) {
  if (value <= 0) return null;
  return <span className="cart-badge" aria-label={`${value} товарів у кошику`}>{value > 9 ? '9+' : value}</span>;
}

export function QuantitySelector({ value, max, loading, disabled, onChange }: { value: number; max: number; loading?: boolean; disabled?: boolean; onChange: (value: number) => void }) {
  return <div className="quantity-selector" aria-label="Кількість"><button type="button" aria-label="Зменшити кількість" disabled={disabled || loading || value <= 1} onClick={() => onChange(value - 1)}><MinusIcon size={17}/></button><span aria-live="polite">{loading ? '…' : value}</span><button type="button" aria-label="Збільшити кількість" disabled={disabled || loading || value >= max} onClick={() => onChange(value + 1)}><PlusIcon size={17}/></button></div>;
}

export function PriceChangeNotice({ snapshot, current, onAccept, loading }: { snapshot: string; current: string; onAccept: () => void; loading?: boolean }) {
  const lower = Number(current) < Number(snapshot);
  return <div className="price-change-notice"><strong>{lower ? 'Ціна знизилася' : 'Ціна змінилася'}</strong><span>Було {formatPrice(snapshot)}, зараз {formatPrice(current)}.</span><button type="button" disabled={loading} onClick={onAccept}>Зрозуміло</button></div>;
}

export function StockNotice({ message }: { message: string }) {
  return <div className="stock-notice" role="status">{message}</div>;
}

export function CartItemCard({ item, busy, onQuantity, onRemove, onAcceptPrice }: { item: CartItemData; busy?: boolean; onQuantity: (value: number) => void; onRemove: () => void; onAcceptPrice: () => void }) {
  return <article className={`cart-item-card ${!item.is_available ? 'cart-item-card--issue' : ''}`}><Link className="cart-item-card__image" to={`/products/${item.product_slug}`}>{item.image_url ? <img src={item.image_url} alt={item.product_name}/> : <div>BW</div>}</Link><div className="cart-item-card__content"><div className="cart-item-card__head"><div><p>{item.brand}</p><Link to={`/products/${item.product_slug}`}><h2>{item.product_name}</h2></Link></div><RemoveItemButton loading={busy} onClick={onRemove}/></div><p className="cart-item-card__variant">{item.color.name} · {item.size.name} <span>SKU {item.sku}</span></p><Price price={item.unit_price} compareAt={item.old_price} compact/>{item.price_changed ? <PriceChangeNotice snapshot={item.unit_price_snapshot} current={item.unit_price} onAccept={onAcceptPrice} loading={busy}/> : null}{item.unavailable_message ? <StockNotice message={item.unavailable_message}/> : null}<div className="cart-item-card__footer"><QuantitySelector value={item.quantity} max={item.max_quantity} loading={busy} disabled={!item.is_available} onChange={onQuantity}/><div><span>Сума</span><strong>{formatPrice(item.subtotal)}</strong></div></div></div></article>;
}

export function CartSummary({ cart, authenticated, loading, onCheckout }: { cart: CartData; authenticated: boolean; loading?: boolean; onCheckout: () => void }) {
  const canCheckout = authenticated && cart.items.length > 0 && !cart.has_issues && !cart.items.some((item) => item.price_changed || !item.is_available);
  return <section className="cart-summary"><h2>Підсумок</h2><dl><div><dt>Товарів</dt><dd>{cart.total_quantity}</dd></div><div><dt>Вартість</dt><dd>{formatPrice(cart.subtotal, cart.currency)}</dd></div>{Number(cart.discount_total) > 0 ? <div className="cart-summary__discount"><dt>Знижка</dt><dd>− {formatPrice(cart.discount_total, cart.currency)}</dd></div> : null}<div className="cart-summary__total"><dt>Разом</dt><dd>{formatPrice(cart.grand_total, cart.currency)}</dd></div></dl><p className="cart-summary__reserve">Кошик не резервує товар. Резерв на 15 хвилин створиться після підтвердження замовлення.</p>{cart.has_issues ? <p className="cart-summary__issue">Виправте проблемні позиції перед оформленням.</p> : null}<Button full loading={loading} disabled={!canCheckout} onClick={onCheckout}>Оформити замовлення</Button></section>;
}

export function ClearCartDialog({ open, loading, onClose, onConfirm }: { open: boolean; loading?: boolean; onClose: () => void; onConfirm: () => void }) {
  return <Sheet open={open} title="Очистити кошик?" onClose={onClose} footer={<div className="sheet-actions"><Button variant="secondary" onClick={onClose}>Залишити</Button><Button variant="danger" loading={loading} onClick={onConfirm}>Очистити</Button></div>}><p className="dialog-copy">Усі позиції буде видалено. Цю дію не можна скасувати.</p></Sheet>;
}

export function AddedToCartSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  return <Sheet open={open} title="Товар додано" onClose={onClose}><div className="added-to-cart"><div><CartIcon size={27}/></div><p>Варіант збережено у вашому кошику.</p><Link className="button button--primary button--full" to="/cart" onClick={onClose}>Перейти в кошик</Link><Button full variant="secondary" onClick={onClose}>Продовжити покупки</Button></div></Sheet>;
}

export function MutationErrorToast({ message, onClose }: { message: string | null; onClose: () => void }) {
  if (!message) return null;
  return <div className="mutation-toast" role="alert"><span>{message}</span><button type="button" onClick={onClose}>Закрити</button></div>;
}
