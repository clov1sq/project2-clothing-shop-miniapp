import { BagIcon, ChevronLeftIcon, SearchIcon } from './Icons';
import { BrandMark } from './BrandMark';
import { IconButton } from './IconButton';

type Props = {
  shopName: string;
  back?: boolean;
  onBack?: () => void;
  onPreviewAction?: () => void;
};

export function AppHeader({ shopName, back = false, onBack, onPreviewAction }: Props) {
  return (
    <header className="app-header">
      <div className="app-header__leading">
        {back ? (
          <IconButton label="Назад" onClick={onBack}><ChevronLeftIcon /></IconButton>
        ) : (
          <BrandMark compact shopName={shopName} />
        )}
      </div>
      <div className="app-header__actions">
        <IconButton label="Пошук — preview" onClick={onPreviewAction}><SearchIcon /></IconButton>
        <IconButton badge="0" label="Кошик" onClick={onPreviewAction}><BagIcon /></IconButton>
      </div>
    </header>
  );
}
