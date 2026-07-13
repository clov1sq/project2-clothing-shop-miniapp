import { useEffect, useState } from 'react';
import { useNavigate } from '../../shared/router';
import type { CheckoutContact } from '../../shared/api/types';
import { bindTelegramBack } from '../../shared/telegram/telegram';
import { readCheckoutDraft, writeCheckoutDraft } from '../../shared/checkout/storage';
import { CheckoutActions, CheckoutHeader, Field } from '../../shared/ui/Checkout';

function validate(contact: CheckoutContact): Record<string, string> {
  const errors: Record<string, string> = {};
  if (contact.first_name.trim().length < 2) errors.first_name = 'Вкажіть ім’я';
  if (contact.last_name.trim().length < 2) errors.last_name = 'Вкажіть прізвище';
  if (contact.phone.replace(/\D/g, '').length < 9) errors.phone = 'Вкажіть коректний телефон';
  if (contact.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact.email)) errors.email = 'Перевірте email';
  return errors;
}

export function CheckoutContactPage() {
  const navigate = useNavigate();
  const [draft, setDraft] = useState(readCheckoutDraft);
  const [errors, setErrors] = useState<Record<string,string>>({});
  useEffect(() => bindTelegramBack(() => navigate('/cart')), [navigate]);
  useEffect(() => { writeCheckoutDraft(draft); }, [draft]);
  const update = (key: keyof CheckoutContact, value: string) => setDraft((current) => ({ ...current, contact: { ...current.contact, [key]: value || null } }));
  const next = () => {
    const nextErrors = validate(draft.contact);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;
    writeCheckoutDraft(draft);
    navigate('/checkout/delivery');
  };
  return <main className="page checkout-page"><CheckoutHeader step={1} title="Контактні дані" subtitle="Вкажіть, кому передати замовлення."/><section className="checkout-form-card"><div className="checkout-form-grid"><Field label="Ім’я" error={errors.first_name}><input autoComplete="given-name" value={draft.contact.first_name} onChange={(event)=>update('first_name',event.target.value)}/></Field><Field label="Прізвище" error={errors.last_name}><input autoComplete="family-name" value={draft.contact.last_name} onChange={(event)=>update('last_name',event.target.value)}/></Field></div><Field label="Телефон" error={errors.phone}><input type="tel" inputMode="tel" autoComplete="tel" placeholder="+380 67 000 00 00" value={draft.contact.phone} onChange={(event)=>update('phone',event.target.value)}/></Field><Field label="Email — необов’язково" error={errors.email}><input type="email" inputMode="email" autoComplete="email" value={draft.contact.email || ''} onChange={(event)=>update('email',event.target.value)}/></Field><Field label="Коментар — необов’язково"><textarea rows={3} maxLength={1000} value={draft.contact.comment || ''} onChange={(event)=>update('comment',event.target.value)}/></Field></section><CheckoutActions onBack={()=>navigate('/cart')} onNext={next}/></main>;
}
