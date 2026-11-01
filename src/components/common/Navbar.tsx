import React from 'react';
import { Zap, Sparkles, User, LogIn, LogOut, ReceiptText, ShieldCheck } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

interface NavbarProps {
  onOpenAuth: () => void;
  onNavigateToScan: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenAuth, onNavigateToScan }) => {
  const { user, isAuthenticated, logout } = useAuthStore();

  return (
    <header className="sticky top-0 z-40 border-b border-white/5 bg-[#0B0F19]/85 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-cyan-400 shadow-glow-purple">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-extrabold tracking-tight text-white">ANIKA-AI</span>
              <span className="rounded-md bg-purple-950/80 px-2 py-0.5 text-[10px] font-semibold text-purple-300 border border-purple-800/40 uppercase">
                PRO FINTECH
              </span>
            </div>
            <p className="hidden text-[11px] text-slate-400 sm:block">
              AI-Powered OCR Expense Splitting & Financial Intelligence
            </p>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          {/* Quick Scan Action */}
          <button
            onClick={onNavigateToScan}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-3.5 py-2 text-xs font-semibold text-white shadow-glow-purple transition hover:opacity-95 active:scale-95"
          >
            <ReceiptText className="h-4 w-4" />
            <span className="hidden sm:inline">Scan Receipt</span>
          </button>

          {/* User Profile / Auth */}
          {isAuthenticated && user ? (
            <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-900/60 p-1.5 pl-3">
              <div className="flex flex-col text-right">
                <span className="text-xs font-medium text-slate-200">{user.full_name || user.username}</span>
                <span className="text-[10px] text-emerald-400 flex items-center justify-end gap-1">
                  <ShieldCheck className="h-2.5 w-2.5" /> Verified
                </span>
              </div>
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-900/50 text-purple-300 border border-purple-700/50 font-semibold text-xs">
                {user.username.slice(0, 2).toUpperCase()}
              </div>
              <button
                onClick={() => logout()}
                title="Log out"
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="flex items-center gap-1.5 rounded-xl border border-white/10 bg-slate-900/80 px-3 py-2 text-xs font-medium text-slate-300 hover:border-purple-500/40 hover:text-white transition"
            >
              <LogIn className="h-3.5 w-3.5" />
              Sign In
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
