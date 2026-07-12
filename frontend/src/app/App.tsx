import type { ReactNode } from 'react';
import { Navigate, Route, Routes, useLocation } from '../shared/router';

import { canAccessAdmin } from '../shared/catalog/logic.js';
import { useAuth } from '../auth/AuthProvider';
import { AdminDashboardPage } from '../pages/admin/AdminDashboardPage';
import { AdminInventoryPage } from '../pages/admin/AdminInventoryPage';
import { AdminProductFormPage } from '../pages/admin/AdminProductFormPage';
import { AdminProductsPage } from '../pages/admin/AdminProductsPage';
import { AdminTaxonomyPage } from '../pages/admin/AdminTaxonomyPage';
import { CatalogPage } from '../pages/catalog/CatalogPage';
import { HomePage } from '../pages/home/HomePage';
import { ProductPage } from '../pages/product/ProductPage';
import { ProfilePage } from '../pages/profile/ProfilePage';
import { AuthErrorScreen, AuthLoadingScreen } from '../shared/ui/AuthScreens';
import { BottomNavigation } from '../shared/ui/BottomNavigation';

function AdminGuard({ children }: { children: ReactNode }) { const {user}=useAuth(); return canAccessAdmin(user) ? <>{children}</> : <Navigate to="/profile" replace/>; }

export function App() {
  const auth=useAuth(); const location=useLocation();
  if(auth.loading) return <AuthLoadingScreen/>;
  if(auth.error || !auth.user) return <AuthErrorScreen message={auth.error || 'Авторизація не завершена'} onRetry={auth.retry}/>;
  const isProduct=location.pathname.startsWith('/products/'); const isAdmin=location.pathname.startsWith('/admin');
  return <div className={`app-shell ${isProduct?'app-shell--detail':''} ${isAdmin?'app-shell--admin':''}`}><Routes><Route path="/" element={<HomePage/>}/><Route path="/catalog" element={<CatalogPage/>}/><Route path="/products/:slug" element={<ProductPage/>}/><Route path="/profile" element={<ProfilePage/>}/><Route path="/admin" element={<AdminGuard><AdminDashboardPage/></AdminGuard>}/><Route path="/admin/products" element={<AdminGuard><AdminProductsPage/></AdminGuard>}/><Route path="/admin/products/new" element={<AdminGuard><AdminProductFormPage/></AdminGuard>}/><Route path="/admin/products/:id" element={<AdminGuard><AdminProductFormPage/></AdminGuard>}/><Route path="/admin/categories" element={<AdminGuard><AdminTaxonomyPage type="categories"/></AdminGuard>}/><Route path="/admin/brands" element={<AdminGuard><AdminTaxonomyPage type="brands"/></AdminGuard>}/><Route path="/admin/inventory" element={<AdminGuard><AdminInventoryPage/></AdminGuard>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes>{!isProduct&&!isAdmin?<BottomNavigation/>:null}</div>;
}
