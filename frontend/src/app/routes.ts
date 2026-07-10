export type AppRoute = 'home' | 'catalog' | 'cart' | 'orders';

const allowedRoutes: AppRoute[] = ['home', 'catalog', 'cart', 'orders'];

export function readRouteFromHash(): AppRoute {
  const value = window.location.hash.replace('#/', '') as AppRoute;
  return allowedRoutes.includes(value) ? value : 'home';
}

export function setRouteHash(route: AppRoute): void {
  window.location.hash = `/${route}`;
}
