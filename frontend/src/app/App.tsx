import { useEffect, useMemo, useState } from 'react';

import { AdminPage } from '../pages/admin/AdminPage';
import { CartPage } from '../pages/cart/CartPage';
import { CatalogPage } from '../pages/catalog/CatalogPage';
import { HomePage } from '../pages/home/HomePage';
import { ProfilePage } from '../pages/profile/ProfilePage';
import { fetchMeta } from '../shared/api/client';
import { getTelegramUser, getTelegramWebApp, hapticTap, initTelegramShell } from '../shared/telegram/telegram';
import { AuthErrorScreen, AuthLoadingScreen } from '../shared/ui/AuthScreens';
import { BottomNavigation } from '../shared/ui/BottomNavigation';
import { Toast } from '../shared/ui/Toast';
import { type AppRoute, readRouteFromHash, setRouteHash } from './routes';

const fallbackShopName = import.meta.env.VITE_SHOP_NAME || 'BlueWear';

export function App() {
  const [route, setRoute] = useState<AppRoute>(() => readRouteFromHash());
  const [shopName, setShopName] = useState(fallbackShopName);
  const [authState, setAuthState] = useState<'loading' | 'ready' | 'error'>(() =>
    new URLSearchParams(window.location.search).get('auth') === 'error' ? 'error' : 'loading',
  );
  const [toastVisible, setToastVisible] = useState(false);
  const user = useMemo(() => getTelegramUser(), []);

  useEffect(() => {
    initTelegramShell();
    if (authState !== 'error') {
      const timer = window.setTimeout(() => setAuthState('ready'), 520);
      return () => window.clearTimeout(timer);
    }
    return undefined;
  }, [authState]);

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

  useEffect(() => {
    const backButton = getTelegramWebApp()?.BackButton;
    if (!backButton) return undefined;
    const onBack = () => setRouteHash(route === 'admin' ? 'profile' : 'home');
    if (route === 'admin') {
      backButton.show();
      backButton.onClick(onBack);
    } else {
      backButton.hide();
    }
    return () => backButton.offClick(onBack);
  }, [route]);

  const navigate = (nextRoute: AppRoute) => {
    if (nextRoute === route) return;
    hapticTap();
    setRouteHash(nextRoute);
  };

  const showPreviewToast = () => {
    hapticTap();
    setToastVisible(true);
    window.setTimeout(() => setToastVisible(false), 2600);
  };

  if (authState === 'loading') return <AuthLoadingScreen shopName={shopName} />;
  if (authState === 'error') {
    return <AuthErrorScreen onRetry={() => { window.history.replaceState({}, '', window.location.pathname); setAuthState('loading'); }} />;
  }

  return (
    <div className="app-shell">
      {route === 'home' && <HomePage onNavigate={navigate} onPreviewAction={showPreviewToast} shopName={shopName} />}
      {route === 'catalog' && <CatalogPage onPreviewAction={showPreviewToast} shopName={shopName} />}
      {route === 'cart' && <CartPage onNavigate={navigate} onPreviewAction={showPreviewToast} shopName={shopName} />}
      {route === 'profile' && <ProfilePage onNavigate={navigate} onPreviewAction={showPreviewToast} shopName={shopName} user={user} />}
      {route === 'admin' && <AdminPage onNavigate={navigate} shopName={shopName} />}
      <BottomNavigation current={route} onNavigate={navigate} />
      <Toast message="Це preview-елемент. Функцію буде підключено в наступній версії." onClose={() => setToastVisible(false)} visible={toastVisible} />
    </div>
  );
}
