import React, { useState, useEffect } from 'react';
import { PieChart, Save, AlertTriangle, CheckCircle, Sliders } from 'lucide-react';
import { api } from '../services/api';
import { BudgetStatus, CategoryBudget } from '../types';
import { formatINR } from '../utils/currency';

export const BudgetPage: React.FC = () => {
  const [budgetData, setBudgetData] = useState<BudgetStatus | null>(null);
  const [totalBudgetInput, setTotalBudgetInput] = useState<string>('45000');
  const [categoryInputs, setCategoryInputs] = useState<Record<string, number>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const fetchBudget = async () => {
    try {
      const res = await api.get('/budget');
      if (res.data.success && res.data.data) {
        const data: BudgetStatus = res.data.data;
        setBudgetData(data);
        setTotalBudgetInput(data.total_budget.toString());
        const cats: Record<string, number> = {};
        data.categories.forEach((c: CategoryBudget) => {
          cats[c.category] = c.allocated;
        });
        setCategoryInputs(cats);
      }
    } catch (e) {
      console.error("Budget fetch error:", e);
    }
  };

  useEffect(() => {
    fetchBudget();
  }, []);

  const handleSaveBudget = async (e: React.FormEvent) => {
    e.preventDefault();
    const total = parseFloat(totalBudgetInput);
    if (isNaN(total) || total <= 0) return;

    setIsSaving(true);
    setSaveSuccess(false);
    try {
      await api.post('/budget', {
        total_budget: total,
        category_budgets: categoryInputs
      });
      setSaveSuccess(true);
      fetchBudget();
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      alert(err.message || 'Failed to update budget.');
    } finally {
      setIsSaving(false);
    }
  };

  const getStatusColor = (status: string) => {
    if (status === 'exceeded') return 'text-rose-400 bg-rose-500';
    if (status === 'warning') return 'text-amber-400 bg-amber-500';
    return 'text-emerald-400 bg-emerald-500';
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-xl font-extrabold text-white">Monthly Budget & Category Limits</h2>
        <p className="text-xs text-slate-400">
          Set spending boundaries, monitor live utilization thresholds, and prevent overspending.
        </p>
      </div>

      {saveSuccess && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/30 p-4 text-xs font-bold text-emerald-300 flex items-center gap-2">
          <CheckCircle className="h-4 w-4" />
          Budget configuration successfully updated.
        </div>
      )}

      {/* Main Budget Card */}
      {budgetData && (
        <div className="rounded-2xl border border-white/10 bg-[#111827] p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-white/5 pb-6 gap-4">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                Current Month Utilization
              </span>
              <h3 className="text-2xl font-black text-white mt-1">
                {formatINR(budgetData.total_spent)}{' '}
                <span className="text-xs font-normal text-slate-400">
                  of {formatINR(budgetData.total_budget)} ({budgetData.overall_utilization_pct}%)
                </span>
              </h3>
            </div>

            <div className="text-right">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                Remaining Allowance
              </span>
              <p className={`text-xl font-extrabold mt-1 ${budgetData.is_budget_exceeded ? 'text-rose-400' : 'text-emerald-400'}`}>
                {formatINR(budgetData.remaining_budget)}
              </p>
            </div>
          </div>

          {/* Progress Bar */}
          <div>
            <div className="h-3 w-full rounded-full bg-slate-800 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  budgetData.overall_utilization_pct >= 100
                    ? 'bg-rose-500'
                    : budgetData.overall_utilization_pct >= 80
                    ? 'bg-amber-500'
                    : 'bg-gradient-to-r from-purple-500 to-emerald-400'
                }`}
                style={{ width: `${Math.min(100, budgetData.overall_utilization_pct)}%` }}
              />
            </div>
            <div className="flex justify-between text-[11px] text-slate-500 mt-2">
              <span>0%</span>
              <span>80% Warning Limit</span>
              <span>100% Exceeded</span>
            </div>
          </div>
        </div>
      )}

      {/* Category Budgets Grid & Form */}
      <form onSubmit={handleSaveBudget} className="rounded-2xl border border-white/10 bg-[#111827] p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-4">
          <div>
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <Sliders className="h-4 w-4 text-purple-400" />
              Category Budget Limits
            </h4>
            <p className="text-xs text-slate-400">Customize monthly caps per category</p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-300">Total Monthly Budget:</span>
            <div className="relative">
              <span className="absolute left-3 top-2 text-xs text-slate-500">₹</span>
              <input
                type="number"
                value={totalBudgetInput}
                onChange={(e) => setTotalBudgetInput(e.target.value)}
                className="w-32 rounded-xl border border-purple-500/40 bg-slate-900 pl-7 pr-3 py-1.5 text-xs font-bold text-white focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Category Limit Bars */}
        <div className="space-y-4">
          {budgetData?.categories.map((cat: CategoryBudget) => {
            const currentCap = categoryInputs[cat.category] !== undefined ? categoryInputs[cat.category] : cat.allocated;
            const pct = Math.round(cat.utilization_pct);
            const statusColor = getStatusColor(cat.status);

            return (
              <div key={cat.category} className="rounded-xl border border-white/5 bg-slate-900/50 p-4 space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{cat.category}</span>
                    {cat.status === 'exceeded' && (
                      <span className="rounded bg-rose-950/80 px-2 py-0.5 text-[9px] font-bold text-rose-300 border border-rose-800/40">
                        Exceeded
                      </span>
                    )}
                    {cat.status === 'warning' && (
                      <span className="rounded bg-amber-950/80 px-2 py-0.5 text-[9px] font-bold text-amber-300 border border-amber-800/40">
                        Warning (80%+)
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-4 text-xs">
                    <span className="text-slate-400">
                      Spent: <strong className="text-white">{formatINR(cat.spent)}</strong>
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span className="text-slate-400">Cap: ₹</span>
                      <input
                        type="number"
                        value={currentCap}
                        onChange={(e) =>
                          setCategoryInputs((prev) => ({
                            ...prev,
                            [cat.category]: parseFloat(e.target.value) || 0
                          }))
                        }
                        className="w-24 rounded-lg border border-white/10 bg-slate-800 px-2 py-1 text-right text-xs font-semibold text-white focus:outline-none focus:border-purple-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${statusColor.split(' ')[1]}`}
                    style={{ width: `${Math.min(100, pct)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Save button */}
        <div className="flex justify-end pt-4 border-t border-white/5">
          <button
            type="submit"
            disabled={isSaving}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-glow-purple hover:opacity-95 transition active:scale-95 disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            {isSaving ? 'Saving Budget...' : 'Save Budget Configuration'}
          </button>
        </div>
      </form>
    </div>
  );
};
