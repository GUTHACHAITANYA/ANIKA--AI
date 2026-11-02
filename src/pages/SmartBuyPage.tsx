import React, { useState, useCallback, useRef } from 'react';
import { SmartBuyCard } from '../components/smartbuy/SmartBuyCard';
import { ProductOfferCard } from '../components/smartbuy/ProductOfferCard';
import { smartBuyService } from '../services/smartBuyService';
import type { SmartBuySearchResult, ProviderStatus, SmartBuySearchHistoryItem } from '../types/smartbuy';

// ── Popular search suggestions ─────────────────────────────────────────────
const SUGGESTIONS = [
  'iPhone 16',
  'Samsung Galaxy S24',
  'boAt Airdopes 141',
  'HP Pavilion laptop',
  'Samsung 55 inch 4K TV',
  'OnePlus 12',
  'Sony WH-1000XM5',
  'Laptop under ₹50,000',
  'Smartphone under ₹25,000',
  'Nike running shoes',
];

const SORT_OPTIONS = [
  { value: 'highest_discount', label: '🔥 Highest Discount' },
  { value: 'lowest_price', label: '💸 Lowest Price' },
  { value: 'highest_rating', label: '⭐ Highest Rating' },
  { value: 'newest', label: '🕐 Newest Offer' },
] as const;

type SortOption = typeof SORT_OPTIONS[number]['value'];

// ── Loading stage animation ─────────────────────────────────────────────────
const LOADING_STAGES = [
  '🤖 Parsing your query with AI…',
  '🔍 Searching Amazon India…',
  '📦 Searching Flipkart…',
  '🔵 Checking Croma & Reliance Digital…',
  '📊 Calculating discounts & ranking…',
];

function useLoadingStages(active: boolean) {
  const [stage, setStage] = useState(0);
  const ref = useRef<ReturnType<typeof setInterval> | null>(null);

  React.useEffect(() => {
    if (active) {
      setStage(0);
      ref.current = setInterval(() => {
        setStage((s) => (s + 1) % LOADING_STAGES.length);
      }, 1200);
    } else {
      if (ref.current) clearInterval(ref.current);
    }
    return () => {
      if (ref.current) clearInterval(ref.current);
    };
  }, [active]);

  return LOADING_STAGES[stage];
}

