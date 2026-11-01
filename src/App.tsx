import React, { useState, useEffect } from 'react';
import { Navbar } from './components/common/Navbar';
import { Sidebar, NavigationTab } from './components/common/Sidebar';
import { ToastContainer, ToastMessage } from './components/common/Toast';
import { AuthModal } from './pages/AuthModal';
import { DashboardPage } from './pages/DashboardPage';
import { OCRScannerPage } from './pages/OCRScannerPage';
import { SplitBillPage } from './pages/SplitBillPage';
import { ExpensesPage } from './pages/ExpensesPage';
import { BudgetPage } from './pages/BudgetPage';
import { SmartBuyPage } from './pages/SmartBuyPage';
import { ActivityLogsPage } from './pages/ActivityLogsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { ChatAdvisor } from './components/advisor/ChatAdvisor';
import { useAuthStore } from './store/authStore';
import { Expense } from './types';
import {
  LayoutDashboard,
  MessageSquareCode,
  ScanLine,
  Receipt,
  Users,
  PieChart,
  ShoppingBag,
  TrendingUp,
  Settings,
  History
} from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavigationTab>('dashboard');
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const { fetchCurrentUser } = useAuthStore();

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const addToast = (type: 'success' | 'warning' | 'error', title: string, description?: string) => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, type, title, description }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  };

  const handleSavedExpense = (expense: Expense) => {
    addToast(
      'success',
      'Expense Saved Successfully',
      `Saved ${expense.merchant_name} (${expense.total_amount} INR) with ${expense.settlements.length} settlement transfers.`
    );
  };

  const mobileNavItems = [
    { id: 'dashboard' as NavigationTab, label: 'Home', icon: LayoutDashboard },
    { id: 'ocr' as NavigationTab, label: 'Scan', icon: ScanLine },
    { id: 'split' as NavigationTab, label: 'Split', icon: Users },
    { id: 'advisor' as NavigationTab, label: 'Advisor', icon: MessageSquareCode },
    { id: 'expenses' as NavigationTab, label: 'History', icon: Receipt },
  ];

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col selection:bg-purple-600 selection:text-white pb-16 md:pb-0">
      {/* Top Navbar */}
      <Navbar
        onOpenAuth={() => setIsAuthOpen(true)}
        onNavigateToScan={() => setActiveTab('ocr')}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar (Desktop) */}
        <Sidebar activeTab={activeTab} onSelectTab={(tab) => setActiveTab(tab)} />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-7xl">
            {activeTab === 'dashboard' && (
              <DashboardPage
                onNavigateToSplit={() => setActiveTab('split')}
                onNavigateToOCR={() => setActiveTab('ocr')}
                onNavigateToAdvisor={() => setActiveTab('advisor')}
              />
            )}

            {activeTab === 'ocr' && (
              <OCRScannerPage onProceedToSplit={() => setActiveTab('split')} />
            )}

            {activeTab === 'split' && (
              <SplitBillPage
                onSavedSuccess={handleSavedExpense}
                onNavigateToChat={() => setActiveTab('advisor')}
              />
            )}

            {activeTab === 'expenses' && <ExpensesPage />}

            {activeTab === 'advisor' && <ChatAdvisor />}

            {activeTab === 'budget' && <BudgetPage />}

            {activeTab === 'smartbuy' && <SmartBuyPage />}

            {activeTab === 'analytics' && <AnalyticsPage />}

            {activeTab === 'activity' && <ActivityLogsPage />}

            {activeTab === 'settings' && <SettingsPage />}
          </div>
        </main>
      </div>

      {/* Mobile Bottom Navigation Bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 border-t border-white/10 bg-[#0B0F19]/95 backdrop-blur-lg px-2 py-1.5 flex justify-around">
        {mobileNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex flex-col items-center gap-1 p-1.5 text-[10px] font-bold ${
                isActive ? 'text-purple-400' : 'text-slate-500'
              }`}
            >
              <Icon className="h-5 w-5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Authentication Modal */}
      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />

      {/* Toast Notifications */}
      <ToastContainer
        toasts={toasts}
        onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))}
      />
    </div>
  );
};
