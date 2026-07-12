import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { ApiError, adminApi } from '../../shared/api/client';
import type { Brand, Category } from '../../shared/api/types';
import { AppHeader } from '../../shared/ui/AppHeader';
import { Button } from '../../shared/ui/Button';
import { PlusIcon } from '../../shared/ui/Icons';

type TaxonomyType = 'categories' | 'brands';
type TaxonomyItem = Category | Brand;
type TaxonomyResponse = { items: TaxonomyItem[] };

type AdminTaxonomyPageProps = {
  type: TaxonomyType;
};

export function AdminTaxonomyPage({ type }: AdminTaxonomyPageProps) {
  const isCategories = type === 'categories';
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [message, setMessage] = useState<string | null>(null);

  const query = useQuery<TaxonomyResponse>({
    queryKey: ['admin', type],
    queryFn: async (): Promise<TaxonomyResponse> => {
      if (isCategories) {
        return adminApi.categories();
      }
      return adminApi.brands();
    },
  });

  const mutation = useMutation<TaxonomyItem, Error, void>({
    mutationFn: async (): Promise<TaxonomyItem> => {
      if (isCategories) {
        return adminApi.createCategory({ name });
      }
      return adminApi.createBrand({ name });
    },
    onSuccess: () => {
      setName('');
      setMessage(null);
      void queryClient.invalidateQueries({ queryKey: ['admin', type] });
    },
    onError: (error) => {
      setMessage(error instanceof ApiError ? error.message : 'Не вдалося зберегти');
    },
  });

  return (
    <main className="page admin-page">
      <AppHeader
        title={isCategories ? 'Категорії' : 'Бренди'}
        eyebrow="Структура каталогу"
      />
      {message ? <div className="form-message">{message}</div> : null}
      <section className="taxonomy-create">
        <input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder={isCategories ? 'Назва категорії' : 'Назва бренду'}
        />
        <Button
          icon={<PlusIcon size={18} />}
          disabled={name.trim().length < 2}
          loading={mutation.isPending}
          onClick={() => mutation.mutate()}
        >
          Додати
        </Button>
      </section>
      <div className="taxonomy-list">
        {query.data?.items.map((item) => (
          <article key={item.id}>
            <div>
              <strong>{item.name}</strong>
              <span>/{item.slug}</span>
            </div>
            <span className={item.is_active ? 'taxonomy-state taxonomy-state--active' : 'taxonomy-state'}>
              {item.is_active ? 'Активний' : 'Прихований'}
            </span>
          </article>
        ))}
      </div>
    </main>
  );
}
