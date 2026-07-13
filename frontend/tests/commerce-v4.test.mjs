import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('FavoriteButton implements optimistic state and rollback', async () => {
  const source = await read('../src/shared/ui/FavoriteButton.tsx');
  assert.match(source, /onMutate/);
  assert.match(source, /onError/);
  assert.match(source, /previous/);
  assert.match(source, /invalidateQueries/);
});

test('favorites page has loading, empty and retry states', async () => {
  const source = await read('../src/pages/favorites/FavoritesPage.tsx');
  const commerce = await read('../src/shared/ui/Commerce.tsx');
  assert.match(source, /ProductCardSkeleton/);
  assert.match(source, /EmptyFavorites/);
  assert.match(commerce, /Поки що порожньо/);
  assert.match(source, /Повторити/);
});

test('cart page has empty, retry, clear confirmation and server mutations', async () => {
  const source = await read('../src/pages/cart/CartPage.tsx');
  const commerce = await read('../src/shared/ui/Commerce.tsx');
  assert.match(source, /EmptyCart/);
  assert.match(commerce, /Кошик порожній/);
  assert.match(source, /ClearCartDialog/);
  assert.match(source, /cartApi\.update/);
  assert.match(source, /cartApi\.remove/);
});

test('product page only adds a selected available variant', async () => {
  const source = await read('../src/pages/product/ProductPage.tsx');
  const commerce = await read('../src/shared/ui/Commerce.tsx');
  assert.match(source, /selectedVariant\?\.is_available/);
  assert.match(source, /enabled=\{canAdd\}/);
  assert.match(commerce, /disabled=\{!enabled\}/);
  assert.match(source, /cartApi\.add/);
  assert.match(source, /AddedToCartSheet/);
});

test('cart item includes quantity, price-change and stock states', async () => {
  const source = await read('../src/shared/ui/Commerce.tsx');
  assert.match(source, /QuantitySelector/);
  assert.match(source, /PriceChangeNotice/);
  assert.match(source, /StockNotice/);
  assert.match(source, /max_quantity/);
});

test('cart badge is capped and does not resize navigation', async () => {
  const source = await read('../src/shared/ui/Commerce.tsx');
  const css = await read('../src/styles/index.css');
  assert.match(source, /value > 9 \? '9\+' : value/);
  assert.match(css, /\.cart-badge/);
  assert.match(css, /position:\s*absolute/);
});

test('mobile navigation exposes five functional routes', async () => {
  const source = await read('../src/shared/ui/BottomNavigation.tsx');
  const css = await read('../src/styles/index.css');
  assert.match(source, /\/favorites/);
  assert.match(source, /\/cart/);
  assert.match(css, /repeat\(5/);
});

test('app supports direct favorites and cart routes', async () => {
  const source = await read('../src/app/App.tsx');
  assert.match(source, /path="\/favorites"/);
  assert.match(source, /path="\/cart"/);
});

test('cart mutations send an idempotency key', async () => {
  const source = await read('../src/shared/api/client.ts');
  assert.match(source, /Idempotency-Key/);
  assert.match(source, /crypto\.randomUUID/);
});

test('reduced motion remains enabled for commerce animations', async () => {
  const css = await read('../src/styles/index.css');
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /transition-duration:\s*\.001ms/);
});
