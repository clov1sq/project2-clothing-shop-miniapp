import { CheckIcon, CloseIcon } from './Icons';
import { IconButton } from './IconButton';

type Props = {
  message: string;
  visible: boolean;
  onClose: () => void;
};

export function Toast({ message, visible, onClose }: Props) {
  return (
    <div aria-live="polite" className={visible ? 'toast toast--visible' : 'toast'} role="status">
      <span className="toast__icon"><CheckIcon size={18} /></span>
      <span>{message}</span>
      <IconButton label="Закрити повідомлення" onClick={onClose}><CloseIcon size={17} /></IconButton>
    </div>
  );
}
