import React, { useState } from 'react';
import {
  CheckCircle2,
  Download,
  Share2,
  FileText,
  MessageSquare,
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
  Check,
  RotateCcw
} from 'lucide-react';
import { useExpenseWorkflowStore } from '../../store/expenseWorkflowStore';
import { expenseService } from '../../services/expenseService';
import { exportService } from '../../services/exportService';
import { formatINR } from '../../utils/currency';
import { Expense } from '../../types';

interface Step4FinalSaveProps {
  onSavedSuccess: (expense: Expense) => void;
  onNavigateToChat: () => void;
}

export const Step4FinalSave: React.FC<Step4FinalSaveProps> = ({
  onSavedSuccess,
  onNavigateToChat
}) => {
  const {
    merchantName,
    transactionDate,
    totalAmount,
    subtotal,
    tax,
    gst,
    category,
    currency,
    items,
    participants,
    payerId,
    payerName,
    splitStrategy,
    splits,
    settlements,
    resetWorkflow,
    prevStep
  } = useExpenseWorkflowStore();

  const [isSaving, setIsSaving] = useState(false);
  const [savedExpense, setSavedExpense] = useState<Expense | null>(null);
  const [copied, setCopied] = useState(false);
  const [saveSuccessMessage, setSaveSuccessMessage] = useState<string | null>(null);

  const handleSaveExpense = async () => {
    setIsSaving(true);
    try {
      const payload = {
        title: `${merchantName} Bill`,
        merchant_name: merchantName,
        transaction_date: transactionDate,
        currency,
        subtotal,
        tax,
        gst,
        total_amount: totalAmount,
        category,
        split_strategy: splitStrategy,
        payer_id: payerId,
        payer_name: payerName,
        participants,
        items,
        splits,
        settlements
      };

      const saved = await expenseService.saveExpense(payload);
      setSavedExpense(saved);
      setSaveSuccessMessage("Expense saved successfully.");
      setIsSaving(false);
      onSavedSuccess(saved);
    } catch (err: any) {
      setIsSaving(false);
      alert(err.message || "Failed to save expense.");
    }
  };

  const handleSaveAndChat = async () => {
    if (!savedExpense) {
      await handleSaveExpense();
    }
    onNavigateToChat();
  };

  const handleShareSplitSheet = () => {
    const textLines = [
      `🧾 ANIKA-AI SPLIT SHEET: ${merchantName}`,
      `Total: ${formatINR(totalAmount)} | Paid by: ${payerName}`,
      `Strategy: ${splitStrategy.toUpperCase()}`,
      `\nIndividual Shares:`,
      ...splits.map((s) => `• ${s.participant_name}: ${formatINR(s.amount)}`),
      `\nSettlement Instructions:`,
      ...settlements.map((st) => `👉 ${st.from_name} owes ${st.to_name}: ${formatINR(st.amount)}`)
    ];
    const text = textLines.join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleExportTXT = () => {
    if (savedExpense) {
      exportService.downloadTXT(savedExpense.id);
    } else {
      // Direct text download if not saved yet
      const text = [
        "========================================",
        `ANIKA-AI SETTLEMENT SHEET: ${merchantName}`,
        `Total: ${formatINR(totalAmount)} | Payer: ${payerName}`,
        "========================================",
        ...settlements.map((st) => `${st.from_name} pays ${st.to_name}: ${formatINR(st.amount)}`)
      ].join('\n');
      const blob = new Blob([text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `settlement_${merchantName.replace(/\s+/g, '_')}.txt`;
      a.click();
    }
  };

  const handleExportPDF = () => {
    const expenseData: Expense = savedExpense || {
      id: 1,
      title: `${merchantName} Bill`,
      merchant_name: merchantName,
      transaction_date: transactionDate,
      currency,
      subtotal,
      tax,
      gst,
      total_amount: totalAmount,
      category,
      payment_method: 'UPI / Card',
      split_strategy: splitStrategy,
      payer_id: payerId,
      payer_name: payerName,
      status: 'saved',
      items,
      participants,
      splits,
      settlements
    };
    exportService.generatePDF(expenseData, payerName);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Success banner if saved */}
      {saveSuccessMessage && (
        <div className="flex items-center gap-3 rounded-2xl border border-emerald-500/30 bg-emerald-950/30 p-4 text-emerald-300">
          <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
          <span className="text-xs font-bold">{saveSuccessMessage}</span>
        </div>
      )}

      {/* Bill Overview Header */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-white/5 pb-4 mb-4 gap-2">
          <div>
            <h4 className="text-base font-bold text-white">{merchantName}</h4>
            <p className="text-xs text-slate-400">
              {transactionDate} • {category} • Paid by{' '}
              <span className="text-emerald-400 font-bold">{payerName}</span>
            </p>
          </div>
          <div className="text-right">
            <span className="text-[10px] uppercase font-semibold text-slate-400">Total Bill</span>
            <p className="text-xl font-extrabold text-white">{formatINR(totalAmount)}</p>
          </div>
        </div>

        {/* Individual Shares Grid */}
        <div className="mb-6">
          <h5 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
            Individual Shares ({splits.length} participants)
          </h5>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {splits.map((s, idx) => (
              <div key={idx} className="rounded-xl border border-white/5 bg-slate-900/60 p-3">
                <span className="text-xs text-slate-400 block truncate">{s.participant_name}</span>
                <span className="text-sm font-bold text-white mt-1 block">
                  {formatINR(s.amount)}
                </span>
                {s.percentage !== undefined && (
                  <span className="text-[10px] text-purple-400 font-medium">
                    {s.percentage.toFixed(1)}% of bill
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Deterministic Settlement Transfers */}
        <div>
          <h5 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            Optimized Settlement Transfers (Who Owes Whom)
          </h5>

          <div className="space-y-2">
            {settlements.length > 0 ? (
              settlements.map((st, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between rounded-xl border border-emerald-500/20 bg-emerald-950/10 p-3.5"
                >
                  <div className="flex items-center gap-2">
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-800 text-xs font-bold text-purple-300">
                      {idx + 1}
                    </span>
                    <span className="text-xs font-bold text-white">{st.from_name}</span>
                    <span className="text-xs text-slate-400 font-medium">owes</span>
                    <span className="text-xs font-bold text-emerald-400">{st.to_name}</span>
                  </div>

                  <span className="text-sm font-extrabold text-white">
                    {formatINR(st.amount)}
                  </span>
                </div>
              ))
            ) : (
              <div className="rounded-xl border border-white/5 bg-slate-900/40 p-4 text-center text-xs text-slate-400">
                No debts remaining. All participants have zero net balance.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Working Action Buttons Toolbar */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
        <h5 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
          Actions & Exports
        </h5>

        <div className="flex flex-wrap items-center gap-3">
          {/* 1. SAVE EXPENSE */}
          <button
            onClick={handleSaveExpense}
            disabled={isSaving || savedExpense !== null}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-2.5 text-xs font-bold text-white shadow-glow-green hover:opacity-95 transition disabled:opacity-50"
          >
            <CheckCircle2 className="h-4 w-4" />
            {savedExpense ? 'EXPENSE SAVED' : isSaving ? 'SAVING...' : 'SAVE EXPENSE'}
          </button>

          {/* 2. SAVE & CHAT */}
          <button
            onClick={handleSaveAndChat}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-glow-purple hover:opacity-95 transition"
          >
            <MessageSquare className="h-4 w-4" />
            SAVE & CHAT
          </button>

          {/* 3. EXPORT PDF */}
          <button
            onClick={handleExportPDF}
            className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-900 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:border-purple-500/40 hover:text-white transition"
          >
            <Download className="h-4 w-4 text-purple-400" />
            EXPORT PDF
          </button>

          {/* 4. EXPORT TXT */}
          <button
            onClick={handleExportTXT}
            className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-900 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:border-purple-500/40 hover:text-white transition"
          >
            <FileText className="h-4 w-4 text-cyan-400" />
            EXPORT TXT
          </button>

          {/* 5. SHARE SPLIT SHEET */}
          <button
            onClick={handleShareSplitSheet}
            className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-900 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:border-emerald-500/40 hover:text-white transition"
          >
            {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Share2 className="h-4 w-4 text-emerald-400" />}
            {copied ? 'COPIED TO CLIPBOARD' : 'SHARE SPLIT SHEET'}
          </button>
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-4">
        <button
          onClick={prevStep}
          className="flex items-center gap-2 rounded-xl border border-white/10 px-5 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 transition"
        >
          <ArrowLeft className="h-4 w-4" />
          Back: Strategy
        </button>

        <button
          onClick={() => {
            resetWorkflow();
          }}
          className="flex items-center gap-2 rounded-xl border border-white/10 px-5 py-2.5 text-xs font-semibold text-slate-400 hover:text-white transition"
        >
          <RotateCcw className="h-4 w-4" />
          Start New Split
        </button>
      </div>
    </div>
  );
};
