import type {
  Brand,
  CatalogMeta,
  CatalogResponse,
  Category,
  HomeResponse,
  ProductDetailData,
  User,
  FavoritesResponse,
  CartData,
} from './types';

const apiBaseUrl = '';

export class ApiError extends Error {
  code: string;
  status: number;
  details?: Record<string, unknown>;

  constructor(code: string, message: string, status: number, details?: Record<string, unknown>) {
    super(message);
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

type ApiEnvelope<T> =
  | { ok: true; data: T }
  | { ok: false; error: { code: string; message: string; details?: Record<string, unknown> } };

type SessionRefreshHandler = () => Promise<void>;
type ApiRequestOptions = RequestInit & { skipAuthRefresh?: boolean };

let sessionRefreshHandler: SessionRefreshHandler | null = null;
let sessionRefreshPromise: Promise<void> | null = null;

export function setSessionRefreshHandler(handler: SessionRefreshHandler | null): () => void {
  sessionRefreshHandler = handler;
  return () => {
    if (sessionRefreshHandler === handler) sessionRefreshHandler = null;
  };
}

async function refreshSessionOnce(): Promise<void> {
  if (!sessionRefreshHandler) throw new ApiError('AUTH_REQUIRED', 'Потрібна авторизація', 401);
  if (!sessionRefreshPromise) {
    sessionRefreshPromise = sessionRefreshHandler().finally(() => {
      sessionRefreshPromise = null;
    });
  }
  await sessionRefreshPromise;
}

function buildRequest(options: RequestInit): RequestInit {
  return {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  };
}

async function parseResponse<T>(response: Response): Promise<T> {
  let payload: ApiEnvelope<T>;
  try {
    payload = (await response.json()) as ApiEnvelope<T>;
  } catch {
    throw new ApiError(
      'NETWORK_RESPONSE_INVALID',
      'Сервер повернув некоректну відповідь',
      response.status,
    );
  }
  if (!response.ok || !payload.ok) {
    const error =
      'error' in payload
        ? payload.error
        : { code: 'REQUEST_FAILED', message: 'Не вдалося виконати запит' };
    throw new ApiError(error.code, error.message, response.status, error.details);
  }
  return payload.data;
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { skipAuthRefresh = false, ...requestOptions } = options;
  const request = buildRequest(requestOptions);
  let response = await fetch(`${apiBaseUrl}${path}`, request);

  if (response.status === 401 && !skipAuthRefresh && sessionRefreshHandler) {
    await refreshSessionOnce();
    response = await fetch(`${apiBaseUrl}${path}`, request);
  }

  return parseResponse<T>(response);
}

export const authApi = {
  login: (initData: string) =>
    apiRequest<{ user: User }>('/api/v1/auth/telegram', {
      method: 'POST',
      body: JSON.stringify({ init_data: initData }),
      skipAuthRefresh: true,
    }),
  me: () => apiRequest<{ user: User }>('/api/v1/auth/me', { skipAuthRefresh: true }),
  logout: () =>
    apiRequest<{ logged_out: boolean }>('/api/v1/auth/logout', {
      method: 'POST',
      skipAuthRefresh: true,
    }),
};

export const catalogApi = {
  home: () => apiRequest<HomeResponse>('/api/v1/home'),
  meta: () => apiRequest<CatalogMeta>('/api/v1/catalog/meta'),
  products: (params: URLSearchParams) =>
    apiRequest<CatalogResponse>(`/api/v1/products?${params.toString()}`),
  product: (slug: string) =>
    apiRequest<ProductDetailData>(`/api/v1/products/${encodeURIComponent(slug)}`),
  categories: () => apiRequest<{ items: Category[] }>('/api/v1/categories'),
  brands: () => apiRequest<{ items: Brand[] }>('/api/v1/brands'),
};

export const adminApi = {
  dashboard: () =>
    apiRequest<{ products_by_status: Record<string, number>; low_stock_variants: number }>(
      '/api/v1/admin/dashboard',
    ),
  products: (params = new URLSearchParams()) =>
    apiRequest<{
      items: ProductDetailData[];
      pagination: { page: number; limit: number; total: number };
    }>(`/api/v1/admin/products?${params.toString()}`),
  product: (id: string) => apiRequest<ProductDetailData>(`/api/v1/admin/products/${id}`),
  createProduct: (payload: Record<string, unknown>) =>
    apiRequest<ProductDetailData>('/api/v1/admin/products', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateProduct: (id: string, payload: Record<string, unknown>) =>
    apiRequest<ProductDetailData>(`/api/v1/admin/products/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  publishProduct: (id: string) =>
    apiRequest<ProductDetailData>(`/api/v1/admin/products/${id}/publish`, { method: 'POST' }),
  archiveProduct: (id: string) =>
    apiRequest<ProductDetailData>(`/api/v1/admin/products/${id}/archive`, { method: 'POST' }),
  categories: () => apiRequest<{ items: Category[] }>('/api/v1/admin/categories'),
  createCategory: (payload: Record<string, unknown>) =>
    apiRequest<Category>('/api/v1/admin/categories', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateCategory: (id: string, payload: Record<string, unknown>) =>
    apiRequest<Category>(`/api/v1/admin/categories/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  brands: () => apiRequest<{ items: Brand[] }>('/api/v1/admin/brands'),
  createBrand: (payload: Record<string, unknown>) =>
    apiRequest<Brand>('/api/v1/admin/brands', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateBrand: (id: string, payload: Record<string, unknown>) =>
    apiRequest<Brand>(`/api/v1/admin/brands/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  options: () =>
    apiRequest<{
      colors: Array<{
        id: string;
        name: string;
        code: string;
        hex_value: string | null;
        is_active: boolean;
      }>;
      sizes: Array<{ id: string; name: string; code: string; is_active: boolean }>;
    }>('/api/v1/admin/options'),
  createVariant: (productId: string, payload: Record<string, unknown>) =>
    apiRequest<ProductDetailData>(`/api/v1/admin/products/${productId}/variants`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateVariant: (variantId: string, payload: Record<string, unknown>) =>
    apiRequest<ProductDetailData>(`/api/v1/admin/variants/${variantId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  archiveVariant: (variantId: string) =>
    apiRequest<ProductDetailData>(`/api/v1/admin/variants/${variantId}/archive`, {
      method: 'POST',
    }),
  adjustInventory: (variantId: string, payload: Record<string, unknown>) =>
    apiRequest<{
      variant_id: string;
      quantity_on_hand: number;
      quantity_reserved: number;
      available_quantity: number;
    }>(`/api/v1/admin/variants/${variantId}/inventory`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  addMedia: (productId: string, payload: Record<string, unknown>) =>
    apiRequest<ProductDetailData>(`/api/v1/admin/products/${productId}/media`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  deleteMedia: (mediaId: string) =>
    apiRequest<ProductDetailData>(`/api/v1/admin/media/${mediaId}`, { method: 'DELETE' }),
};

export const favoritesApi = {
  list: (page = 1) =>
    apiRequest<FavoritesResponse>(`/api/v1/favorites?page=${page}&limit=40`),
  add: (productId: string) =>
    apiRequest<{ product_id: string; is_favorite: boolean }>(
      `/api/v1/favorites/${productId}`,
      { method: 'POST' },
    ),
  remove: (productId: string) =>
    apiRequest<{ product_id: string; is_favorite: boolean }>(
      `/api/v1/favorites/${productId}`,
      { method: 'DELETE' },
    ),
};

export const cartApi = {
  get: () => apiRequest<CartData>('/api/v1/cart'),
  add: (variantId: string, quantity = 1, idempotencyKey = crypto.randomUUID()) =>
    apiRequest<CartData>('/api/v1/cart/items', {
      method: 'POST',
      headers: { 'Idempotency-Key': idempotencyKey },
      body: JSON.stringify({ variant_id: variantId, quantity }),
    }),
  update: (itemId: string, quantity: number) =>
    apiRequest<CartData>(`/api/v1/cart/items/${itemId}`, {
      method: 'PATCH',
      body: JSON.stringify({ quantity }),
    }),
  remove: (itemId: string) =>
    apiRequest<CartData>(`/api/v1/cart/items/${itemId}`, { method: 'DELETE' }),
  clear: () => apiRequest<CartData>('/api/v1/cart', { method: 'DELETE' }),
  refresh: () => apiRequest<CartData>('/api/v1/cart/refresh', { method: 'POST' }),
};
