
// ── Smart Buy – Price Comparison Types ──────────────────────────────────────

export interface ProductOffer {
  platform_id: string;
  platform_name: string;
  platform_logo: string;
  website_url: string;
  product_title: string;
  product_url: string;
  image_url: string;
  brand: string;
  model_name: string;
  category: string;
  seller_name: string;
  // Pricing
  original_price: number;
  selling_price: number;
  discount_percentage: number;
  // Guaranteed savings
  coupon_discount: number;
  // Conditional savings (never subtracted from final_payable)
  bank_discount: number;
  cashback: number;
  // Delivery & final
  delivery_fee: number;
  final_payable_price: number;
  // Quality signals
  rating: number;
  reviews_count: number;
  // Status
  availability: 'in_stock' | 'out_of_stock' | 'limited_stock';
  offer_details: string;
  variant_attributes: Record<string, string>;
  variant_warning: string[];
  is_verified: boolean;
  is_demo: boolean;
  is_best_discount: boolean;
  last_checked: string;
}

export interface SmartBuySearchResult {
  query: string;
  parsed_intent: {
    product_name: string;
    category: string;
    brand: string;
    model: string;
    budget_max: number | null;
    specs: Record<string, string | null>;
    sort: string;
  };
  offers: ProductOffer[];
  providers_checked: ProviderStatus[];
  total_offers: number;
  search_id: number | null;
}

export interface ProviderStatus {
  platform_id: string;
  platform_name: string;
  logo: string;
  website_url?: string;
  available: boolean;
  offers_found?: number;
  message: string;
}

export interface SmartBuySearchHistoryItem {
  id: number;
  user_id: number | null;
  query: string;
  category: string;
  filters: Record<string, unknown>;
  results_count: number;
  top_platform: string;
  top_discount_pct: number;
  created_at: string;
}

