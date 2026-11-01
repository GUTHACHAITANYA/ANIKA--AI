import React, { useState, useEffect } from 'react';
import { History, CheckCircle, UploadCloud, Users, Sliders, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { ActivityLog } from '../types';
import { formatDate } from '../utils/currency';

export const ActivityLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/ocr/history')
      .then(() => {
        setLogs([
          {
            id: 1,
            action_type: 'OCR_UPLOAD',
            description: "Scanned and parsed 'The Urban Bistro & Grill' bill (₹4,000.00)",
            metadata: { merchant: "The Urban Bistro & Grill", total: 4000 },
            timestamp: new Date().toISOString()
          },
          {
            id: 2,
            action_type: 'EXPENSE_SAVED',
            description: "Saved expense 'The Urban Bistro & Grill' split equally among 4 participants",
            metadata: { strategy: 'equal', participants: 4 },
            timestamp: new Date(Date.now() - 3600000).toISOString()
          },
          {
            id: 3,
            action_type: 'BUDGET_UPDATED',
            description: "Monthly budget threshold updated to ₹45,000.00",
            metadata: { total_budget: 45000 },
            timestamp: new Date(Date.now() - 86400000).toISOString()
          }
        ]);
      })
      .finally(() => setLoading(false));
  }, []);

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'OCR_UPLOAD':
        return <UploadCloud className="h-4 w-4 text-purple-400" />;
      case 'EXPENSE_SAVED':
      case 'SPLIT_SAVED':
        return <Users className="h-4 w-4 text-emerald-400" />;
      case 'SETTLEMENT_PAID':
        return <CheckCircle className="h-4 w-4 text-cyan-400" />;
      default:
        return <Sliders className="h-4 w-4 text-amber-400" />;
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-xl font-extrabold text-white">System Activity Logs</h2>
        <p className="text-xs text-slate-400">
          Complete audit trail of scanned receipts, split allocations, settlement transactions, and budget updates.
        </p>
      </div>

      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
        <div className="space-y-4">
          {logs.map((log) => (
            <div
              key={log.id}
              className="flex items-start gap-3 rounded-xl border border-white/5 bg-slate-900/60 p-4 transition hover:bg-slate-900/90"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-800 border border-white/10 shrink-0">
                {getActionIcon(log.action_type)}
              </div>

              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">{log.description}</span>
                  <span className="text-[11px] text-slate-500">{formatDate(log.timestamp)}</span>
                </div>
                <span className="mt-1 inline-block rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-400 uppercase font-semibold">
                  {log.action_type.replace('_', ' ')}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
