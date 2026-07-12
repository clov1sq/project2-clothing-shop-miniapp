import { NavLink } from '../router';
import { GridIcon, HomeIcon, UserIcon } from './Icons';

const items = [
  { to: '/', label: 'Головна', icon: HomeIcon },
  { to: '/catalog', label: 'Каталог', icon: GridIcon },
  { to: '/profile', label: 'Профіль', icon: UserIcon },
];

export function BottomNavigation() {
  return <nav className="bottom-nav" aria-label="Основна навігація">{items.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `bottom-nav__item ${isActive ? 'bottom-nav__item--active' : ''}`}><Icon size={21}/><span>{label}</span></NavLink>)}</nav>;
}
