import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  trend?: string;
  trendPositive?: boolean;
  accentColor?: 'purple' | 'emerald' | 'amber' | 'cyan' | 'rose';
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendPositive,
  accentColor = 'purple',
  onClick
}) => {
  const colorMap = {
    purple: {
      bg: 'from-purple-900/20 to-indigo-950/30 border-purple-500/20',
      iconBg: 'bg-purple-600/20 text-purple-400 border-purple-500/30',
      glow: 'hover:border-purple-500/40',
    },
    emerald: {
      bg: 'from-emerald-900/20 to-teal-950/30 border-emerald-500/20',
      iconBg: 'bg-emerald-600/20 text-emerald-400 border-emerald-500/30',
      glow: 'hover:border-emerald-500/40',
    },
    amber: {
      bg: 'from-amber-900/20 to-yellow-950/30 border-amber-500/20',
      iconBg: 'bg-amber-600/20 text-amber-400 border-amber-500/30',
      glow: 'hover:border-amber-500/40',
    },
    cyan: {
      bg: 'from-cyan-900/20 to-blue-950/30 border-cyan-500/20',
      iconBg: 'bg-cyan-600/20 text-cyan-400 border-cyan-500/30',
      glow: 'hover:border-cyan-500/40',
    },
    rose: {
      bg: 'from-rose-900/20 to-red-950/30 border-rose-500/20',
      iconBg: 'bg-rose-600/20 text-rose-400 border-rose-500/30',
      glow: 'hover:border-rose-500/40',
    },
  };

  const scheme = colorMap[accentColor];

  return (
    <div
      onClick={onClick}
      className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${scheme.bg} p-6 border transition-all duration-200 ${scheme.glow} ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
          <h3 className="mt-2 text-2xl font-bold tracking-tight text-white">{value}</h3>
          {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
        </div>
        <div className={`rounded-xl p-3 border ${scheme.iconBg}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>

      {trend && (
        <div className="mt-4 flex items-center gap-1.5 text-xs">
          <span className={trendPositive ? 'text-emerald-400 font-semibold' : 'text-amber-400 font-semibold'}>
            {trend}
          </span>
          <span className="text-slate-500">vs target pace</span>
        </div>
      )}
    </div>
  );
};
