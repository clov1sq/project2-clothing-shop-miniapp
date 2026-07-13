# Checkout v5

## Flow

1. `/checkout/contact`
2. `/checkout/delivery`
3. `/checkout/review`
4. `/checkout/result/{orderId}`

The frontend stores the unfinished form in `sessionStorage`. The server remains the source of truth for cart contents, price and inventory.

## Atomic confirmation

`POST /api/v1/checkout/confirm` requires `Idempotency-Key` and performs one database transaction:

- locks the user cart and cart items;
- locks inventory rows in deterministic order with `FOR UPDATE`;
- revalidates product, variant, price and available quantity;
- creates the order and item snapshots;
- atomically increments `quantity_reserved` only when enough stock remains;
- creates active reservations and inventory movements;
- stores the idempotent response;
- clears cart items;
- commits all changes together.

A repeated request with the same key and payload returns the original order. A different payload with the same key returns `IDEMPOTENCY_CONFLICT`.

## Reservation expiry

The backend process runs a lightweight periodic task without Redis or Celery. It selects expired active reservations with row locks and `SKIP LOCKED`, releases reserved quantities, writes inventory movements and marks orders as expired. Repeated execution is safe.

## Payment

Online payment is intentionally outside v5. Orders are created as `awaiting_payment`, with `payment_status=not_started` and `delivery_status=not_created`.
