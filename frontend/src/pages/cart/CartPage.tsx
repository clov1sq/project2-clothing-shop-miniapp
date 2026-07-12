import type { AppRoute } from '../../app/routes';
import { AppHeader } from '../../shared/ui/AppHeader';
import { EmptyState } from '../../shared/ui/EmptyState';
import { BagIcon } from '../../shared/ui/Icons';

type Props = {
  shopName: string;
  onNavigate: (route: AppRoute) => void;
  onPreviewAction: () => void;
};

export function CartPage({ shopName, onNavigate, onPreviewAction }: Props) {
  return (
    <main className="page">
      <AppHeader onPreviewAction={onPreviewAction} shopName={shopName} />
      <div className="page-title-block">
        <p className="page-kicker">Ваш вибір</p>
        <h1>Кошик</h1>
      </div>
      <EmptyState
        actionLabel="Перейти до каталогу"
        description="У v2 кошик ще не підключений до бази. Демонстраційні товари доступні в каталозі."
        icon={<BagIcon size={30} />}
        onAction={() => onNavigate('catalog')}
        title="Тут поки порожньо"
      />
    </main>
  );
}
