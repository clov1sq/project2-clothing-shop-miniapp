# Commerce v4 — обране і кошик

Версія `0.4.0` продовжує стабільну базу `project2_v3_fix1` і додає серверні обране та кошик без checkout.

## Нові таблиці

- `favorites` — один запис на пару користувач + товар;
- `carts` — один активний кошик на користувача;
- `cart_items` — конкретний variant, кількість і snapshot ціни;
- `idempotency_keys` — захист від повторного додавання через double tap або network retry.

Міграція: `0004_favorites_cart`.

## API

### Обране

- `GET /api/v1/favorites`;
- `POST /api/v1/favorites/{product_id}`;
- `DELETE /api/v1/favorites/{product_id}`.

### Кошик

- `GET /api/v1/cart`;
- `POST /api/v1/cart/items` з header `Idempotency-Key`;
- `PATCH /api/v1/cart/items/{item_id}`;
- `DELETE /api/v1/cart/items/{item_id}`;
- `DELETE /api/v1/cart`;
- `POST /api/v1/cart/refresh` для підтвердження актуальних цін.

Backend завжди повторно перевіряє товар, variant, актуальну ціну та доступний залишок. Кошик не резервує товар.

## Frontend

Додані маршрути:

- `/#/favorites`;
- `/#/cart`.

Нижня навігація тепер містить: Головна, Каталог, Обране, Кошик, Профіль. Badge кошика показує загальну кількість одиниць.

Checkout, замовлення, доставка й оплата навмисно не входять у v4.

## Railway

Нові environment variables не потрібні. Backend `start.sh` автоматично виконає `alembic upgrade head` під час deployment.
