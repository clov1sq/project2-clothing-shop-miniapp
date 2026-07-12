import type { ReactElement } from 'react';

import type { CatalogColor, CatalogSize, ProductVariant } from '../api/types';
import { findVariant } from '../catalog/logic.js';

type ColorSelectorProps = {
  colors: CatalogColor[];
  selected: string | null;
  onSelect: (code: string) => void;
};

type SizeSelectorProps = {
  sizes: CatalogSize[];
  variants: ProductVariant[];
  selectedColor: string | null;
  selectedSize: string | null;
  onSelect: (code: string) => void;
};

export function ColorSelector({ colors, selected, onSelect }: ColorSelectorProps): ReactElement {
  const selectedColorName = colors.find((item) => item.code === selected)?.name ?? 'Оберіть';

  return (
    <div className="selector">
      <div className="selector__label">
        <span>Колір</span>
        <strong>{selectedColorName}</strong>
      </div>
      <div className="color-options">
        {colors.map((color) => (
          <button
            type="button"
            key={color.code}
            className={`color-option ${selected === color.code ? 'color-option--active' : ''}`}
            onClick={() => onSelect(color.code)}
            aria-label={color.name}
            aria-pressed={selected === color.code}
          >
            <span style={{ background: color.hex_value ?? 'var(--color-border)' }} />
          </button>
        ))}
      </div>
    </div>
  );
}

export function SizeSelector({
  sizes,
  variants,
  selectedColor,
  selectedSize,
  onSelect,
}: SizeSelectorProps): ReactElement {
  const selectedSizeName = selectedSize
    ? sizes.find((item) => item.code === selectedSize)?.name ?? 'Оберіть'
    : 'Оберіть';

  return (
    <div className="selector">
      <div className="selector__label">
        <span>Розмір</span>
        <strong>{selectedSizeName}</strong>
      </div>
      <div className="size-options">
        {sizes.map((size) => {
          const variant = findVariant(variants, selectedColor, size.code) as ProductVariant | null;
          const disabled = !variant || !variant.is_available;

          return (
            <button
              type="button"
              key={size.code}
              className={`size-option ${selectedSize === size.code ? 'size-option--active' : ''}`}
              disabled={disabled}
              onClick={() => onSelect(size.code)}
              aria-pressed={selectedSize === size.code}
            >
              {size.name}
            </button>
          );
        })}
      </div>
    </div>
  );
}
