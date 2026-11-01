import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, X } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'warning' | 'error';
  title: string;
  description?: string;
}

interface ToastContainerProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((t) => {
        const icons = {
          success: <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />,
          warning: <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0" />,
          error: <XCircle className="h-5 w-5 text-rose-400 shrink-0" />,
        };

        const borders = {
          success: 'border-emerald-500/30 bg-emerald-950/90 text-emerald-200',
          warning: 'border-amber-500/30 bg-amber-950/90 text-amber-200',
          error: 'border-rose-500/30 bg-rose-950/90 text-rose-200',
        };

        return (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-start justify-between rounded-xl border p-4 shadow-xl backdrop-blur-md transition-all duration-200 ${borders[t.type]}`}
          >
            <div className="flex items-start gap-3">
              {icons[t.type]}
              <div>
                <p className="text-xs font-bold text-white">{t.title}</p>
                {t.description && <p className="mt-0.5 text-xs text-slate-300">{t.description}</p>}
              </div>
            </div>
            <button
              onClick={() => onDismiss(t.id)}
              className="text-slate-400 hover:text-white transition ml-2"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
