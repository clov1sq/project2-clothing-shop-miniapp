import { ArrowRightIcon } from './Icons';

type Props = {
  title: string;
  eyebrow?: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function SectionHeader({ title, eyebrow, actionLabel, onAction }: Props) {
  return (
    <div className="section-header">
      <div>
        {eyebrow ? <p className="section-header__eyebrow">{eyebrow}</p> : null}
        <h2>{title}</h2>
      </div>
      {actionLabel ? (
        <button className="section-header__action" onClick={onAction} type="button">
          {actionLabel}<ArrowRightIcon size={18} />
        </button>
      ) : null}
    </div>
  );
}
