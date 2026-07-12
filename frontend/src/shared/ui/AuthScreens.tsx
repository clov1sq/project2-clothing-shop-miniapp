import { Button } from './Button';
import { BrandMark } from './BrandMark';

export function AuthLoadingScreen() { return <main className="auth-screen"><BrandMark/><div className="auth-screen__pulse"/><h1>Відкриваємо магазин</h1><p>Перевіряємо Telegram-сесію та готуємо каталог.</p></main>; }
export function AuthErrorScreen({ message, onRetry }: { message: string; onRetry: () => void }) { return <main className="auth-screen"><BrandMark/><div className="auth-screen__error">!</div><h1>Не вдалося увійти</h1><p>{message}</p><Button onClick={onRetry}>Спробувати ще раз</Button></main>; }
