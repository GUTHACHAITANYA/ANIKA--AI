import { api } from './api';
import { Participant, ReceiptItem, SplitStrategy, SplitShare, SettlementTransaction, Expense } from '../types';

export const expenseService = {
  async calculateSplit(params: {
    total_amount: number;
    participants: Participant[];
    strategy: SplitStrategy;
    percentages?: Record<string, number>;
    custom_amounts?: Record<string, number>;
    items?: ReceiptItem[];
    tax?: number;
    gst?: number;
  }): Promise<{ splits: SplitShare[]; summary: any }> {
    const res = await api.post('/splits/calculate', params);
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.error || 'Failed to calculate split.');
    }
    return res.data.data;
  },

  async calculateSettlements(params: {
    participants: Participant[];
    payer_id: string;
    total_amount: number;
    splits: SplitShare[];
  }): Promise<{ transactions: SettlementTransaction[]; net_balances: any[] }> {
    const res = await api.post('/settlements/calculate', params);
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.error || 'Failed to calculate settlement.');
    }
    return res.data.data;
  },

  async saveExpense(expenseData: any): Promise<Expense> {
    const res = await api.post('/expenses', expenseData);
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.error || 'Failed to save expense.');
    }
    return res.data.data;
  },

  async getExpenses(filters?: { category?: string; search?: string }): Promise<Expense[]> {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.search) params.append('search', filters.search);
    
    const queryStr = params.toString() ? `?${params.toString()}` : '';
    const res = await api.get(`/expenses${queryStr}`);
    return res.data.data || [];
  },

  async getExpenseDetails(id: number): Promise<Expense> {
    const res = await api.get(`/expenses/${id}`);
    return res.data.data;
  },

  async deleteExpense(id: number): Promise<void> {
    await api.delete(`/expenses/${id}`);
  },

  async markSettlementPaid(settlementId: number, reference: string = "Direct UPI / Cash Settlement") {
    const res = await api.post(`/settlements/${settlementId}/paid`, { payment_reference: reference });
    return res.data.data;
  }
};