// ── Main page ───────────────────────────────────────────────────────────────
export const SmartBuyPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'finder' | 'advisor'>('finder');

  // Search state
  const [inputQuery, setInputQuery] = useState('');
  const [sort, setSort] = useState<SortOption>('highest_discount');
  const [budget, setBudget] = useState<string>('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  // Results state
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SmartBuySearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // History state
  const [history, setHistory] = useState<SmartBuySearchHistoryItem[]>([]);
  const [providers, setProviders] = useState<ProviderStatus[]>([]);

  const loadingStage = useLoadingStages(loading);

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleSearch = useCallback(
    async (q?: string) => {
      const query = (q ?? inputQuery).trim();
      if (!query) return;
      if (q) setInputQuery(q);

      setLoading(true);
      setError(null);
      setResult(null);
      setShowSuggestions(false);

      try {
        const budgetVal = budget ? parseFloat(budget.replace(/,/g, '')) : undefined;
        const res = await smartBuyService.search(query, {
          sort,
          budget: budgetVal || null,
          platforms: selectedPlatforms.length > 0 ? selectedPlatforms : undefined,
        });
        setResult(res);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Search failed. Please try again.');
      } finally {
        setLoading(false);
      }
    },
    [inputQuery, sort, budget, selectedPlatforms]
  );

  const loadHistory = useCallback(async () => {
    try {
      const data = await smartBuyService.getHistory(10);
      setHistory(data.history);
    } catch {
      /* silent */
    }
  }, []);

  const loadProviders = useCallback(async () => {
    try {
      const data = await smartBuyService.getProviders();
      setProviders(data.providers);
    } catch {
      /* silent */
    }
  }, []);

  React.useEffect(() => {
    loadProviders();
  }, [loadProviders]);

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
            <span className="text-2xl">🛒</span> Smart Buy
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            AI-powered product price & discount comparison across Indian shopping platforms.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-800/60 rounded-xl p-1 w-fit">
        {[
          { key: 'finder', label: '🔍 Price Finder' },
          { key: 'advisor', label: '💡 Affordability Check' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as 'finder' | 'advisor')}
            className={`px-4 py-1.5 rounded-lg text-sm font-semibold transition-all ${
              activeTab === tab.key
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── AFFORDABILITY CHECK TAB ── */}
      {activeTab === 'advisor' && (
        <div>
          <SmartBuyCard />
        </div>
      )}

      {/* ── PRICE FINDER TAB ── */}
      {activeTab === 'finder' && (
        <div className="space-y-5">
          {/* Search bar */}
          <div className="relative">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={inputQuery}
                  onChange={(e) => {
                    setInputQuery(e.target.value);
                    setShowSuggestions(e.target.value.length === 0);
                  }}
                  onFocus={() => setShowSuggestions(inputQuery.length === 0)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSearch();
                    if (e.key === 'Escape') setShowSuggestions(false);
                  }}
                  placeholder='Search any product… e.g. "iPhone 16" or "laptop under ₹60,000"'
                  className="w-full bg-slate-800/80 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors text-sm"
                />
                {inputQuery && (
                  <button
                    onClick={() => { setInputQuery(''); setResult(null); setError(null); setShowSuggestions(true); }}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white text-lg"
                  >
                    ×
                  </button>
                )}
              </div>
              <button
                onClick={() => handleSearch()}
                disabled={loading || !inputQuery.trim()}
                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-bold rounded-xl transition-all shadow-md shadow-indigo-500/20 text-sm"
              >
                {loading ? '⏳' : '🔍 Search'}
              </button>
            </div>

            {/* Suggestions dropdown */}
            {showSuggestions && (
              <div
                className="absolute z-20 top-full left-0 right-0 mt-1 bg-slate-800 border border-slate-700 rounded-xl shadow-xl overflow-hidden"
                onMouseLeave={() => setShowSuggestions(false)}
              >
                <div className="px-3 pt-2 pb-1 text-xs text-slate-500 font-semibold uppercase tracking-wide">
                  Popular Searches
                </div>
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSearch(s)}
                    className="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-slate-700/80 hover:text-white transition-colors flex items-center gap-2"
                  >
                    <span className="text-slate-600">🔍</span> {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Filters bar */}
          <div className="flex flex-wrap gap-3 items-center">
            {/* Budget */}
            <div className="flex items-center gap-2 bg-slate-800/60 border border-slate-700/50 rounded-lg px-3 py-1.5">
              <span className="text-xs text-slate-400">Max Budget ₹</span>
              <input
                type="number"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                placeholder="e.g. 60000"
                className="w-24 bg-transparent text-sm text-white outline-none placeholder-slate-600"
              />
            </div>

            {/* Sort */}
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value as SortOption)}
              className="bg-slate-800/60 border border-slate-700/50 rounded-lg px-3 py-1.5 text-sm text-white outline-none cursor-pointer"
            >
              {SORT_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>

            {/* History toggle */}
            <button
              onClick={() => {
                setShowHistory(!showHistory);
                if (!showHistory) loadHistory();
              }}
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white bg-slate-800/60 border border-slate-700/50 rounded-lg px-3 py-1.5 transition-colors"
            >
              🕐 History
            </button>
          </div>

          {/* Provider status chips */}
          {providers.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {providers.map((p) => (
                <div
                  key={p.platform_id}
                  title={p.message}
                  className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border transition-colors ${
                    p.available
                      ? 'border-emerald-500/40 text-emerald-400 bg-emerald-500/5'
                      : 'border-slate-700 text-slate-500 bg-slate-800/40'
                  }`}
                >
                  <span>{p.logo}</span>
                  <span>{p.platform_name}</span>
                  <span>{p.available ? '●' : '○'}</span>
                </div>
              ))}
            </div>
          )}

          {/* Search History */}
          {showHistory && (
            <div className="bg-slate-800/40 rounded-xl border border-slate-700/40 p-4">
              <h3 className="text-sm font-semibold text-white mb-3">Recent Searches</h3>
              {history.length === 0 ? (
                <p className="text-xs text-slate-500">No search history yet.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {history.map((h) => (
                    <button
                      key={h.id}
                      onClick={() => {
                        setShowHistory(false);
                        handleSearch(h.query);
                      }}
                      className="flex items-center gap-1.5 text-xs bg-slate-700/60 hover:bg-slate-700 border border-slate-600/40 rounded-full px-3 py-1 text-slate-300 hover:text-white transition-colors"
                    >
                      <span>🔍</span> {h.query}
                      {h.top_discount_pct > 0 && (
                        <span className="text-emerald-400 ml-1">({h.top_discount_pct.toFixed(0)}% off)</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-16 gap-4">
              <div className="relative w-16 h-16">
                <div className="absolute inset-0 rounded-full border-4 border-indigo-600/30 animate-ping" />
                <div className="absolute inset-0 rounded-full border-4 border-indigo-600 border-t-transparent animate-spin" />
                <div className="absolute inset-2 rounded-full bg-indigo-600/10 flex items-center justify-center text-2xl">
                  🛒
                </div>
              </div>
              <div className="text-center">
                <p className="text-sm text-indigo-300 font-semibold animate-pulse">{loadingStage}</p>
                <p className="text-xs text-slate-500 mt-1">Searching live platforms for you…</p>
              </div>
            </div>
          )}

          {/* Error state */}
          {!loading && error && (
            <div className="flex flex-col items-center py-12 gap-3">
              <span className="text-4xl">❌</span>
              <p className="text-sm font-semibold text-red-400">Search failed</p>
              <p className="text-xs text-slate-400 text-center max-w-sm">{error}</p>
              <button
                onClick={() => handleSearch()}
                className="mt-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-sm text-white rounded-lg transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Empty state (searched but no results) */}
          {!loading && !error && result && result.total_offers === 0 && (
            <div className="flex flex-col items-center py-12 gap-3">
              <span className="text-4xl">🔍</span>
              <p className="text-sm font-semibold text-slate-300">No results found</p>
              <p className="text-xs text-slate-500 text-center max-w-sm">
                Try a different product name or remove budget filters.
              </p>
            </div>
          )}

          {/* Results */}
          {!loading && !error && result && result.total_offers > 0 && (
            <div className="space-y-4">
              {/* Results header */}
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-sm text-white font-semibold">
                    {result.total_offers} offer{result.total_offers !== 1 ? 's' : ''} found
                  </span>
                  {result.parsed_intent?.product_name && (
                    <span className="text-xs text-slate-400 ml-2">
                      for "{result.parsed_intent.product_name}"
                    </span>
                  )}
                </div>
                {result.offers[0]?.is_demo && (
                  <div className="text-xs text-amber-400 bg-amber-400/10 border border-amber-400/20 rounded-full px-3 py-1">
                    ⚠️ Demo prices shown – connect provider APIs for live data
                  </div>
                )}
              </div>

              {/* AI parsed intent */}
              {result.parsed_intent && (
                <div className="flex flex-wrap gap-2">
                  {result.parsed_intent.category && result.parsed_intent.category !== 'general' && (
                    <span className="text-xs bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 rounded-full px-2.5 py-0.5">
                      📁 {result.parsed_intent.category}
                    </span>
                  )}
                  {result.parsed_intent.brand && (
                    <span className="text-xs bg-purple-600/20 border border-purple-500/30 text-purple-300 rounded-full px-2.5 py-0.5">
                      🏷 {result.parsed_intent.brand}
                    </span>
                  )}
                  {result.parsed_intent.budget_max && (
                    <span className="text-xs bg-emerald-600/20 border border-emerald-500/30 text-emerald-300 rounded-full px-2.5 py-0.5">
                      💰 Budget ≤ ₹{result.parsed_intent.budget_max.toLocaleString('en-IN')}
                    </span>
                  )}
                  {result.parsed_intent.specs?.ram && (
                    <span className="text-xs bg-slate-700 border border-slate-600 text-slate-300 rounded-full px-2.5 py-0.5">
                      🖥 {result.parsed_intent.specs.ram} RAM
                    </span>
                  )}
                </div>
              )}

              {/* Offer cards */}
              <div className="space-y-3">
                {result.offers.map((offer, i) => (
                  <ProductOfferCard key={`${offer.platform_id}-${i}`} offer={offer} rank={i + 1} />
                ))}
              </div>

              {/* Provider check status */}
              {result.providers_checked.length > 0 && (
                <details className="text-xs">
                  <summary className="cursor-pointer text-slate-500 hover:text-slate-300 transition-colors">
                    Provider search details ({result.providers_checked.filter((p) => p.available).length} active)
                  </summary>
                  <div className="mt-2 space-y-1 pl-2 border-l-2 border-slate-700">
                    {result.providers_checked.map((p) => (
                      <div key={p.platform_id} className="flex items-center gap-2 text-slate-500">
                        <span>{p.logo}</span>
                        <span className={p.available ? 'text-emerald-400' : 'text-slate-600'}>
                          {p.platform_name}
                        </span>
                        <span>–</span>
                        <span>{p.message}</span>
                        {p.available && p.offers_found !== undefined && (
                          <span className="text-emerald-400">({p.offers_found} offers)</span>
                        )}
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          )}

          {/* Initial empty state (no search yet) */}
          {!loading && !error && !result && (
            <div className="flex flex-col items-center py-16 gap-4 text-center">
              <div className="text-5xl">🛒</div>
              <div>
                <p className="text-base font-semibold text-white">
                  Find the best deals across Indian platforms
                </p>
                <p className="text-sm text-slate-400 mt-1 max-w-md">
                  Search for any product and we'll compare prices across Amazon, Flipkart, Croma,
                  Reliance Digital and more — sorted by highest discount first.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2 mt-2">
                {SUGGESTIONS.slice(0, 6).map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSearch(s)}
                    className="text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-indigo-500/50 text-slate-300 hover:text-white rounded-full px-3 py-1.5 transition-all"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
