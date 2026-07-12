import { BrandMark } from './BrandMark';
import { Button } from './Button';
import { HomeSkeleton } from './Skeleton';

export function AuthLoadingScreen({ shopName }: { shopName: string }) {
  return (
    <div className="auth-screen">
      <div className="auth-screen__brand"><BrandMark shopName={shopName} /></div>
      <HomeSkeleton />
    </div>
  );
}

export function AuthErrorScreen({ onRetry }: { onRetry: () => void }) {
  return (
    <main className="auth-error-screen">
      <div className="auth-error-screen__code">401</div>
      <p className="auth-error-screen__eyebrow">Telegram authorization</p>
      <h1>Не вдалося підтвердити вхід</h1>
      <p>Закрийте Mini App, відкрийте його знову через бота та повторіть спробу.</p>
      <Button fullWidth onClick={onRetry}>Спробувати ще раз</Button>
    </main>
  );
}
