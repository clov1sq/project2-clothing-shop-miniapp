import assert from 'node:assert/strict';
import test from 'node:test';

import {
  availableSizeCodes,
  calculateDiscount,
  canAccessAdmin,
  countActiveCatalogFilters,
  findVariant,
  formatCatalogPrice,
} from '../src/shared/catalog/logic.js';

test('formats Ukrainian catalog price', () => {
  assert.match(formatCatalogPrice('2499'), /2\s?499/);
});

test('discount only exists for a real lower price', () => {
  assert.equal(calculateDiscount('800', '1000'), 20);
  assert.equal(calculateDiscount('1000', '1000'), null);
  assert.equal(calculateDiscount('1200', '1000'), null);
});

test('variant logic never invents unavailable combinations', () => {
  const variants = [
    { color_code: 'black', size_code: 'M', is_available: true, id: '1' },
    { color_code: 'black', size_code: 'L', is_available: false, id: '2' },
    { color_code: 'blue', size_code: 'L', is_available: true, id: '3' },
  ];
  assert.deepEqual(availableSizeCodes(variants, 'black'), ['M']);
  assert.equal(findVariant(variants, 'blue', 'M'), null);
  assert.equal(findVariant(variants, 'blue', 'L')?.id, '3');
});

test('filter counter ignores false toggles', () => {
  const params = new URLSearchParams('brand=northline&sale=true&new=false');
  assert.equal(countActiveCatalogFilters(params), 2);
});

test('admin guard is role based', () => {
  assert.equal(canAccessAdmin({ is_admin: true }), true);
  assert.equal(canAccessAdmin({ is_admin: false }), false);
  assert.equal(canAccessAdmin(null), false);
});
