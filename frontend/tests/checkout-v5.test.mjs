import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('checkout routes include contact, delivery, review and result', async () => {
  const source = await read('../src/app/App.tsx');
  assert.match(source, /\/checkout\/contact/);
  assert.match(source, /\/checkout\/delivery/);
  assert.match(source, /\/checkout\/review/);
  assert.match(source, /\/checkout\/result\/:orderId/);
});

test('cart validates before opening checkout', async () => {
  const source = await read('../src/pages/cart/CartPage.tsx');
  assert.match(source, /checkoutApi\.validate/);
  assert.match(source, /navigate\('\/checkout\/contact'\)/);
  const commerce = await read('../src/shared/ui/Commerce.tsx');
  assert.match(commerce, /cart\.has_issues/);
});

test('checkout confirmation uses a stable idempotency key and disables double tap', async () => {
  const source = await read('../src/pages/checkout/ReviewPage.tsx');
  const storage = await read('../src/shared/checkout/storage.ts');
  assert.match(source, /getCheckoutIdempotencyKey/);
  assert.match(source, /confirm\.isPending/);
  assert.match(storage, /sessionStorage\.getItem\(IDEMPOTENCY_KEY\)/);
  assert.match(storage, /crypto\.randomUUID/);
});

test('checkout API is protected by the central credentialed client', async () => {
  const client = await read('../src/shared/api/client.ts');
  assert.match(client, /credentials:\s*'include'/);
  assert.match(client, /\/api\/v1\/checkout\/validate/);
  assert.match(client, /\/api\/v1\/checkout\/confirm/);
  assert.match(client, /Idempotency-Key/);
});

test('product page explicitly scrolls to top and catalog restores real scroll position', async () => {
  const product = await read('../src/pages/product/ProductPage.tsx');
  const catalog = await read('../src/pages/catalog/CatalogPage.tsx');
  const scroll = await read('../src/shared/scroll.ts');
  assert.match(product, /scrollAppTo\(0/);
  assert.match(catalog, /readScrollTop/);
  assert.match(catalog, /scrollAppTo\(saved/);
  assert.match(scroll, /document\.scrollingElement/);
});

test('badges and selected size have explicit contrast', async () => {
  const css = await read('../src/styles/index.css');
  assert.match(css, /\.badge--new\s*\{[^}]*background:\s*#102449[^}]*color:\s*#fff/s);
  assert.match(css, /\.badge--sale\s*\{[^}]*background:\s*#b42335[^}]*color:\s*#fff/s);
  assert.match(css, /\.size-option--active\s*\{[^}]*background:\s*var\(--color-primary\)[^}]*color:\s*#fff/s);
});

test('accordion removes tap highlight while keeping focus visible', async () => {
  const css = await read('../src/styles/index.css');
  assert.match(css, /product-detail-block summary\s*\{[^}]*-webkit-tap-highlight-color:\s*transparent/s);
  assert.match(css, /summary:focus-visible/);
});

test('checkout pages expose loading error retry and reservation result UX', async () => {
  const review = await read('../src/pages/checkout/ReviewPage.tsx');
  const result = await read('../src/pages/checkout/ResultPage.tsx');
  const checkout = await read('../src/shared/ui/Checkout.tsx');
  assert.match(review, /PageSkeleton/);
  assert.match(review, /StateScreen/);
  assert.match(review, /Підтвердити замовлення/);
  assert.match(result, /Очікує оплату/);
  assert.match(result, /Тестова оплата буде додана в наступній версії/);
  assert.match(checkout, /Резерв на 15 хвилин/);
});
