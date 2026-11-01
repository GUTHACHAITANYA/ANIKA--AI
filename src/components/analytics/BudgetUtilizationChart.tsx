import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';
import { formatINR } from '../../utils/currency';

interface BudgetUtilizationChartProps {
  data: Array<{ category: string; spent: number; allocated: number; percentage: number }>;
}

export const BudgetUtilizationChart: React.FC<BudgetUtilizationChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-xs text-slate-500">
        No budget comparisons available
      </div>
    );
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="category"
            stroke="#64748B"
            fontSize={10}
            tickLine={false}
          />
          <YAxis
            stroke="#64748B"
            fontSize={11}
            tickLine={false}
            tickFormatter={(v) => `₹${v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#111827',
              borderColor: 'rgba(255,255,255,0.1)',
              borderRadius: '12px',
              fontSize: '12px'
            }}
            formatter={(val: any) => [formatINR(Number(val))]}
          />
          <Legend
            verticalAlign="top"
            height={36}
            iconType="circle"
            formatter={(val: string) => <span className="text-xs text-slate-300 mr-3">{val}</span>}
          />
          <Bar dataKey="spent" name="Actual Spent" fill="#EC4899" radius={[4, 4, 0, 0]} />
          <Bar dataKey="allocated" name="Budget Limit" fill="#3B82F6" radius={[4, 4, 0, 0]} opacity={0.6} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
