import React, { useState } from 'react';
import { Modal } from '../components/common/Modal';
import { useAuthStore } from '../store/authStore';
import { LogIn, UserPlus, AlertCircle, ShieldCheck } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const [tab, setTab] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');

  const { login, register, error, clearError, isLoading } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    if (tab === 'login') {
      const ok = await login({ identifier: username, password });
      if (ok) onClose();
    } else {
      const ok = await register({ username, email, password, full_name: fullName });
      if (ok) onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={tab === 'login' ? 'Sign In to ANIKA-AI' : 'Create an Account'}>
      <div className="space-y-4">
        {/* Tab Toggle */}
        <div className="flex rounded-xl bg-slate-900 p-1 border border-white/5">
          <button
            type="button"
            onClick={() => {
              setTab('login');
              clearError();
            }}
            className={`flex-1 rounded-lg py-2 text-xs font-bold transition ${
              tab === 'login' ? 'bg-purple-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setTab('register');
              clearError();
            }}
            className={`flex-1 rounded-lg py-2 text-xs font-bold transition ${
              tab === 'register' ? 'bg-purple-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-950/30 p-3 text-xs text-rose-300 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          {tab === 'register' && (
            <div>
              <label className="text-[11px] font-semibold text-slate-400">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. Chaitanya"
                className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3.5 py-2 text-xs text-white focus:border-purple-500 focus:outline-none"
              />
            </div>
          )}

          <div>
            <label className="text-[11px] font-semibold text-slate-400">
              {tab === 'login' ? 'Username or Email' : 'Username'}
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. chaitu"
              className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3.5 py-2 text-xs text-white focus:border-purple-500 focus:outline-none"
            />
          </div>

          {tab === 'register' && (
            <div>
              <label className="text-[11px] font-semibold text-slate-400">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="chaitu@example.com"
                className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3.5 py-2 text-xs text-white focus:border-purple-500 focus:outline-none"
              />
            </div>
          )}

          <div>
            <label className="text-[11px] font-semibold text-slate-400">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3.5 py-2 text-xs text-white focus:border-purple-500 focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 py-2.5 text-xs font-bold text-white shadow-glow-purple hover:opacity-95 transition disabled:opacity-50"
          >
            {tab === 'login' ? <LogIn className="h-4 w-4" /> : <UserPlus className="h-4 w-4" />}
            {isLoading ? 'Processing...' : tab === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-[11px] text-slate-500 pt-2">
          Encrypted authentication with secure session tokens & password hashing.
        </p>
      </div>
    </Modal>
  );
};
