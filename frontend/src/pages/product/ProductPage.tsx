import { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate, useParams } from '../../shared/router';

import { catalogApi } from '../../shared/api/client';
import { bindTelegramBack, haptic } from '../../shared/telegram/telegram';
import { Button } from '../../shared/ui/Button';
import { ArrowLeftIcon, BoxIcon, ChevronDownIcon } from '../../shared/ui/Icons';
import { IconButton } from '../../shared/ui/IconButton';
import { Price } from '../../shared/ui/Price';
import { PageSkeleton } from '../../shared/ui/Skeleton';
import { StateScreen } from '../../shared/ui/StateScreen';
import { ColorSelector, SizeSelector } from '../../shared/ui/VariantSelector';
import { NewBadge, SaleBadge } from '../../shared/ui/Badges';

export function ProductPage() {
  const { slug = '' } = useParams();
  const navigate = useNavigate();
  const query = useQuery({ queryKey: ['product', slug], queryFn: () => catalogApi.product(slug), staleTime: 60_000 });
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  useEffect(() => bindTelegramBack(() => navigate(-1)), [navigate]);
  useEffect(() => { if (query.data && !selectedColor) { const firstAvailable = query.data.variants.find((item) => item.is_available) || query.data.variants[0]; setSelectedColor(firstAvailable?.color_code || query.data.colors[0]?.code || null); } }, [query.data, selectedColor]);
  useEffect(() => { setSelectedSize(null); }, [selectedColor]);
  const selectedVariant = useMemo(() => query.data?.variants.find((item) => item.color_code === selectedColor && item.size_code === selectedSize), [query.data, selectedColor, selectedSize]);
  if (query.isLoading) return <PageSkeleton/>;
  if (query.isError || !query.data) return <StateScreen title="Товар не відкрився" description="Можливо, його приховано або з’єднання перервано." actionLabel="Назад" onAction={() => navigate(-1)}/>;
  const product = query.data;
  const visibleMedia = selectedColor ? product.media.filter((item) => !item.variant_id || product.variants.some((variant) => variant.id === item.variant_id && variant.color_code === selectedColor)) : product.media;
  const currentPrice = selectedVariant?.price || product.price;
  const currentCompare = selectedVariant?.compare_at_price || product.compare_at_price;
  return <main className="page product-page"><div className="product-topbar"><IconButton onClick={() => navigate(-1)} aria-label="Назад"><ArrowLeftIcon/></IconButton><span>{product.brand.name}</span><span className="product-topbar__spacer"/></div><div className="product-gallery">{visibleMedia.length ? visibleMedia.map((media) => <figure key={media.id}><img src={media.url} alt={media.alt_text || product.name}/></figure>) : <figure className="product-gallery__fallback">BW</figure>}<div className="product-gallery__count">{Math.max(visibleMedia.length,1)} фото</div></div><section className="product-info"><div className="product-info__badges">{product.is_new ? <NewBadge/> : null}<SaleBadge value={selectedVariant?.discount_percent ?? product.discount_percent}/></div><p className="product-info__brand">{product.brand.name}</p><h1>{product.name}</h1><p className="product-info__model">Модель {product.model_code}</p><Price price={currentPrice} compareAt={currentCompare} currency={product.currency}/>{product.short_description ? <p className="product-info__lead">{product.short_description}</p> : null}<ColorSelector colors={product.colors} selected={selectedColor} onSelect={(code) => { haptic(); setSelectedColor(code); }}/><SizeSelector sizes={product.sizes} variants={product.variants} selectedColor={selectedColor} selectedSize={selectedSize} onSelect={(code) => { haptic(); setSelectedSize(code); }}/>{selectedVariant ? <div className={`availability-note ${selectedVariant.is_available ? 'availability-note--yes' : ''}`}><span/>{selectedVariant.is_available ? `У наявності: ${selectedVariant.available_quantity}` : 'Цей варіант тимчасово відсутній'}</div> : <p className="selection-note">Оберіть колір і розмір, щоб перевірити наявність.</p>}<Button full disabled className="product-preview-button">Кошик буде доступний у наступному оновленні</Button><div className="delivery-preview"><BoxIcon/><div><strong>Доставка — preview</strong><span>Умови та строки з’являться разом із checkout.</span></div></div><details className="product-detail-block" open><summary>Опис <ChevronDownIcon size={19}/></summary><p>{product.description || 'Опис уточнюється.'}</p></details><details className="product-detail-block"><summary>Матеріал <ChevronDownIcon size={19}/></summary><p>{product.material || 'Інформація уточнюється.'}</p></details><details className="product-detail-block"><summary>Догляд <ChevronDownIcon size={19}/></summary><p>{product.care_instructions || 'Дотримуйтеся рекомендацій на етикетці.'}</p></details></section></main>;
}
