import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../auth/AuthProvider';
import { cartApi } from '../api/client';
import { NavLink } from '../router';
import { CartIcon, GridIcon, HeartIcon, HomeIcon, UserIcon } from './Icons';
import { CartBadge } from './Commerce';

const items = [
  { to: '/', label: 'Головна', icon: HomeIcon },
  { to: '/catalog', label: 'Каталог', icon: GridIcon },
  { to: '/favorites', label: 'Обране', icon: HeartIcon },
  { to: '/cart', label: 'Кошик', icon: CartIcon },
  { to: '/profile', label: 'Профіль', icon: UserIcon },
];

export function BottomNavigation() {
  const { status } = useAuth();
  const cart = useQuery({ queryKey: ['cart'], queryFn: cartApi.get, staleTime: 30_000, enabled: status === 'authenticated' });
  return <nav className="bottom-nav" aria-label="Основна навігація">{items.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `bottom-nav__item ${isActive ? 'bottom-nav__item--active' : ''}`}><span className="bottom-nav__icon"><Icon size={20}/>{to === '/cart' ? <CartBadge value={cart.data?.total_quantity || 0}/> : null}</span><span>{label}</span></NavLink>)}</nav>;
}
