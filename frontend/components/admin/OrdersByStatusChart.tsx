import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface OrdersByStatusChartProps {
  data: Record<string, number>;
}

export default function OrdersByStatusChart({ data }: OrdersByStatusChartProps) {
  const chartData = Object.entries(data || {}).map(([status, count]) => ({
    status,
    count
  }));

  return (
    <div className="bg-[#16161C] p-4 rounded-lg border border-white/10">
      <h3 className="text-lg font-semibold text-[#F4F4F7] mb-4">Orders By Status</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 20, right: 20, left: -20, bottom: 20 }}>
          <XAxis
            dataKey="status"
            stroke="#8A8A97"
            tick={{ fill: '#8A8A97', fontSize: 12 }}
            interval={0}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis stroke="#8A8A97" allowDecimals={false} tick={{ fill: '#8A8A97', fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#16161C', borderRadius: '4px', border: 'none' }}
            itemStyle={{ color: '#F4F4F7' }}
          />
          <Bar dataKey="count" fill="#18E7FF" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
