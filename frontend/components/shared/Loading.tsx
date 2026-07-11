import React from 'react';

export default function Loading() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="p-6 h-[120px] bg-panelCharcoal border border-white/10 rounded-lg">
          <div className="h-4 bg-white/10 rounded w-1/2 mb-4"></div>
          <div className="h-8 bg-white/10 rounded w-1/3"></div>
        </div>
      ))}
    </div>
  );
}
