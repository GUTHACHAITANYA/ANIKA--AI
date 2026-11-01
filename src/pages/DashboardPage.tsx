import React, { useEffect, useState } from 'react';
import {
  Calendar,
  Wallet,
  Clock,
  PieChart,
  ArrowUpRight,
  Sparkles,
  Receipt,
  CheckCircle,
  Plus
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { Badge } from '../components/common/Badge';
import { api } from '../services/api';
import { expenseService } from '../services/expenseService';
import { DashboardStats, Expense } from '../types';
import { formatINR, formatDate } from '../utils/currency';
import { ResponsiveContainer, AreaChart, Area, XAxis, Tooltip } from 'recharts';

interface DashboardPageProps {
  onNavigateToSplit: () => void;
  onNavigateToOCR: () => void;
  onNavigateToAdvisor: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigateToSplit,
  onNavigateToOCR,
  onNavigateToAdvisor
}) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<Expense[]>([]);
  const [dailyTrends, setDailyTrends] = useState<any[]>([]);
  const [aiInsights, setAiInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const res = await api.get('/dashboard');
      if (res.data.success && res.data.data) {
        setStats(res.data.data.stats);
        setRecentTransactions(res.data.data.recent_transactions || []);
        setDailyTrends(res.data.data.daily_trends || []);
        setAiInsights(res.data.data.ai_insights || []);
      }
    } catch (e) {
      console.error("Dashboard fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-white/10 bg-gradient-to-r from-purple-950/40 via-slate-900 to-indigo-950/40 p-6">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-extrabold text-white">Financial Intelligence Overview</h2>
            <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-bold text-emerald-300 border border-emerald-500/40">
              Live Real-Time
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Automated OCR extraction, machine learning classification, and deterministic debt minimization.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={onNavigateToOCR}
            className="flex items-center gap-2 rounded-xl bg-purple-600 px-4 py-2.5 text-xs font-bold text-white shadow-glow-purple hover:bg-purple-500 transition active:scale-95"
          >
            <Plus className="h-4 w-4" />
            Upload Bill
          </button>
          <button
            onClick={onNavigateToAdvisor}
            className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-900 px-4 py-2.5 text-xs font-semibold text-purple-300 hover:border-purple-500/40 hover:text-white transition"
          >
            <Sparkles className="h-4 w-4 text-purple-400" />
            Ask AI Advisor
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Today's Spending"
          value={formatINR(stats?.today_spending || 0)}
          subtitle="Real-time daily tracker"
          icon={Calendar}
          accentColor="purple"
        />
        <StatCard
          title="Monthly Spending"
          value={formatINR(stats?.monthly_spending || 0)}
          subtitle={`Budget: ${formatINR(stats?.monthly_budget || 45000)}`}
          icon={Wallet}
          accentColor="cyan"
          trend={`${stats?.budget_utilization_pct || 0}% used`}
          trendPositive={(stats?.budget_utilization_pct || 0) < 85}
        />
        <StatCard
          title="Pending Settlements"
          value={formatINR(stats?.pending_settlements || 0)}
          subtitle={`${stats?.pending_settlements_count || 0} active unsettled debts`}
          icon={Clock}
          accentColor="amber"
        />
        <StatCard
          title="Remaining Budget"
          value={formatINR(stats?.remaining_budget || 0)}
          subtitle={`Top Outlay: ${stats?.top_category || 'General'}`}
          icon={PieChart}
          accentColor="emerald"
        />
      </div>

      {/* Middle Section: Trends & Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Spending Trends Chart */}
        <div className="lg:col-span-2 rounded-2xl border border-white/10 bg-[#111827] p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-white">7-Day Spending Trend</h4>
              <p className="text-xs text-slate-400">Daily expenses recorded this week</p>
            </div>
            <span className="text-xs font-bold text-purple-400">
              {formatINR(dailyTrends.reduce((a, b) => a + (b.amount || 0), 0))} week total
            </span>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dailyTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="dashSpend" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111827',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderRadius: '12px',
                    fontSize: '12px'
                  }}
                  formatter={(val: any) => [formatINR(Number(val)), 'Spent']}
                />
                <Area
                  type="monotone"
                  dataKey="amount"
                  stroke="#8B5CF6"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#dashSpend)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Financial Insights */}
        <div className="rounded-2xl border border-white/10 bg-[#111827] p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-purple-400" />
            <h4 className="text-sm font-bold text-white">AI Financial Insights</h4>
          </div>

          <div className="space-y-3">
            {aiInsights.map((insight, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-white/5 bg-slate-900/70 p-3.5 text-xs text-slate-300"
              >
                <p className="font-semibold text-white mb-1">{insight.content}</p>
                {insight.recommendations && insight.recommendations[0] && (
                  <p className="text-[11px] text-purple-300 mt-1">
                    💡 {insight.recommendations[0]}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Transactions Table */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className="text-sm font-bold text-white">Recent Transactions</h4>
            <p className="text-xs text-slate-400">Past processed bills and settlements</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="border-b border-white/10 text-[11px] uppercase tracking-wider text-slate-400">
              <tr>
                <th className="py-3 px-3">Title / Merchant</th>
                <th className="py-3 px-3">Date</th>
                <th className="py-3 px-3">Category</th>
                <th className="py-3 px-3">Payer</th>
                <th className="py-3 px-3">Strategy</th>
                <th className="py-3 px-3 text-right">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {recentTransactions.length > 0 ? (
                recentTransactions.map((exp) => (
                  <tr key={exp.id} className="hover:bg-slate-900/50 transition">
                    <td className="py-3 px-3 font-semibold text-white flex items-center gap-2">
                      <Receipt className="h-4 w-4 text-purple-400 shrink-0" />
                      {exp.title}
                    </td>
                    <td className="py-3 px-3 text-slate-400">{formatDate(exp.transaction_date)}</td>
                    <td className="py-3 px-3">
                      <Badge variant="purple">{exp.category}</Badge>
                    </td>
                    <td className="py-3 px-3 text-emerald-400 font-medium">{exp.payer_name}</td>
                    <td className="py-3 px-3 capitalize text-slate-300">{exp.split_strategy}</td>
                    <td className="py-3 px-3 text-right font-bold text-white">
                      {formatINR(exp.total_amount)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-xs text-slate-500">
                    No transactions saved yet. Click "Upload Bill" to scan your first receipt.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
