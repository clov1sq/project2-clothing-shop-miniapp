import type { AppRoute } from '../../app/routes';
import { AppHeader } from '../../shared/ui/AppHeader';
import { ArrowRightIcon, BagIcon, GridIcon, UserIcon } from '../../shared/ui/Icons';
import { StatusBadge } from '../../shared/ui/StatusBadge';

type Props = {
  shopName: string;
  onNavigate: (route: AppRoute) => void;
};

export function AdminPage({ shopName, onNavigate }: Props) {
  return (
    <main className="page page--admin">
      <AppHeader back onBack={() => onNavigate('profile')} shopName={shopName} />
      <header className="admin-header">
        <div>
          <p className="page-kicker">Administration · Preview</p>
          <h1>Огляд магазину</h1>
        </div>
        <StatusBadge tone="info">DEMO DATA</StatusBadge>
      </header>

      <section className="admin-stats">
        <article><span><BagIcon /></span><p>Замовлення</p><strong>0</strong><small>Після checkout</small></article>
        <article><span><GridIcon /></span><p>Товари</p><strong>6</strong><small>Mock preview</small></article>
        <article><span><UserIcon /></span><p>Клієнти</p><strong>1</strong><small>Поточний preview</small></article>
      </section>

      <section className="admin-panel">
        <div className="admin-panel__header">
          <div><p>Стан Foundation</p><h2>Готовність модулів</h2></div>
          <StatusBadge tone="success">ONLINE</StatusBadge>
        </div>
        <div className="admin-progress-row"><span>Frontend shell</span><strong>100%</strong></div>
        <div className="admin-progress"><span style={{ width: '100%' }} /></div>
        <div className="admin-progress-row"><span>Preview catalog</span><strong>100%</strong></div>
        <div className="admin-progress"><span style={{ width: '100%' }} /></div>
        <div className="admin-progress-row"><span>Real products API</span><strong>0%</strong></div>
        <div className="admin-progress"><span style={{ width: '4%' }} /></div>
      </section>

      <section className="admin-list">
        <button type="button">
          <span>Товари та варіанти</span><StatusBadge>PREVIEW</StatusBadge><ArrowRightIcon size={19} />
        </button>
        <button type="button">
          <span>Замовлення</span><StatusBadge>PREVIEW</StatusBadge><ArrowRightIcon size={19} />
        </button>
        <button type="button">
          <span>Медіа та банери</span><StatusBadge>PREVIEW</StatusBadge><ArrowRightIcon size={19} />
        </button>
      </section>
    </main>
  );
}
