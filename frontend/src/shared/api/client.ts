const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

export type ApiMeta = {
  shop_name: string;
  version: string;
  features: Record<string, boolean>;
};

export async function fetchMeta(): Promise<ApiMeta> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 6000);
  try {
    const response = await fetch(`${apiBaseUrl}/api/meta`, { signal: controller.signal });
    if (!response.ok) {
      throw new Error('Не вдалося отримати конфігурацію магазину');
    }
    const payload = await response.json();
    return payload.data as ApiMeta;
  } finally {
    window.clearTimeout(timeout);
  }
}
