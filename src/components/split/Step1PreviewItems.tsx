import React, { useState } from 'react';
import { Plus, Trash2, ArrowRight, Store, Calendar, Tag, IndianRupee } from 'lucide-react';
import { useExpenseWorkflowStore } from '../../store/expenseWorkflowStore';
import { formatINR } from '../../utils/currency';
import { ReceiptItem } from '../../types';

export const Step1PreviewItems: React.FC = () => {
  const {
    merchantName,
    transactionDate,
    totalAmount,
    subtotal,
    tax,
    gst,
    category,
    items,
    notes,
    setBillData,
    addItem,
    updateItem,
    removeItem,
    nextStep
  } = useExpenseWorkflowStore();

  const [newItemName, setNewItemName] = useState('');
  const [newItemPrice, setNewItemPrice] = useState('');
  const [newItemQty, setNewItemQty] = useState('1');

  const handleAddNewItem = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemName.trim() || !newItemPrice) return;
    const price = parseFloat(newItemPrice) || 0;
    const qty = parseFloat(newItemQty) || 1;
    const item: ReceiptItem = {
      name: newItemName.trim(),
      quantity: qty,
      unit_price: price,
      total_price: price * qty,
      category: category || 'Food & Dining',
      assigned_participants: []
    };
    addItem(item);
    setNewItemName('');
    setNewItemPrice('');
    setNewItemQty('1');
  };

  return (
    <div className="space-y-6">
      {/* Bill Overview Header */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
        <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
          <Store className="h-4 w-4 text-purple-400" />
          Receipt & Bill Details
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="text-[11px] font-semibold text-slate-400">Merchant Name</label>
            <input
              type="text"
              value={merchantName}
              onChange={(e) => setBillData({ merchantName: e.target.value })}
              className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-xs font-medium text-white focus:border-purple-500 focus:outline-none"
              placeholder="e.g. Domino's Pizza"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400">Transaction Date</label>
            <input
              type="date"
              value={transactionDate}
              onChange={(e) => setBillData({ transactionDate: e.target.value })}
              className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-xs font-medium text-white focus:border-purple-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400">Category</label>
            <select
              value={category}
              onChange={(e) => setBillData({ category: e.target.value })}
              className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-xs font-medium text-white focus:border-purple-500 focus:outline-none"
            >
              {[
                "Food & Dining", "Groceries", "Shopping", "Transport", "Fuel",
                "Healthcare", "Entertainment", "Utilities", "Travel", "Education", "Bills", "Other"
              ].map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-400">Total Bill (INR)</label>
            <div className="relative mt-1">
              <span className="absolute left-3 top-2 text-xs text-slate-500">₹</span>
              <input
                type="number"
                step="0.01"
                value={totalAmount}
                onChange={(e) => setBillData({ totalAmount: parseFloat(e.target.value) || 0 })}
                className="w-full rounded-xl border border-white/10 bg-slate-900 pl-7 pr-3 py-2 text-xs font-bold text-emerald-400 focus:border-purple-500 focus:outline-none"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Itemized Table */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className="text-sm font-bold text-white">Line Items ({items.length})</h4>
            <p className="text-xs text-slate-400">Review or adjust item prices before assigning shares</p>
          </div>
          <span className="text-xs font-semibold text-slate-300">
            Items Subtotal: <span className="text-white font-bold">{formatINR(subtotal)}</span>
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="border-b border-white/10 text-[11px] uppercase tracking-wider text-slate-400 bg-slate-900/50">
              <tr>
                <th className="py-2.5 px-3">Item Name</th>
                <th className="py-2.5 px-3 w-20">Qty</th>
                <th className="py-2.5 px-3 w-28">Unit Price</th>
                <th className="py-2.5 px-3 w-28">Total</th>
                <th className="py-2.5 px-3 w-12 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {items.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40 transition">
                  <td className="py-2 px-3">
                    <input
                      type="text"
                      value={item.name}
                      onChange={(e) => updateItem(idx, { name: e.target.value })}
                      className="w-full bg-transparent font-medium text-white focus:outline-none focus:text-purple-300"
                    />
                  </td>
                  <td className="py-2 px-3">
                    <input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) => updateItem(idx, { quantity: parseFloat(e.target.value) || 1 })}
                      className="w-16 rounded-lg border border-white/10 bg-slate-900 px-2 py-1 text-center text-xs text-white"
                    />
                  </td>
                  <td className="py-2 px-3">
                    <input
                      type="number"
                      step="0.01"
                      value={item.unit_price}
                      onChange={(e) => updateItem(idx, { unit_price: parseFloat(e.target.value) || 0 })}
                      className="w-24 rounded-lg border border-white/10 bg-slate-900 px-2 py-1 text-right text-xs text-white"
                    />
                  </td>
                  <td className="py-2 px-3 font-semibold text-right text-emerald-400">
                    {formatINR(item.total_price)}
                  </td>
                  <td className="py-2 px-3 text-center">
                    <button
                      onClick={() => removeItem(idx)}
                      className="text-slate-500 hover:text-rose-400 transition"
                      title="Remove item"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Add item inline form */}
        <form onSubmit={handleAddNewItem} className="mt-4 flex flex-wrap gap-2 pt-3 border-t border-white/5">
          <input
            type="text"
            placeholder="Add new item name..."
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            className="flex-1 min-w-[200px] rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
          />
          <input
            type="number"
            min="1"
            placeholder="Qty"
            value={newItemQty}
            onChange={(e) => setNewItemQty(e.target.value)}
            className="w-16 rounded-xl border border-white/10 bg-slate-900 px-2 py-2 text-center text-xs text-white focus:outline-none"
          />
          <input
            type="number"
            step="0.01"
            placeholder="Unit ₹"
            value={newItemPrice}
            onChange={(e) => setNewItemPrice(e.target.value)}
            className="w-28 rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-right text-xs text-white focus:outline-none"
          />
          <button
            type="submit"
            className="flex items-center gap-1 rounded-xl bg-purple-600/30 text-purple-300 border border-purple-500/40 px-3 py-2 text-xs font-semibold hover:bg-purple-600/50 transition"
          >
            <Plus className="h-3.5 w-3.5" />
            Add Item
          </button>
        </form>
      </div>

      {/* Navigation Footer */}
      <div className="flex justify-end pt-4">
        <button
          onClick={nextStep}
          className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-glow-purple hover:opacity-95 transition active:scale-95"
        >
          Next: Add Participants
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};
