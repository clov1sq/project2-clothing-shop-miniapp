const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export type ApiMeta = {
  shop_name: string;
  version: string;
  features: Record<string, boolean>;
};

export async function fetchMeta(): Promise<ApiMeta> {
  const response = await fetch(`${apiBaseUrl}/api/meta`);
  if (!response.ok) {
    throw new Error('Не вдалося отримати конфігурацію магазину');
  }
  const payload = await response.json();
  return payload.data as ApiMeta;
}
