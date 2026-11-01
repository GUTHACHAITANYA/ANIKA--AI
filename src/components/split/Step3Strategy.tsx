import React, { useState, useEffect } from 'react';
import {
  CreditCard,
  Percent,
  Sliders,
  CheckSquare,
  ArrowLeft,
  ArrowRight,
  Calculator,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { useExpenseWorkflowStore } from '../../store/expenseWorkflowStore';
import { expenseService } from '../../services/expenseService';
import { SplitStrategy, ReceiptItem } from '../../types';
import { formatINR } from '../../utils/currency';

export const Step3Strategy: React.FC = () => {
  const {
    totalAmount,
    participants,
    payerId,
    payerName,
    setPayer,
    splitStrategy,
    setSplitStrategy,
    percentages,
    setParticipantPercentage,
    setPercentages,
    customAmounts,
    setParticipantCustomAmount,
    setCustomAmounts,
    items,
    updateItem,
    tax,
    gst,
    setSplits,
    setSettlements,
    nextStep,
    prevStep
  } = useExpenseWorkflowStore();

  const [calculationError, setCalculationError] = useState<string | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  // Initialize defaults for percentage and custom when participants change
  useEffect(() => {
    if (participants.length > 0) {
      // Default equal percentages
      const defaultPct = (100 / participants.length).toFixed(2);
      const newPct: Record<string, number> = {};
      const newCustom: Record<string, number> = {};
      const baseAmt = Math.floor((totalAmount / participants.length) * 100) / 100;

      participants.forEach((p, idx) => {
        newPct[p.id] = idx === 0 ? 100 - (parseFloat(defaultPct) * (participants.length - 1)) : parseFloat(defaultPct);
        newCustom[p.id] = baseAmt;
      });

      if (Object.keys(percentages).length === 0) setPercentages(newPct);
      if (Object.keys(customAmounts).length === 0) setCustomAmounts(newCustom);
    }
  }, [participants.length, totalAmount]);

  // Handler for calculating split and settlements
  const handleCalculateAndAdvance = async () => {
    setCalculationError(null);
    setIsCalculating(true);

    try {
      // 1. Calculate Split
      const splitResult = await expenseService.calculateSplit({
        total_amount: totalAmount,
        participants,
        strategy: splitStrategy,
        percentages,
        custom_amounts: customAmounts,
        items,
        tax,
        gst
      });

      setSplits(splitResult.splits);

      // 2. Calculate Settlements using Selected Payer
      const settlementResult = await expenseService.calculateSettlements({
        participants,
        payer_id: payerId,
        total_amount: totalAmount,
        splits: splitResult.splits
      });

      setSettlements(settlementResult.transactions);

      // 3. Advance to step 4
      setIsCalculating(false);
      nextStep();
    } catch (err: any) {
      setIsCalculating(false);
      setCalculationError(err.message || 'Error calculating split. Please check the entered allocations.');
    }
  };

  const handleApplyEqualPercentages = () => {
    const pct = parseFloat((100 / participants.length).toFixed(2));
    const newPct: Record<string, number> = {};
    participants.forEach((p, idx) => {
      newPct[p.id] = idx === 0 ? parseFloat((100 - pct * (participants.length - 1)).toFixed(2)) : pct;
    });
    setPercentages(newPct);
  };

  const handleApplyEqualCustomAmounts = () => {
    const share = parseFloat((totalAmount / participants.length).toFixed(2));
    const newCustom: Record<string, number> = {};
    participants.forEach((p, idx) => {
      newCustom[p.id] = idx === 0 ? parseFloat((totalAmount - share * (participants.length - 1)).toFixed(2)) : share;
    });
    setCustomAmounts(newCustom);
  };

  const toggleParticipantOnItem = (itemIdx: number, participantId: string) => {
    const currentItem = items[itemIdx];
    const assigned = currentItem.assigned_participants || [];
    const updated = assigned.includes(participantId)
      ? assigned.filter((id) => id !== participantId)
      : [...assigned, participantId];
    updateItem(itemIdx, { assigned_participants: updated });
  };

  return (
    <div className="space-y-6">
      {/* Payer Selection Box */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <CreditCard className="h-4 w-4 text-emerald-400" />
              Who Paid the Bill?
            </h4>
            <p className="text-xs text-slate-400">
              The primary payer will receive reimbursement from participants who owe money
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-300">Payer:</span>
            <select
              value={payerId}
              onChange={(e) => setPayer(e.target.value)}
              className="rounded-xl border border-emerald-500/40 bg-slate-900 px-4 py-2 text-xs font-bold text-emerald-400 focus:border-emerald-400 focus:outline-none shadow-sm"
            >
              {participants.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} {p.id === 'me' ? '(You)' : ''}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Split Strategy Tabs */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
        <h4 className="text-sm font-bold text-white mb-3">Choose Split Strategy</h4>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-6">
          <button
            type="button"
            onClick={() => setSplitStrategy('equal')}
            className={`flex items-center justify-center gap-2 rounded-xl py-3 px-4 text-xs font-bold transition-all ${
              splitStrategy === 'equal'
                ? 'bg-purple-600 text-white shadow-glow-purple border border-purple-400'
                : 'bg-slate-900/80 text-slate-400 border border-white/5 hover:text-white'
            }`}
          >
            <Calculator className="h-4 w-4" />
            EQUAL SPLIT
          </button>

          <button
            type="button"
            onClick={() => setSplitStrategy('percentage')}
            className={`flex items-center justify-center gap-2 rounded-xl py-3 px-4 text-xs font-bold transition-all ${
              splitStrategy === 'percentage'
                ? 'bg-purple-600 text-white shadow-glow-purple border border-purple-400'
                : 'bg-slate-900/80 text-slate-400 border border-white/5 hover:text-white'
            }`}
          >
            <Percent className="h-4 w-4" />
            PERCENTAGE SPLIT
          </button>

          <button
            type="button"
            onClick={() => setSplitStrategy('custom')}
            className={`flex items-center justify-center gap-2 rounded-xl py-3 px-4 text-xs font-bold transition-all ${
              splitStrategy === 'custom'
                ? 'bg-purple-600 text-white shadow-glow-purple border border-purple-400'
                : 'bg-slate-900/80 text-slate-400 border border-white/5 hover:text-white'
            }`}
          >
            <Sliders className="h-4 w-4" />
            CUSTOM AMOUNT
          </button>

          <button
            type="button"
            onClick={() => setSplitStrategy('itemized')}
            className={`flex items-center justify-center gap-2 rounded-xl py-3 px-4 text-xs font-bold transition-all ${
              splitStrategy === 'itemized'
                ? 'bg-purple-600 text-white shadow-glow-purple border border-purple-400'
                : 'bg-slate-900/80 text-slate-400 border border-white/5 hover:text-white'
            }`}
          >
            <CheckSquare className="h-4 w-4" />
            ITEMIZED SPLIT
          </button>
        </div>

        {/* Strategy Specific Input Panel */}
        <div className="rounded-xl border border-white/5 bg-slate-900/50 p-5">
          {/* A. EQUAL SPLIT */}
          {splitStrategy === 'equal' && (
            <div className="text-center py-4">
              <p className="text-xs text-slate-300">
                Dividing total <span className="font-bold text-emerald-400">{formatINR(totalAmount)}</span> equally across{' '}
                <span className="font-bold text-white">{participants.length}</span> participants.
              </p>
              <p className="mt-2 text-2xl font-extrabold text-purple-400">
                {formatINR(totalAmount / (participants.length || 1))}
                <span className="text-xs font-normal text-slate-400 ml-1">/ person</span>
              </p>
              <button
                type="button"
                onClick={handleCalculateAndAdvance}
                className="mt-4 rounded-xl bg-purple-600/30 text-purple-300 border border-purple-500/40 px-4 py-1.5 text-xs font-semibold hover:bg-purple-600/50 transition"
              >
                APPLY EQUAL
              </button>
            </div>
          )}

          {/* B. PERCENTAGE SPLIT */}
          {splitStrategy === 'percentage' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Total must sum to 100.0%</span>
                <button
                  type="button"
                  onClick={handleApplyEqualPercentages}
                  className="text-xs font-semibold text-purple-400 hover:text-purple-300"
                >
                  Distribute Evenly
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {participants.map((p) => {
                  const pct = percentages[p.id] || 0;
                  const share = (totalAmount * pct) / 100;
                  return (
                    <div key={p.id} className="flex items-center justify-between rounded-xl bg-slate-900 p-3 border border-white/5">
                      <span className="text-xs font-medium text-slate-200">{p.name}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-slate-400">{formatINR(share)}</span>
                        <div className="relative">
                          <input
                            type="number"
                            min="0"
                            max="100"
                            step="0.1"
                            value={pct}
                            onChange={(e) => setParticipantPercentage(p.id, parseFloat(e.target.value) || 0)}
                            className="w-20 rounded-lg border border-white/10 bg-slate-800 px-2 py-1 text-right text-xs font-bold text-white focus:outline-none focus:border-purple-500 pr-5"
                          />
                          <span className="absolute right-2 top-1 text-xs text-slate-500">%</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Total percentage check */}
              {(() => {
                const totalPct = Object.values(percentages).reduce((a, b) => a + (b || 0), 0);
                const is100 = Math.abs(totalPct - 100) < 0.05;
                return (
                  <div className={`flex items-center justify-between rounded-xl p-3 border text-xs ${
                    is100 ? 'border-emerald-500/30 bg-emerald-950/20 text-emerald-300' : 'border-amber-500/30 bg-amber-950/20 text-amber-300'
                  }`}>
                    <span>Current Percentage Sum: <strong>{totalPct.toFixed(1)}%</strong></span>
                    {is100 ? <span>✓ Ready to split</span> : <span>Need: {(100 - totalPct).toFixed(1)}% more</span>}
                  </div>
                );
              })()}
            </div>
          )}

          {/* C. CUSTOM AMOUNT */}
          {splitStrategy === 'custom' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">Custom sum must equal {formatINR(totalAmount)}</span>
                <button
                  type="button"
                  onClick={handleApplyEqualCustomAmounts}
                  className="text-xs font-semibold text-purple-400 hover:text-purple-300"
                >
                  Distribute Evenly
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {participants.map((p) => {
                  const amt = customAmounts[p.id] || 0;
                  return (
                    <div key={p.id} className="flex items-center justify-between rounded-xl bg-slate-900 p-3 border border-white/5">
                      <span className="text-xs font-medium text-slate-200">{p.name}</span>
                      <div className="relative">
                        <span className="absolute left-2.5 top-1 text-xs text-slate-500">₹</span>
                        <input
                          type="number"
                          step="0.01"
                          value={amt}
                          onChange={(e) => setParticipantCustomAmount(p.id, parseFloat(e.target.value) || 0)}
                          className="w-28 rounded-lg border border-white/10 bg-slate-800 pl-6 pr-2 py-1 text-right text-xs font-bold text-white focus:outline-none focus:border-purple-500"
                        />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Total custom check */}
              {(() => {
                const totalCustom = Object.values(customAmounts).reduce((a, b) => a + (b || 0), 0);
                const diff = totalAmount - totalCustom;
                const matches = Math.abs(diff) < 0.05;
                return (
                  <div className={`flex items-center justify-between rounded-xl p-3 border text-xs ${
                    matches ? 'border-emerald-500/30 bg-emerald-950/20 text-emerald-300' : 'border-amber-500/30 bg-amber-950/20 text-amber-300'
                  }`}>
                    <span>Total Allocated: <strong>{formatINR(totalCustom)}</strong></span>
                    {matches ? <span>✓ Exactly matches bill</span> : <span>Difference: {formatINR(diff)}</span>}
                  </div>
                );
              })()}
            </div>
          )}

          {/* D. ITEMIZED SPLIT */}
          {splitStrategy === 'itemized' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-xs text-slate-400">
                  Select which participants shared each item. Taxes are automatically apportioned proportionally.
                </p>
                <button
                  type="button"
                  onClick={() => {
                    // Assign all participants to all items
                    const allIds = participants.map((p) => p.id);
                    items.forEach((_, idx) => updateItem(idx, { assigned_participants: allIds }));
                  }}
                  className="text-xs font-semibold text-purple-400 hover:text-purple-300"
                >
                  APPLY ITEMIZED (Select All)
                </button>
              </div>

              <div className="space-y-3">
                {items.map((it, itemIdx) => {
                  const assigned = it.assigned_participants || [];
                  return (
                    <div key={itemIdx} className="rounded-xl border border-white/5 bg-slate-900 p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-white">
                          {it.name} <span className="text-slate-500">x{it.quantity}</span>
                        </span>
                        <span className="text-xs font-bold text-emerald-400">
                          {formatINR(it.total_price)}
                        </span>
                      </div>

                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {participants.map((p) => {
                          const isAssigned = assigned.includes(p.id);
                          return (
                            <button
                              key={p.id}
                              type="button"
                              onClick={() => toggleParticipantOnItem(itemIdx, p.id)}
                              className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold border transition ${
                                isAssigned
                                  ? 'border-purple-500/50 bg-purple-950/60 text-purple-200'
                                  : 'border-white/5 bg-slate-800 text-slate-400 hover:text-slate-200'
                              }`}
                            >
                              {p.name} {isAssigned ? '✓' : ''}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Error message */}
        {calculationError && (
          <div className="mt-4 rounded-xl border border-rose-500/30 bg-rose-950/30 p-4 text-xs text-rose-300 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{calculationError}</span>
          </div>
        )}
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-4">
        <button
          onClick={prevStep}
          className="flex items-center gap-2 rounded-xl border border-white/10 px-5 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 transition"
        >
          <ArrowLeft className="h-4 w-4" />
          Back: Participants
        </button>

        <button
          onClick={handleCalculateAndAdvance}
          disabled={isCalculating}
          className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-glow-purple hover:opacity-95 transition disabled:opacity-50"
        >
          {isCalculating ? 'Computing Settlements...' : 'Calculate Settlement & Save'}
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};
