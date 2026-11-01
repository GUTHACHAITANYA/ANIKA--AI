import React, { useState, useEffect } from 'react';
import { UploadDropzone } from '../components/ocr/UploadDropzone';
import { Sparkles, MessageSquare, History, ArrowRight, CheckCircle } from 'lucide-react';
import { ocrService } from '../services/ocrService';
import { useExpenseWorkflowStore } from '../store/expenseWorkflowStore';
import { formatINR, formatDate } from '../utils/currency';

interface OCRScannerPageProps {
  onProceedToSplit: () => void;
}

export const OCRScannerPage: React.FC<OCRScannerPageProps> = ({ onProceedToSplit }) => {
  const [nlpText, setNlpText] = useState('');
  const [isAnalyzingNlp, setIsAnalyzingNlp] = useState(false);
  const [nlpResult, setNlpResult] = useState<any | null>(null);
  const [history, setHistory] = useState<any[]>([]);

  const { setBillData, setPayer, addParticipant } = useExpenseWorkflowStore();

  useEffect(() => {
    ocrService.getHistory().then((data: any[]) => setHistory(data)).catch(() => {});
  }, []);

  const handleNlpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nlpText.trim()) return;
    setIsAnalyzingNlp(true);
    try {
      const data = await ocrService.analyzeText(nlpText.trim());
      setNlpResult(data);

      // Populate store
      if (data.amount > 0) {
        setBillData({
          merchantName: data.merchant,
          totalAmount: data.amount,
          subtotal: data.amount,
          category: data.category,
          items: [{ name: data.description || "Expense item", quantity: 1, unit_price: data.amount, total_price: data.amount, category: data.category }]
        });
        if (data.person && data.person.toLowerCase() !== 'me') {
          addParticipant(data.person);
          setPayer(data.person);
        }
      }
    } catch (err: any) {
      alert(err.message || 'Failed to parse expense text.');
    } finally {
      setIsAnalyzingNlp(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-extrabold text-white">OCR Document Scanner & NLP Parser</h2>
        <p className="text-xs text-slate-400">
          Upload multi-bill receipts, grocery bills, payment screenshots, or use natural language to auto-extract structured line items.
        </p>
      </div>

      {/* 1. Main Upload Dropzone */}
      <UploadDropzone onProceedToSplit={onProceedToSplit} />

      {/* 2. Quick NLP Natural Language Parser */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-purple-400" />
          <h4 className="text-sm font-bold text-white">Quick Natural Language Expense Parser</h4>
        </div>
        <p className="text-xs text-slate-400">
          Don't have a photo? Type a natural sentence (e.g., <span className="text-purple-300">"Chaitu paid 1200 for dinner at Pizza Hut"</span> or <span className="text-purple-300">"Ramu paid 450 for coffee at Starbucks"</span>).
        </p>

        <form onSubmit={handleNlpSubmit} className="flex gap-2">
          <input
            type="text"
            value={nlpText}
            onChange={(e) => setNlpText(e.target.value)}
            placeholder="Type: e.g. Chaitu paid 1200 for dinner at Pizza Hut"
            className="flex-1 rounded-xl border border-white/10 bg-slate-900 px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={isAnalyzingNlp || !nlpText.trim()}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-glow-purple hover:opacity-95 transition disabled:opacity-40"
          >
            {isAnalyzingNlp ? 'Parsing...' : 'Extract'}
          </button>
        </form>

        {nlpResult && (
          <div className="rounded-xl border border-purple-500/30 bg-purple-950/20 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-fadeIn">
            <div className="text-xs text-slate-300 space-y-1">
              <p>
                Payer: <strong className="text-white">{nlpResult.person}</strong> • Amount:{' '}
                <strong className="text-emerald-400">{formatINR(nlpResult.amount)}</strong>
              </p>
              <p>
                Category: <strong className="text-purple-300">{nlpResult.category}</strong> • Merchant:{' '}
                <strong className="text-white">{nlpResult.merchant}</strong>
              </p>
            </div>
            <button
              onClick={onProceedToSplit}
              className="flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white shadow-glow-green hover:bg-emerald-500 transition self-end sm:self-auto"
            >
              Split This Bill <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* 3. Past Upload History */}
      {history.length > 0 && (
        <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
          <div className="flex items-center gap-2 mb-4">
            <History className="h-4 w-4 text-purple-400" />
            <h4 className="text-sm font-bold text-white">Recent Scanned Receipts</h4>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {history.map((h) => (
              <div
                key={h.id}
                className="rounded-xl border border-white/5 bg-slate-900/60 p-3.5 text-xs hover:border-purple-500/30 transition cursor-pointer"
                onClick={() => {
                  if (h.extracted_data) {
                    setBillData(h.extracted_data);
                    onProceedToSplit();
                  }
                }}
              >
                <div className="flex items-center justify-between font-bold text-white mb-1">
                  <span className="truncate">{h.original_filename}</span>
                  <span className="text-emerald-400 font-semibold">{formatINR(h.extracted_data?.total || 0)}</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span>{formatDate(h.upload_date)}</span>
                  <span className="text-purple-300">Confidence: {(h.ocr_confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
