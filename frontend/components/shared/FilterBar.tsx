'use client';
import React, { useState } from 'react';

interface FilterBarProps {
  onFilter: (dateFrom: string, dateTo: string, categoryId: string) => void;
}

export default function FilterBar({ onFilter }: FilterBarProps) {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [categoryId, setCategoryId] = useState('');

  const handleApply = () => {
    onFilter(dateFrom, dateTo, categoryId);
  };

  return (
    <div className="flex flex-col sm:flex-row gap-4 items-end mb-6 p-4 bg-panelCharcoal border border-white/10 rounded-lg">
      <div className="flex flex-col gap-1 w-full sm:w-auto">
        <label className="text-textMuted text-sm">Date From</label>
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          className="bg-panelCharcoal text-textPrimary border border-white/10 rounded px-3 py-2 focus:outline-none focus:border-neonBlue focus:shadow-[0_0_0_3px_rgba(24,231,255,0.25)] transition-all"
        />
      </div>
      <div className="flex flex-col gap-1 w-full sm:w-auto">
        <label className="text-textMuted text-sm">Date To</label>
        <input
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          className="bg-panelCharcoal text-textPrimary border border-white/10 rounded px-3 py-2 focus:outline-none focus:border-neonBlue focus:shadow-[0_0_0_3px_rgba(24,231,255,0.25)] transition-all"
        />
      </div>
      <div className="flex flex-col gap-1 w-full sm:w-auto">
        <label className="text-textMuted text-sm">Category ID</label>
        <input
          type="text"
          value={categoryId}
          onChange={(e) => setCategoryId(e.target.value)}
          placeholder="e.g. cat_123"
          className="bg-panelCharcoal text-textPrimary border border-white/10 rounded px-3 py-2 focus:outline-none focus:border-neonBlue focus:shadow-[0_0_0_3px_rgba(24,231,255,0.25)] transition-all placeholder-textMuted"
        />
      </div>
      <button
        onClick={handleApply}
        className="px-4 py-2 bg-neonBlue/10 text-neonBlue border border-neonBlue/20 rounded hover:bg-neonBlue/20 transition-colors"
      >
        Apply
      </button>
    </div>
  );
}
