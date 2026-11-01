import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'purple' | 'emerald' | 'amber' | 'rose' | 'slate' | 'cyan';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'slate',
  size = 'sm',
  className = ''
}) => {
  const variantStyles = {
    purple: 'bg-purple-950/60 text-purple-300 border-purple-800/50',
    emerald: 'bg-emerald-950/60 text-emerald-300 border-emerald-800/50',
    amber: 'bg-amber-950/60 text-amber-300 border-amber-800/50',
    rose: 'bg-rose-950/60 text-rose-300 border-rose-800/50',
    slate: 'bg-slate-800/60 text-slate-300 border-slate-700/50',
    cyan: 'bg-cyan-950/60 text-cyan-300 border-cyan-800/50',
  };

  const sizeStyles = {
    sm: 'text-xs px-2.5 py-0.5 rounded-full',
    md: 'text-sm px-3 py-1 rounded-full',
  };

  return (
    <span className={`inline-flex items-center gap-1 font-medium border ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}>
      {children}
    </span>
  );
};
