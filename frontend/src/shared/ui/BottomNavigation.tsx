import type { AppRoute } from '../../app/routes';

const items: Array<{ route: AppRoute; label: string; icon: string }> = [
  { route: 'home', label: 'Головне', icon: '⌂' },
  { route: 'catalog', label: 'Каталог', icon: '◇' },
  { route: 'cart', label: 'Кошик', icon: '◌' },
  { route: 'orders', label: 'Замовлення', icon: '☰' },
];

type Props = {
  current: AppRoute;
  onNavigate: (route: AppRoute) => void;
};

export function BottomNavigation({ current, onNavigate }: Props) {
  return (
    <nav className="bottom-nav" aria-label="Основна навігація">
      {items.map((item) => (
        <button
          key={item.route}
          type="button"
          className={item.route === current ? 'bottom-nav__item bottom-nav__item--active' : 'bottom-nav__item'}
          onClick={() => onNavigate(item.route)}
        >
          <span aria-hidden="true">{item.icon}</span>
          <span>{item.label}</span>
        </button>
      ))}
    </nav>
  );
}
