import type { AppRoute } from '../../app/routes';
import type { TelegramUser } from '../../shared/telegram/telegram';
import { AppHeader } from '../../shared/ui/AppHeader';
import { ArrowRightIcon, BagIcon, SettingsIcon, ShieldIcon } from '../../shared/ui/Icons';
import { ProfileCard } from '../../shared/ui/ProfileCard';
import { StatusBadge } from '../../shared/ui/StatusBadge';

type Props = {
  shopName: string;
  user: TelegramUser | null;
  onNavigate: (route: AppRoute) => void;
  onPreviewAction: () => void;
};

export function ProfilePage({ shopName, user, onNavigate, onPreviewAction }: Props) {
  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || 'Гість BlueWear';
  return (
    <main className="page">
      <AppHeader onPreviewAction={onPreviewAction} shopName={shopName} />
      <ProfileCard name={fullName} username={user?.username} />

      <section className="profile-section">
        <div className="profile-section__header">
          <h2>Останнє замовлення</h2>
          <StatusBadge tone="neutral">PREVIEW</StatusBadge>
        </div>
        <article className="order-preview-card">
          <div className="order-preview-card__icon"><BagIcon /></div>
          <div>
            <strong>Замовлень ще немає</strong>
            <p>Історія з’явиться після підключення checkout.</p>
          </div>
          <ArrowRightIcon size={19} />
        </article>
      </section>

      <section className="profile-menu" aria-label="Налаштування профілю">
        <button onClick={onPreviewAction} type="button">
          <span className="profile-menu__icon"><ShieldIcon /></span>
          <span><strong>Приватність і дані</strong><small>Preview стану</small></span>
          <ArrowRightIcon size={19} />
        </button>
        <button onClick={() => onNavigate('admin')} type="button">
          <span className="profile-menu__icon"><SettingsIcon /></span>
          <span><strong>Admin preview</strong><small>Окремий оформлений маршрут</small></span>
          <ArrowRightIcon size={19} />
        </button>
      </section>
    </main>
  );
}
