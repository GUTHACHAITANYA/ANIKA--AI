import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, RefreshCw, ArrowRight, Layers } from 'lucide-react';
import { ocrService } from '../../services/ocrService';
import { MultiBillSummary, UploadedReceiptResult } from '../../types';
import { useExpenseWorkflowStore } from '../../store/expenseWorkflowStore';
import { formatINR } from '../../utils/currency';

interface UploadDropzoneProps {
  onProceedToSplit: () => void;
}

type OCRStage = 'idle' | 'uploading' | 'processing' | 'extracting' | 'validating' | 'completed' | 'failed';

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({ onProceedToSplit }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [stage, setStage] = useState<OCRStage>('idle');
  const [progressPercent, setProgressPercent] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [multiBillSummary, setMultiBillSummary] = useState<MultiBillSummary | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const loadFromOCR = useExpenseWorkflowStore((s) => s.loadFromOCR);

  const handleFileSelection = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArr = Array.from(e.target.files);
      setSelectedFiles(filesArr);
      setErrorMessage(null);
      setStage('idle');
      setMultiBillSummary(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArr = Array.from(e.dataTransfer.files);
      setSelectedFiles(filesArr);
      setErrorMessage(null);
      setStage('idle');
      setMultiBillSummary(null);
    }
  };

  const executeOCRProcess = async () => {
    if (selectedFiles.length === 0) return;

    try {
      setErrorMessage(null);
      setStage('uploading');
      setProgressPercent(20);

      // Simulate step progression for UX
      setTimeout(() => {
        setStage('processing');
        setProgressPercent(45);
      }, 500);

      setTimeout(() => {
        setStage('extracting');
        setProgressPercent(70);
      }, 1100);

      setTimeout(() => {
        setStage('validating');
        setProgressPercent(90);
      }, 1700);

      const result = await ocrService.uploadReceipts(selectedFiles);

      setProgressPercent(100);
      setStage('completed');
      setMultiBillSummary(result.summary);

      // Automatically populate workflow store with first receipt (or combined)
      if (result.receipts.length > 0) {
        loadFromOCR(result.receipts[0].data);
      }
    } catch (err: any) {
      setStage('failed');
      setErrorMessage(err.message || 'Unable to process this receipt. Please try a clearer image or document.');
    }
  };

  const handleProceedClick = () => {
    if (!multiBillSummary || multiBillSummary.receipts.length === 0) return;
    // Load data and navigate
    loadFromOCR(multiBillSummary.receipts[0].data);
    onProceedToSplit();
  };

  return (
    <div className="space-y-6">
      {/* Dropzone Box */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`group relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-200 ${
          stage === 'failed'
            ? 'border-rose-500/40 bg-rose-950/10'
            : stage === 'completed'
            ? 'border-emerald-500/40 bg-emerald-950/10'
            : 'border-white/10 bg-[#111827]/70 hover:border-purple-500/40 hover:bg-[#172236]/80'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".jpg,.jpeg,.png,.webp,.pdf"
          onChange={handleFileSelection}
          className="hidden"
        />

        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-purple-600/20 text-purple-400 border border-purple-500/30 group-hover:scale-105 transition">
          <UploadCloud className="h-7 w-7" />
        </div>

        <h4 className="mt-4 text-base font-bold text-white">
          {selectedFiles.length > 0
            ? `${selectedFiles.length} file(s) selected`
            : 'Drop receipts, invoices, or PDFs here'}
        </h4>
        <p className="mt-1 text-xs text-slate-400 max-w-sm">
          Supports JPG, PNG, WEBP, and PDF files up to 16MB. Multi-bill batch processing enabled.
        </p>

        {selectedFiles.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2 justify-center">
            {selectedFiles.map((file, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 rounded-lg border border-purple-500/30 bg-purple-950/40 px-2.5 py-1 text-xs font-medium text-purple-200"
              >
                <FileText className="h-3.5 w-3.5 text-purple-400" />
                {file.name} ({(file.size / 1024).toFixed(0)} KB)
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Action & Progress Area */}
      {selectedFiles.length > 0 && stage === 'idle' && (
        <div className="flex justify-end gap-3">
          <button
            onClick={() => {
              setSelectedFiles([]);
              setMultiBillSummary(null);
            }}
            className="rounded-xl border border-white/10 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-800 transition"
          >
            Clear
          </button>
          <button
            onClick={executeOCRProcess}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-glow-purple hover:opacity-95 transition active:scale-95"
          >
            <RefreshCw className="h-4 w-4" />
            Analyze & Extract Bill
          </button>
        </div>
      )}

      {/* Progress Indicator */}
      {['uploading', 'processing', 'extracting', 'validating'].includes(stage) && (
        <div className="rounded-2xl border border-purple-500/20 bg-purple-950/20 p-5">
          <div className="flex items-center justify-between text-xs font-semibold text-purple-200 mb-2">
            <span className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4 animate-spin text-purple-400" />
              Stage: <span className="capitalize">{stage} document...</span>
            </span>
            <span>{progressPercent}%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 transition-all duration-300 rounded-full"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      )}

      {/* Error state with retry */}
      {stage === 'failed' && (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-5 flex items-start justify-between">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-white">OCR Processing Failed</p>
              <p className="text-xs text-rose-300 mt-1">{errorMessage}</p>
            </div>
          </div>
          <button
            onClick={executeOCRProcess}
            className="flex items-center gap-1.5 rounded-xl border border-rose-500/40 bg-rose-900/40 px-3 py-1.5 text-xs font-bold text-rose-200 hover:bg-rose-900/60 transition"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Retry
          </button>
        </div>
      )}

      {/* Completed Multi-Bill Extraction Results */}
      {stage === 'completed' && multiBillSummary && (
        <div className="space-y-4 animate-fadeIn">
          {/* Summary Banner */}
          <div className="flex flex-wrap items-center justify-between rounded-2xl border border-emerald-500/30 bg-emerald-950/20 p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-emerald-500/20 p-2.5 text-emerald-400 border border-emerald-500/30">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">Extraction Completed</h4>
                <p className="text-xs text-emerald-300">
                  Identified {multiBillSummary.receipt_count} distinct receipt(s) with {multiBillSummary.total_items_count} items.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 mt-3 sm:mt-0">
              <div className="text-right">
                <p className="text-[10px] uppercase font-semibold text-slate-400">Combined Total</p>
                <p className="text-lg font-extrabold text-emerald-400">
                  {formatINR(multiBillSummary.combined_total)}
                </p>
              </div>

              <button
                onClick={handleProceedClick}
                className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-4 py-2.5 text-xs font-bold text-white shadow-glow-green hover:opacity-95 transition"
              >
                Proceed to Split Bill
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Independent Multi-Bill Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {multiBillSummary.receipts.map((r, idx) => (
              <div
                key={r.receipt_id || idx}
                className="rounded-2xl border border-white/10 bg-[#111827] p-5 shadow-sm hover:border-purple-500/30 transition"
              >
                <div className="flex items-center justify-between border-b border-white/5 pb-3 mb-3">
                  <div className="flex items-center gap-2">
                    <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-purple-900/50 text-xs font-bold text-purple-300">
                      {idx + 1}
                    </span>
                    <h5 className="text-sm font-bold text-white">{r.data.merchant_name}</h5>
                  </div>
                  <span className="text-xs font-bold text-emerald-400">
                    {formatINR(r.data.total)}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400 mb-3">
                  <span>Date: {r.data.transaction_date}</span>
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300">
                    {r.data.category}
                  </span>
                </div>

                {/* Items preview */}
                <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                  {r.data.items.map((it, itemIdx) => (
                    <div
                      key={itemIdx}
                      className="flex items-center justify-between rounded-lg bg-slate-900/60 px-2.5 py-1.5 text-xs"
                    >
                      <span className="text-slate-300 truncate max-w-[180px]">
                        {it.name} <span className="text-slate-500">x{it.quantity}</span>
                      </span>
                      <span className="font-semibold text-slate-200">
                        {formatINR(it.total_price)}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="mt-4 pt-3 border-t border-white/5 flex justify-end">
                  <button
                    onClick={() => {
                      loadFromOCR(r.data);
                      onProceedToSplit();
                    }}
                    className="text-xs font-semibold text-purple-400 hover:text-purple-300 flex items-center gap-1"
                  >
                    Split this receipt <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
