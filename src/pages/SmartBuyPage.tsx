import React from 'react';
import { SmartBuyCard } from '../components/smartbuy/SmartBuyCard';

export const SmartBuyPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-xl font-extrabold text-white">Smart Buy AI Advisor</h2>
        <p className="text-xs text-slate-400">
          Intelligent purchase simulation to protect emergency funds and prevent discretionary debt.
        </p>
      </div>

      <SmartBuyCard />
    </div>
  );
};
