import { useEffect, useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { favoritesApi } from '../api/client';
import { haptic, notifyHaptic } from '../telegram/telegram';
import { HeartIcon } from './Icons';

export function FavoriteButton({ productId, initial, disabled = false, onChanged }: { productId: string; initial: boolean; disabled?: boolean; onChanged?: (value: boolean) => void }) {
  const client = useQueryClient();
  const [active, setActive] = useState(initial);
  useEffect(() => setActive(initial), [initial]);
  const mutation = useMutation({
    mutationFn: (next: boolean) => next ? favoritesApi.add(productId) : favoritesApi.remove(productId),
    onMutate: (next) => { setActive(next); onChanged?.(next); haptic('light'); return { previous: active }; },
    onError: (_error, _next, context) => { const previous = context?.previous ?? initial; setActive(previous); onChanged?.(previous); notifyHaptic('error'); },
    onSuccess: () => notifyHaptic('success'),
    onSettled: () => {
      void client.invalidateQueries({ queryKey: ['favorites'] });
      void client.invalidateQueries({ queryKey: ['products'] });
      void client.invalidateQueries({ queryKey: ['product'] });
      void client.invalidateQueries({ queryKey: ['home'] });
    },
  });
  return <button type="button" className={`favorite-button ${active ? 'favorite-button--active' : ''}`} aria-label={active ? 'Видалити з обраного' : 'Додати до обраного'} aria-pressed={active} disabled={disabled || mutation.isPending} onClick={(event) => { event.preventDefault(); event.stopPropagation(); mutation.mutate(!active); }}><HeartIcon size={21} filled={active}/></button>;
}
