import { Link } from '../../shared/router';

import { useAuth } from '../../auth/AuthProvider';
import { AppHeader } from '../../shared/ui/AppHeader';
import { ArrowRightIcon, ShieldIcon, UserIcon } from '../../shared/ui/Icons';

export function ProfilePage() {
  const { user } = useAuth();
  if (!user) return null;
  return <main className="page profile-page"><AppHeader title="Профіль" eyebrow="Ваш акаунт"/><section className="profile-card"><div className="profile-card__avatar">{user.first_name.slice(0,1).toUpperCase()}</div><div><h2>{user.display_name}</h2><p>{user.username ? `@${user.username}` : 'Telegram username не вказано'}</p></div></section><section className="profile-section"><h3>Магазин</h3><div className="profile-row"><UserIcon/><div><strong>Telegram ID</strong><span>{user.telegram_id}</span></div></div><div className="profile-row"><ShieldIcon/><div><strong>Роль</strong><span>{user.is_admin ? 'Адміністратор' : 'Користувач'}</span></div></div></section>{user.is_admin ? <Link to="/admin" className="admin-entry"><div><span>ADMIN SPACE</span><strong>Керування каталогом</strong><p>Товари, фото, варіанти та залишки.</p></div><ArrowRightIcon/></Link> : null}<section className="profile-preview"><h3>Що далі</h3><p>Кошик, замовлення й оплата будуть додані в наступних накопичувальних версіях.</p></section></main>;
}
