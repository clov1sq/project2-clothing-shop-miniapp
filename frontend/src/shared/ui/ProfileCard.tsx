import { UserIcon } from './Icons';
import { StatusBadge } from './StatusBadge';

type Props = {
  name: string;
  username?: string;
};

export function ProfileCard({ name, username }: Props) {
  return (
    <section className="profile-card">
      <div className="profile-card__avatar" aria-hidden="true"><UserIcon size={28} /></div>
      <div className="profile-card__identity">
        <p className="profile-card__label">Профіль покупця</p>
        <h1>{name}</h1>
        <p>{username ? `@${username}` : 'Telegram username не вказано'}</p>
      </div>
      <StatusBadge tone="info">PREVIEW</StatusBadge>
    </section>
  );
}
