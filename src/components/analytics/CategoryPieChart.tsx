import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend
} from 'recharts';
import { formatINR } from '../../utils/currency';

const CATEGORY_COLORS: Record<string, string> = {
  "Food & Dining": "#8B5CF6",   // Purple
  "Groceries": "#10B981",       // Emerald
  "Shopping": "#EC4899",        // Pink
  "Transport": "#06B6D4",       // Cyan
  "Fuel": "#F59E0B",            // Amber
  "Healthcare": "#EF4444",      // Rose
  "Entertainment": "#6366F1",   // Indigo
  "Utilities": "#14B8A6",       // Teal
  "Travel": "#3B82F6",          // Blue
  "Education": "#84CC16",       // Lime
  "Bills": "#F97316",           // Orange
  "Other": "#94A3B8"            // Slate
};

interface CategoryPieChartProps {
  data: Array<{ name: string; value: number }>;
}

export const CategoryPieChart: React.FC<CategoryPieChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-xs text-slate-500">
        No category spending recorded yet
      </div>
    );
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="45%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={CATEGORY_COLORS[entry.name] || '#A855F7'}
                stroke="rgba(11, 15, 25, 0.8)"
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#111827',
              borderColor: 'rgba(255,255,255,0.1)',
              borderRadius: '12px',
              fontSize: '12px'
            }}
            formatter={(val: any) => [formatINR(Number(val)), 'Spent']}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            formatter={(val: string) => <span className="text-xs text-slate-300 mr-2">{val}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
