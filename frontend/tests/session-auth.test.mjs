import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const client = readFileSync(new URL('../src/shared/api/client.ts', import.meta.url), 'utf8');
const authProvider = readFileSync(new URL('../src/auth/AuthProvider.tsx', import.meta.url), 'utf8');
const cartPage = readFileSync(new URL('../src/pages/cart/CartPage.tsx', import.meta.url), 'utf8');
const favoritesPage = readFileSync(new URL('../src/pages/favorites/FavoritesPage.tsx', import.meta.url), 'utf8');
const bottomNavigation = readFileSync(new URL('../src/shared/ui/BottomNavigation.tsx', import.meta.url), 'utf8');
const main = readFileSync(new URL('../src/main.tsx', import.meta.url), 'utf8');
const viteConfig = readFileSync(new URL('../vite.config.ts', import.meta.url), 'utf8');

test('central API client always includes credentials', () => {
  assert.match(client, /credentials:\s*['"]include['"]/);
  assert.equal((client.match(/credentials:\s*['"]include['"]/g) || []).length, 1);
});

test('auth bootstrap verifies cookie through auth me before authenticated state', () => {
  const loginIndex = authProvider.indexOf('await authApi.login');
  const meIndex = authProvider.indexOf('await authApi.me');
  const authenticatedIndex = authProvider.indexOf("setStatus('authenticated')");
  assert.ok(loginIndex >= 0);
  assert.ok(meIndex > loginIndex);
  assert.ok(authenticatedIndex > meIndex);
});

test('protected queries wait for authenticated status', () => {
  for (const source of [cartPage, favoritesPage, bottomNavigation]) {
    assert.match(source, /enabled:\s*status\s*===\s*['"]authenticated['"]/);
  }
});

test('401 refresh is single-flight and original request is retried once', () => {
  assert.match(client, /sessionRefreshPromise/);
  assert.match(client, /response\.status\s*===\s*401/);
  assert.equal((client.match(/await fetch\(`/g) || []).length, 2);
});

test('query retry does not loop on unauthorized responses', () => {
  assert.match(main, /error\.status\s*===\s*401/);
  assert.match(main, /return false/);
});

test('Vite dev and preview proxy API through the frontend origin', () => {
  assert.match(viteConfig, /['"]\/api['"]/);
  assert.match(viteConfig, /server:/);
  assert.match(viteConfig, /preview:/);
  assert.match(viteConfig, /VITE_API_URL/);
});
