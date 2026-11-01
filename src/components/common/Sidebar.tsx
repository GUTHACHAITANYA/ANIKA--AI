import React from 'react';
import {
  LayoutDashboard,
  MessageSquareCode,
  ScanLine,
  Receipt,
  Users,
  PieChart,
  ShoppingBag,
  History,
  TrendingUp,
  Settings
} from 'lucide-react';

export type NavigationTab =
  | 'dashboard'
  | 'advisor'
  | 'ocr'
  | 'expenses'
  | 'split'
  | 'budget'
  | 'smartbuy'
  | 'activity'
  | 'analytics'
  | 'settings';

interface SidebarProps {
  activeTab: NavigationTab;
  onSelectTab: (tab: NavigationTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab }) => {
  const navItems = [
    { id: 'dashboard' as NavigationTab, label: 'Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'advisor' as NavigationTab, label: 'Chat Advisor', icon: MessageSquareCode, badge: 'AI' },
    { id: 'ocr' as NavigationTab, label: 'OCR Scanner', icon: ScanLine, badge: 'Vision' },
    { id: 'split' as NavigationTab, label: 'Split Bill', icon: Users, badge: 'Engine' },
    { id: 'expenses' as NavigationTab, label: 'Expenses', icon: Receipt, badge: null },
    { id: 'budget' as NavigationTab, label: 'Budget Insights', icon: PieChart, badge: null },
    { id: 'smartbuy' as NavigationTab, label: 'Smart Buy AI', icon: ShoppingBag, badge: 'Afford' },
    { id: 'analytics' as NavigationTab, label: 'Analytics', icon: TrendingUp, badge: 'Recharts' },
    { id: 'activity' as NavigationTab, label: 'Activity Logs', icon: History, badge: null },
    { id: 'settings' as NavigationTab, label: 'Settings', icon: Settings, badge: null },
  ];

  return (
    <aside className="w-64 shrink-0 border-r border-white/5 bg-[#0B0F19]/90 backdrop-blur-md hidden md:block">
      <div className="flex h-full flex-col justify-between p-4">
        
        <div className="space-y-1">
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-3">
            Financial Suite
          </p>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`group flex w-full items-center justify-between rounded-xl px-3.5 py-2.5 text-xs font-semibold transition-all duration-150 ${
                  isActive
                    ? 'bg-gradient-to-r from-purple-900/60 to-indigo-900/40 text-purple-300 border border-purple-500/30 shadow-glow-purple'
                    : 'text-slate-400 hover:bg-slate-900/80 hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`h-4 w-4 ${isActive ? 'text-purple-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`rounded-md px-1.5 py-0.5 text-[9px] font-bold uppercase ${
                      isActive
                        ? 'bg-purple-600/30 text-purple-200 border border-purple-500/40'
                        : 'bg-slate-800 text-slate-400 border border-slate-700/50'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Bottom system badge */}
        <div className="rounded-xl border border-white/5 bg-slate-900/40 p-3 text-center">
          <p className="text-[11px] font-medium text-slate-300">ANIKA Settlement Core</p>
          <p className="text-[10px] text-emerald-400 mt-0.5">● Deterministic Engine Online</p>
        </div>

      </div>
    </aside>
  );
};
