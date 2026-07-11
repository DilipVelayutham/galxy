import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

interface TopCategoriesChartProps {
  data: { category_name: string; order_count: number }[];
}

const COLORS = ['#FF2E8A', '#18E7FF', '#9B5CFF'];

export default function TopCategoriesChart({ data }: TopCategoriesChartProps) {
  return (
    <div className="bg-[#16161C] p-4 rounded-lg border border-white/10">
      <h3 className="text-lg font-semibold text-[#F4F4F7] mb-4">Top Categories</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            dataKey="order_count"
            nameKey="category_name"
            cx="50%"
            cy="50%"
            outerRadius={100}
            innerRadius={60}
            label={({ name }) => name}
          >
            {/* @ts-ignore */}
            {(data ?? []).map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: '#16161C', borderRadius: '4px', border: 'none' }}
            itemStyle={{ color: '#F4F4F7' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
