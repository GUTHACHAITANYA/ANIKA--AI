import React, { useState, useEffect } from 'react';
import {
  Receipt,
  Search,
  Filter,
  Download,
  Trash2,
  ChevronDown,
  ChevronUp,
  FileText,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';
import { expenseService } from '../services/expenseService';
import { exportService } from '../services/exportService';
import { Expense, SettlementTransaction, ReceiptItem } from '../types';
import { formatINR, formatDate } from '../utils/currency';
import { Badge } from '../components/common/Badge';

export const ExpensesPage: React.FC = () => {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const fetchExpenses = async () => {
    setLoading(true);
    try {
      const data = await expenseService.getExpenses({
        category: categoryFilter !== 'All' ? categoryFilter : undefined,
        search: search.trim() || undefined
      });
      setExpenses(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExpenses();
  }, [categoryFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchExpenses();
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this expense and its settlements?")) return;
    try {
      await expenseService.deleteExpense(id);
      setExpenses((prev) => prev.filter((e) => e.id !== id));
    } catch (err: any) {
      alert(err.message || "Failed to delete expense.");
    }
  };

  const handleMarkSettlementPaid = async (settlementId: number, expenseId: number) => {
    try {
      await expenseService.markSettlementPaid(settlementId);
      // Update local state
      setExpenses((prev) =>
        prev.map((exp) => {
          if (exp.id === expenseId) {
            return {
              ...exp,
              settlements: exp.settlements.map((st: SettlementTransaction) =>
                st.id === settlementId ? { ...st, is_paid: true } : st
              )
            };
          }
          return exp;
        })
      );
    } catch (err: any) {
      alert(err.message || "Failed to update settlement.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-white">Expense & Settlement History</h2>
          <p className="text-xs text-slate-400">
            View all recorded bills, manage participant shares, and mark debts as settled.
          </p>
        </div>

        <button
          onClick={() => exportService.downloadCSV()}
          className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-900 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:border-purple-500/40 hover:text-white transition"
        >
          <Download className="h-4 w-4 text-purple-400" />
          Export All (CSV)
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 rounded-2xl border border-white/10 bg-[#111827] p-4">
        <form onSubmit={handleSearchSubmit} className="relative flex-1">
          <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by merchant or description..."
            className="w-full rounded-xl border border-white/10 bg-slate-900 pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
          />
        </form>

        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-400 shrink-0" />
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

      {/* Expenses List */}
      <div className="space-y-3">
        {expenses.length > 0 ? (
          expenses.map((exp) => {
            const isExpanded = expandedId === exp.id;
            return (
              <div
                key={exp.id}
                className="rounded-2xl border border-white/10 bg-[#111827] overflow-hidden transition-all duration-150"
              >
                {/* Header Row */}
                <div
                  onClick={() => setExpandedId(isExpanded ? null : exp.id)}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-5 cursor-pointer hover:bg-slate-900/40 transition gap-4"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-600/20 text-purple-400 border border-purple-500/30 shrink-0">
                      <Receipt className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white flex items-center gap-2">
                        {exp.title}
                        <Badge variant="purple">{exp.category}</Badge>
                      </h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {formatDate(exp.transaction_date)} • Paid by{' '}
                        <span className="text-emerald-400 font-semibold">{exp.payer_name}</span> •{' '}
                        <span className="capitalize">{exp.split_strategy} Split</span> ({exp.participants?.length || 0} people)
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 self-end sm:self-auto">
                    <span className="text-base font-extrabold text-white">
                      {formatINR(exp.total_amount)}
                    </span>
                    <button className="text-slate-400 hover:text-white transition">
                      {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* Expanded Details Drawer */}
                {isExpanded && (
                  <div className="border-t border-white/5 bg-slate-950/60 p-6 space-y-6">
                    {/* Items */}
                    {exp.items && exp.items.length > 0 && (
                      <div>
                        <h5 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                          Items ({exp.items.length})
                        </h5>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                          {exp.items.map((it: ReceiptItem, i: number) => (
                            <div key={i} className="rounded-xl border border-white/5 bg-slate-900/70 p-2.5 text-xs flex justify-between">
                              <span className="text-slate-300 truncate max-w-[150px]">
                                {it.name} <span className="text-slate-500">x{it.quantity}</span>
                              </span>
                              <span className="font-bold text-white">{formatINR(it.total_price)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Settlements */}
                    <div>
                      <h5 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                        Settlements (Who Owes Whom)
                      </h5>
                      <div className="space-y-2">
                        {exp.settlements && exp.settlements.length > 0 ? (
                          exp.settlements.map((st: SettlementTransaction) => (
                            <div
                              key={st.id}
                              className="flex items-center justify-between rounded-xl border border-white/5 bg-slate-900/60 p-3 text-xs"
                            >
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-white">{st.from_name}</span>
                                <span className="text-slate-400">owes</span>
                                <span className="font-bold text-emerald-400">{st.to_name}</span>
                                <span className="text-slate-400">({formatINR(st.amount)})</span>
                              </div>

                              <div className="flex items-center gap-2">
                                {st.is_paid ? (
                                  <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded-md border border-emerald-800/40">
                                    <CheckCircle2 className="h-3 w-3" /> Settled
                                  </span>
                                ) : (
                                  <button
                                    onClick={() => handleMarkSettlementPaid(st.id!, exp.id)}
                                    className="rounded-lg bg-purple-600/30 border border-purple-500/40 px-2.5 py-1 text-[11px] font-bold text-purple-300 hover:bg-purple-600/50 transition"
                                  >
                                    MARK PAID
                                  </button>
                                )}
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-xs text-slate-500">No outstanding settlements.</p>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-wrap items-center justify-between pt-4 border-t border-white/5 gap-2">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => exportService.generatePDF(exp)}
                          className="flex items-center gap-1.5 rounded-xl border border-white/10 bg-slate-900 px-3 py-1.5 text-xs text-slate-300 hover:text-white transition"
                        >
                          <FileText className="h-3.5 w-3.5 text-purple-400" />
                          PDF
                        </button>
                        <button
                          onClick={() => exportService.downloadTXT(exp.id)}
                          className="flex items-center gap-1.5 rounded-xl border border-white/10 bg-slate-900 px-3 py-1.5 text-xs text-slate-300 hover:text-white transition"
                        >
                          <Download className="h-3.5 w-3.5 text-cyan-400" />
                          TXT
                        </button>
                      </div>

                      <button
                        onClick={() => handleDelete(exp.id)}
                        className="flex items-center gap-1.5 text-xs font-semibold text-rose-400 hover:text-rose-300 transition"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Delete Record
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="rounded-2xl border border-white/10 bg-[#111827] p-12 text-center text-xs text-slate-500">
            No expenses found matching your criteria.
          </div>
        )}
      </div>
    </div>
  );
};
