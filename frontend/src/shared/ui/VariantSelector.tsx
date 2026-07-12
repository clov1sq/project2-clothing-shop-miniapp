import { findVariant } from '../catalog/logic.js';
import type { CatalogColor, CatalogSize, ProductVariant } from '../api/types';

export function ColorSelector({ colors, selected, onSelect }: { colors: CatalogColor[]; selected: string | null; onSelect: (code: string) => void }) {
  return <div className="selector"><div className="selector__label"><span>Колір</span><strong>{colors.find((item) => item.code === selected)?.name || 'Оберіть'}</strong></div><div className="color-options">{colors.map((color) => <button type="button" key={color.code} className={`color-option ${selected === color.code ? 'color-option--active' : ''}`} onClick={() => onSelect(color.code)} aria-label={color.name}><span style={{ background: color.hex_value || 'var(--color-border)' }}/></button>)}</div></div>;
}

export function SizeSelector({ sizes, variants, selectedColor, selectedSize, onSelect }: { sizes: CatalogSize[]; variants: ProductVariant[]; selectedColor: string | null; selectedSize: string | null; onSelect: (code: string) => void }) {
  return <div className="selector"><div className="selector__label"><span>Розмір</span><strong>{selectedSize ? sizes.find((item) => item.code === selectedSize)?.name : 'Оберіть'}</strong></div><div className="size-options">{sizes.map((size) => { const variant = findVariant(variants, selectedColor, size.code) as ProductVariant | null; const disabled = !variant || !variant.is_available; return <button type="button" key={size.code} className={`size-option ${selectedSize === size.code ? 'size-option--active' : ''}`} disabled={disabled} onClick={() => onSelect(size.code)}>{size.name}</button>; })}</div></div>;
}
