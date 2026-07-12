import { CloseIcon, SearchIcon } from './Icons';
import { IconButton } from './IconButton';

export function SearchInput({ value, onChange, placeholder = 'Пошук товарів' }: { value: string; onChange: (value: string) => void; placeholder?: string }) {
  return <label className="search-input"><SearchIcon size={20}/><input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} aria-label={placeholder}/>{value ? <IconButton type="button" onClick={() => onChange('')} aria-label="Очистити пошук"><CloseIcon size={18}/></IconButton> : null}</label>;
}
