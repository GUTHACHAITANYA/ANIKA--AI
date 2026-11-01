import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { SpendingTrendChart } from '../components/analytics/SpendingTrendChart';
import { CategoryPieChart } from '../components/analytics/CategoryPieChart';
import { DailySpendBarChart } from '../components/analytics/DailySpendBarChart';
import { BudgetUtilizationChart } from '../components/analytics/BudgetUtilizationChart';
import { TrendingUp, Filter, PieChart, BarChart2 } from 'lucide-react';
import { formatINR } from '../utils/currency';

export const AnalyticsPage: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState('All');

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const url = categoryFilter !== 'All' ? `/analytics?category=${categoryFilter}` : '/analytics';
      const res = await api.get(url);
      if (res.data.success && res.data.data) {
        setAnalyticsData(res.data.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [categoryFilter]);

  return (
    <div className="space-y-6">
      {/* Header & Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-white">Financial Analytics & Trends</h2>
          <p className="text-xs text-slate-400">
            Interactive multi-dimensional financial charts rendered via Recharts.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-xs font-medium text-white focus:border-purple-500 focus:outline-none"
          >
            <option value="All">All Categories</option>
            {[
              "Food & Dining", "Groceries", "Shopping", "Transport", "Fuel",
              "Healthcare", "Entertainment", "Utilities", "Travel", "Education", "Bills", "Other"
            ].map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Grid of Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Monthly Spending Trend */}
        <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-purple-400" />
                6-Month Spending Trend
              </h4>
              <p className="text-xs text-slate-400">Monthly expense trajectory</p>
            </div>
          </div>
          <SpendingTrendChart data={analyticsData?.monthly_trend || []} />
        </div>

        {/* 2. Category Breakdown Donut */}
        <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <PieChart className="h-4 w-4 text-emerald-400" />
                Category Spending Breakdown
              </h4>
              <p className="text-xs text-slate-400">Distribution across major sectors</p>
            </div>
          </div>
          <CategoryPieChart data={analyticsData?.category_distribution || []} />
        </div>

        {/* 3. Daily Spending */}
        <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <BarChart2 className="h-4 w-4 text-cyan-400" />
                14-Day Daily Outlays
              </h4>
              <p className="text-xs text-slate-400">Daily transaction pacing</p>
            </div>
          </div>
          <DailySpendBarChart data={analyticsData?.daily_spending || []} />
        </div>

        {/* 4. Budget vs Actual Allocation */}
        <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-pink-400" />
                Budget vs Actual Spending
              </h4>
              <p className="text-xs text-slate-400">Comparison of allocated cap vs spend</p>
            </div>
          </div>
          <BudgetUtilizationChart data={analyticsData?.budget_vs_actual || []} />
        </div>
      </div>
    </div>
  );
};
