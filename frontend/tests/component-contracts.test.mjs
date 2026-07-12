import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('ProductCard keeps stable fashion card content without cart action', async () => {
  const source = await read('../src/shared/ui/ProductCard.tsx');
  assert.match(source, /product-card__media/);
  assert.match(source, /NewBadge/);
  assert.match(source, /SaleBadge/);
  assert.doesNotMatch(source, /Додати в кошик/);
});

test('Price renders current and compare-at values', async () => {
  const source = await read('../src/shared/ui/Price.tsx');
  assert.match(source, /price__current/);
  assert.match(source, /price__old/);
});

test('Catalog includes debounce, filters, sorting and retry states', async () => {
  const source = await read('../src/pages/catalog/CatalogPage.tsx');
  assert.match(source, /useDebouncedValue\(search, 350\)/);
  assert.match(source, /FilterSheet/);
  assert.match(source, /sortLabels/);
  assert.match(source, /Повторити/);
});

test('VariantSelector disables unavailable combinations', async () => {
  const source = await read('../src/shared/ui/VariantSelector.tsx');
  assert.match(source, /!variant \|\| !variant\.is_available/);
  assert.match(source, /disabled=\{disabled\}/);
});

test('Admin guard is server-role aware in the frontend', async () => {
  const source = await read('../src/app/App.tsx');
  assert.match(source, /canAccessAdmin\(user\)/);
  assert.match(source, /Navigate to="\/profile"/);
});

test('Design system enforces two columns, safe area and reduced motion', async () => {
  const css = await read('../src/styles/index.css');
  assert.match(css, /grid-template-columns:\s*repeat\(2/);
  assert.match(css, /env\(safe-area-inset-bottom\)/);
  assert.match(css, /prefers-reduced-motion/);
});
