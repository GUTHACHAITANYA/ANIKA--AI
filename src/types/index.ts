export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  currency: string;
  monthly_budget: number;
  created_at?: string;
}

export interface ReceiptItem {
  name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  category: string;
  assigned_participants?: string[];
}

export interface ExtractedReceiptData {
  merchant_name: string;
  transaction_date: string;
  currency: string;
  subtotal: number;
  tax: number;
  gst: number;
  total: number;
  items: ReceiptItem[];
  category: string;
  confidence: number;
}

export interface UploadedReceiptResult {
  receipt_id: number;
  original_filename: string;
  file_path: string;
  engine: string;
  data: ExtractedReceiptData;
}

export interface MultiBillSummary {
  receipt_count: number;
  receipts: UploadedReceiptResult[];
  combined_total: number;
  total_items_count: number;
  detected_categories: string[];
  currency: string;
}

export interface Participant {
  id: string; // e.g. "me", "p_1", "p_2"
  name: string;
  email?: string;
  phone?: string;
  is_payer?: boolean;
  active?: boolean;
}

export interface SplitShare {
  participant_id: string;
  participant_name: string;
  amount: number;
  percentage?: number;
  item_subtotal?: number;
  tax_share?: number;
  items?: Array<{ name: string; share_amount: number; quantity: number }>;
}

export interface SettlementTransaction {
  id?: number;
  from_id: string;
  from_name: string;
  to_id: string;
  to_name: string;
  amount: number;
  status?: string;
  is_paid?: boolean;
  paid_at?: string;
}

export type SplitStrategy = 'equal' | 'percentage' | 'custom' | 'itemized';

export interface Expense {
  id: number;
  title: string;
  merchant_name: string;
  transaction_date: string;
  currency: string;
  subtotal: number;
  tax: number;
  gst: number;
  total_amount: number;
  category: string;
  payment_method: string;
  split_strategy: SplitStrategy;
  payer_id: string;
  payer_name: string;
  notes?: string;
  status: string;
  items: ReceiptItem[];
  participants: Participant[];
  splits: SplitShare[];
  settlements: SettlementTransaction[];
  created_at?: string;
}

export interface DashboardStats {
  today_spending: number;
  monthly_spending: number;
  pending_settlements: number;
  pending_settlements_count: number;
  remaining_budget: number;
  monthly_budget: number;
  budget_utilization_pct: number;
  top_category: string;
  top_category_amount: number;
}

export interface DailyTrend {
  day: string;
  date: string;
  amount: number;
}

export interface CategoryBudget {
  category: string;
  allocated: number;
  spent: number;
  remaining: number;
  utilization_pct: number;
  status: 'safe' | 'warning' | 'exceeded';
}

export interface BudgetStatus {
  month: number;
  year: number;
  total_budget: number;
  total_spent: number;
  remaining_budget: number;
  overall_utilization_pct: number;
  is_budget_exceeded: boolean;
  categories: CategoryBudget[];
}

export interface SmartBuyResult {
  item_name: string;
  target_price: number;
  monthly_budget: number;
  current_month_spent: number;
  remaining_budget: number;
  budget_utilization_before: number;
  budget_utilization_after: number;
  monthly_impact_percent: number;
  affordability_score: number;
  verdict: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  recommendations: string[];
  is_ai_generated: boolean;
}

export interface ActivityLog {
  id: number;
  action_type: string;
  description: string;
  metadata: Record<string, any>;
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}
