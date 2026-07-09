import React from 'react';
import Link from 'next/link';

interface StatCardProps {
  title: string;
  value: number | string;
  isEstimate?: boolean;
  accentColor?: string;
  href?: string;
}

export default function StatCard({ title, value, isEstimate, accentColor, href }: StatCardProps) {
  const cardContent = (
    <div 
      className={`p-6 bg-[#16161C] border border-white/10 rounded-lg flex flex-col justify-between h-full relative overflow-hidden transition-all duration-200 ${href ? 'hover:bg-white/5 cursor-pointer' : ''}`}
    >
      {accentColor && (
        <div 
          className="absolute left-0 top-0 bottom-0 w-1" 
          style={{ backgroundColor: accentColor }} 
        />
      )}
      <div className="flex items-center gap-2 mb-2">
        <h3 className="text-[#8A8A97] text-sm font-medium uppercase tracking-wider">{title}</h3>
        {isEstimate && (
          <span className="text-[#8A8A97] text-xs px-2 py-0.5 bg-white/5 rounded">ESTIMATE</span>
        )}
      </div>
      <div className="text-3xl font-bold text-[#F4F4F7]">
        {value}
      </div>
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="block h-full outline-none focus:ring-2 focus:ring-[#18E7FF] rounded-lg">
        {cardContent}
      </Link>
    );
  }

  return cardContent;
}
