import type { CheckoutContact, CheckoutDelivery, CheckoutDraft } from '../api/types';

const DRAFT_KEY = 'project2-checkout-draft-v5';
const IDEMPOTENCY_KEY = 'project2-checkout-idempotency-v5';

export const emptyContact: CheckoutContact = {
  first_name: '',
  last_name: '',
  phone: '',
  email: null,
  comment: null,
};

export const emptyDelivery: CheckoutDelivery = {
  method: 'pickup',
  city: null,
  branch: null,
  address: null,
};

export function readCheckoutDraft(): CheckoutDraft {
  try {
    const raw = sessionStorage.getItem(DRAFT_KEY);
    if (!raw) return { contact: emptyContact, delivery: emptyDelivery };
    const parsed = JSON.parse(raw) as Partial<CheckoutDraft>;
    return {
      contact: { ...emptyContact, ...(parsed.contact || {}) },
      delivery: { ...emptyDelivery, ...(parsed.delivery || {}) },
    };
  } catch {
    return { contact: emptyContact, delivery: emptyDelivery };
  }
}

export function writeCheckoutDraft(draft: CheckoutDraft): void {
  sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
}

export function clearCheckoutDraft(): void {
  sessionStorage.removeItem(DRAFT_KEY);
  sessionStorage.removeItem(IDEMPOTENCY_KEY);
}

export function getCheckoutIdempotencyKey(): string {
  const current = sessionStorage.getItem(IDEMPOTENCY_KEY);
  if (current) return current;
  const next = crypto.randomUUID();
  sessionStorage.setItem(IDEMPOTENCY_KEY, next);
  return next;
}
