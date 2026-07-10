import { useEffect, useState } from 'react';

import { fetchMeta } from '../shared/api/client';
import { initTelegramShell } from '../shared/telegram/telegram';
import { BottomNavigation } from '../shared/ui/BottomNavigation';
import { CartPage } from '../pages/cart/CartPage';
import { CatalogPage } from '../pages/catalog/CatalogPage';
import { HomePage } from '../pages/home/HomePage';
import { OrdersPage } from '../pages/orders/OrdersPage';
import { type AppRoute, readRouteFromHash, setRouteHash } from './routes';

const fallbackShopName = import.meta.env.VITE_SHOP_NAME || 'BlueWear';

export function App() {
  const [route, setRoute] = useState<AppRoute>(() => readRouteFromHash());
  const [shopName, setShopName] = useState(fallbackShopName);

  useEffect(() => {
    initTelegramShell();
  }, []);

  useEffect(() => {
    const onHashChange = () => setRoute(readRouteFromHash());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  useEffect(() => {
    fetchMeta()
      .then((meta) => setShopName(meta.shop_name || fallbackShopName))
      .catch(() => setShopName(fallbackShopName));
  }, []);

  const navigate = (nextRoute: AppRoute) => {
    if (nextRoute === route) return;
    setRouteHash(nextRoute);
  };

  return (
    <div className="app-shell">
      {route === 'home' && <HomePage shopName={shopName} />}
      {route === 'catalog' && <CatalogPage />}
      {route === 'cart' && <CartPage />}
      {route === 'orders' && <OrdersPage />}
      <BottomNavigation current={route} onNavigate={navigate} />
    </div>
  );
}
