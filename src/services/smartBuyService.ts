import { SmartBuySearchResult, ProviderStatus, SmartBuySearchHistoryItem } from '../types/smartbuy';

// Detect production vs development
const API_BASE = ((import.meta as any).env?.VITE_API_URL as string) || '';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await resp.json();
  if (!data.success && resp.status >= 400) {
    throw new Error(data.error || `HTTP ${resp.status}`);
  }
  return data as T;
}

export const smartBuyService = {
  /** Search for products across all configured platforms */
  async search(
    query: string,
    options?: {
      sort?: 'highest_discount' | 'lowest_price' | 'highest_rating' | 'newest';
      budget?: number | null;
      platforms?: string[];
    }
  ): Promise<SmartBuySearchResult> {
    const params = new URLSearchParams({ q: query });
    if (options?.sort) params.set('sort', options.sort);
    if (options?.budget) params.set('budget', String(options.budget));
    if (options?.platforms?.length) params.set('platform', options.platforms.join(','));

    return apiFetch<SmartBuySearchResult>(`/api/smart-buy/search?${params}`);
  },

  /** Get status of all registered shopping platform providers */
  async getProviders(): Promise<{ providers: ProviderStatus[]; total: number }> {
    return apiFetch('/api/smart-buy/providers');
  },

  /** Get recent search history */
  async getHistory(limit = 20): Promise<{ history: SmartBuySearchHistoryItem[]; total: number }> {
    return apiFetch(`/api/smart-buy/history?limit=${limit}`);
  },

  /** Compare a list of offer dicts */
  async compare(
    offers: unknown[],
    sortBy = 'highest_discount'
  ): Promise<{ offers: unknown[]; total: number }> {
    return apiFetch('/api/smart-buy/compare', {
      method: 'POST',
      body: JSON.stringify({ offers, sort_by: sortBy }),
    });
  },
};

