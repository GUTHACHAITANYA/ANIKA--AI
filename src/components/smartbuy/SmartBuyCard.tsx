import React, { useState } from 'react';
import { ShoppingBag, Sparkles, ShieldAlert, CheckCircle, HelpCircle, ArrowRight } from 'lucide-react';
import { api } from '../../services/api';
import { SmartBuyResult } from '../../types';
import { formatINR } from '../../utils/currency';

export const SmartBuyCard: React.FC = () => {
  const [itemName, setItemName] = useState('Apple MacBook / Windows Laptop');
  const [targetPrice, setTargetPrice] = useState('70000');
  const [category, setCategory] = useState('Shopping');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SmartBuyResult | null>(null);

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    const priceNum = parseFloat(targetPrice);
    if (!itemName.trim() || isNaN(priceNum) || priceNum <= 0) return;

    setLoading(true);
    try {
      const res = await api.post('/ai/smartbuy', {
        item_name: itemName.trim(),
        price: priceNum,
        category
      });
      setResult(res.data.data);
    } catch (err: any) {
      alert(err.message || 'Failed to analyze purchase affordability.');
    } finally {
      setLoading(false);
    }
  };

  const getVerdictStyle = (risk: string) => {
    switch (risk) {
      case 'low':
        return {
          badge: 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60',
          icon: <CheckCircle className="h-5 w-5 text-emerald-400" />
        };
      case 'medium':
        return {
          badge: 'bg-amber-950/80 text-amber-300 border-amber-800/60',
          icon: <HelpCircle className="h-5 w-5 text-amber-400" />
        };
      default:
        return {
          badge: 'bg-rose-950/80 text-rose-300 border-rose-800/60',
          icon: <ShieldAlert className="h-5 w-5 text-rose-400" />
        };
    }
  };

  return (
    <div className="space-y-6">
      {/* Search / Target Input Form */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-600/20 text-purple-400 border border-purple-500/30">
            <ShoppingBag className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-base font-bold text-white">Smart Buy AI Advisor</h4>
            <p className="text-xs text-slate-400">
              Evaluate big-ticket purchases against your verified monthly budget and savings buffer
            </p>
          </div>
        </div>

        <form onSubmit={handleEvaluate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-[11px] font-semibold text-slate-400">Desired Purchase Item</label>
            <input
              type="text"
              value={itemName}
              onChange={(e) => setItemName(e.target.value)}
              placeholder="e.g. Laptop, iPhone 16, Sony Headphones"
              className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400">Target Price (INR)</label>
            <div className="relative mt-1">
              <span className="absolute left-3 top-2.5 text-xs text-slate-500">₹</span>
              <input
                type="number"
                step="1"
                value={targetPrice}
                onChange={(e) => setTargetPrice(e.target.value)}
                placeholder="70000"
                className="w-full rounded-xl border border-white/10 bg-slate-900 pl-7 pr-3 py-2.5 text-xs font-bold text-white focus:border-purple-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 py-2.5 px-4 text-xs font-bold text-white shadow-glow-purple hover:opacity-95 transition disabled:opacity-50 active:scale-95"
            >
              <Sparkles className="h-4 w-4" />
              {loading ? 'Evaluating Budget...' : 'Analyze Affordability'}
            </button>
          </div>
        </form>
      </div>

      {/* Analysis Output */}
      {result && (
        <div className="rounded-2xl border border-white/10 bg-[#111827] p-6 space-y-6 animate-fadeIn">
          {/* Verdict Banner */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-white/5 pb-5 gap-4">
            <div className="flex items-center gap-3">
              {getVerdictStyle(result.risk_level).icon}
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Verdict</span>
                <h3 className="text-lg font-extrabold text-white">{result.verdict}</h3>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <span className="text-[10px] uppercase text-slate-400 font-semibold">Affordability Score</span>
                <p className="text-2xl font-black text-purple-400">{result.affordability_score}/100</p>
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-white/5 bg-slate-900/60 p-3.5">
              <span className="text-[11px] text-slate-400">Monthly Budget</span>
              <p className="text-sm font-bold text-white mt-1">{formatINR(result.monthly_budget)}</p>
            </div>

            <div className="rounded-xl border border-white/5 bg-slate-900/60 p-3.5">
              <span className="text-[11px] text-slate-400">Spent This Month</span>
              <p className="text-sm font-bold text-slate-300 mt-1">{formatINR(result.current_month_spent)}</p>
            </div>

            <div className="rounded-xl border border-white/5 bg-slate-900/60 p-3.5">
              <span className="text-[11px] text-slate-400">Remaining Buffer</span>
              <p className="text-sm font-bold text-emerald-400 mt-1">{formatINR(result.remaining_budget)}</p>
            </div>

            <div className="rounded-xl border border-white/5 bg-slate-900/60 p-3.5">
              <span className="text-[11px] text-slate-400">Budget Impact</span>
              <p className="text-sm font-bold text-amber-400 mt-1">{result.monthly_impact_percent}%</p>
            </div>
          </div>

          {/* AI Recommendations */}
          <div className="rounded-xl border border-purple-500/20 bg-purple-950/20 p-5">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="h-4 w-4 text-purple-400" />
              <h5 className="text-xs font-bold uppercase tracking-wider text-purple-300">
                AI Financial Recommendations (Clearly Labeled)
              </h5>
            </div>

            <ul className="space-y-2 text-xs text-slate-200">
              {result.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-purple-400 font-bold">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
