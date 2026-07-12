export type AppRoute = 'home' | 'catalog' | 'cart' | 'profile' | 'admin';

const allowedRoutes: AppRoute[] = ['home', 'catalog', 'cart', 'profile', 'admin'];

export function readRouteFromHash(): AppRoute {
  const value = window.location.hash.replace('#/', '') as AppRoute;
  return allowedRoutes.includes(value) ? value : 'home';
}

export function setRouteHash(route: AppRoute): void {
  window.location.hash = `/${route}`;
}
