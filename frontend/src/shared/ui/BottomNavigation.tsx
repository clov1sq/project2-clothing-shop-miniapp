import type { AppRoute } from '../../app/routes';
import { BagIcon, GridIcon, HomeIcon, UserIcon } from './Icons';

const items: Array<{ route: AppRoute; label: string; icon: typeof HomeIcon }> = [
  { route: 'home', label: 'Головна', icon: HomeIcon },
  { route: 'catalog', label: 'Каталог', icon: GridIcon },
  { route: 'cart', label: 'Кошик', icon: BagIcon },
  { route: 'profile', label: 'Профіль', icon: UserIcon },
];

type Props = {
  current: AppRoute;
  onNavigate: (route: AppRoute) => void;
};

export function BottomNavigation({ current, onNavigate }: Props) {
  if (current === 'admin') return null;
  return (
    <nav className="bottom-nav" aria-label="Основна навігація">
      {items.map((item) => {
        const Icon = item.icon;
        const active = item.route === current;
        return (
          <button
            aria-current={active ? 'page' : undefined}
            className={active ? 'bottom-nav__item bottom-nav__item--active' : 'bottom-nav__item'}
            key={item.route}
            onClick={() => onNavigate(item.route)}
            type="button"
          >
            <Icon size={22} />
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
