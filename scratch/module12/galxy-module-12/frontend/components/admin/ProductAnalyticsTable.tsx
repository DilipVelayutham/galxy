import React from 'react';

interface ProductAnalyticsItem {
  product_id: string;
  title: string;
  category_name: string;
  views: number;
  wishlist_count: number;
  order_count: number;
  conversion_rate: number;
}

interface ProductAnalyticsTableProps {
  data: ProductAnalyticsItem[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  sort: string;
  onSortChange: (newSort: string) => void;
  onPageChange: (newPage: number) => void;
  onLimitChange: (newLimit: number) => void;
}

export default function ProductAnalyticsTable({
  data = [],
  page,
  limit,
  total,
  totalPages,
  sort,
  onSortChange,
  onPageChange,
  onLimitChange,
}: ProductAnalyticsTableProps) {
  const handleSortClick = (field: string) => {
    onSortChange(field);
  };

  // Helper to render sort arrows/indicators
  const renderSortIndicator = (field: string) => {
    const isSorted = sort === field;
    return (
      <span className={`inline-block ml-1.5 transition-colors duration-200 ${isSorted ? 'text-neonBlue' : 'text-textMuted/40 group-hover:text-textMuted/70'}`}>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5 inline">
          <path fillRule="evenodd" d="M10 3a.75.75 0 0 1 .75.75v10.638l3.96-4.158a.75.75 0 1 1 1.08 1.04l-5.25 5.5a.75.75 0 0 1-1.08 0l-5.25-5.5a.75.75 0 1 1 1.08-1.04l3.96 4.158V3.75A.75.75 0 0 1 10 3Z" clipRule="evenodd" />
        </svg>
      </span>
    );
  };

  return (
    <div className="space-y-4">
      {/* Scrollable Table Card Container */}
      <div className="overflow-hidden bg-panelCharcoal border border-slate-800 rounded-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-panelCharcoal text-[11px] font-bold uppercase tracking-wider text-textMuted">
                <th className="px-6 py-4">Product Info</th>
                <th className="px-6 py-4">Category</th>
                
                {/* Views Header - Sortable (Right-Aligned) */}
                <th 
                  onClick={() => handleSortClick('views')}
                  className="px-6 py-4 cursor-pointer hover:bg-slate-800/30 transition-colors group select-none text-right"
                >
                  <div className="flex items-center justify-end">
                    Views
                    {renderSortIndicator('views')}
                  </div>
                </th>
                
                {/* Wishlist Adds Header - Sortable (Right-Aligned) */}
                <th 
                  onClick={() => handleSortClick('wishlist_adds')}
                  className="px-6 py-4 cursor-pointer hover:bg-slate-800/30 transition-colors group select-none text-right"
                >
                  <div className="flex items-center justify-end">
                    Wishlist Adds
                    {renderSortIndicator('wishlist_adds')}
                  </div>
                </th>
                
                {/* Orders Header - Sortable (Right-Aligned) */}
                <th 
                  onClick={() => handleSortClick('orders')}
                  className="px-6 py-4 cursor-pointer hover:bg-slate-800/30 transition-colors group select-none text-right"
                >
                  <div className="flex items-center justify-end">
                    Orders
                    {renderSortIndicator('orders')}
                  </div>
                </th>
                
                {/* Conversion Rate Header with Info Warning (Right-Aligned) */}
                <th className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end group relative cursor-help">
                    <span>Conversion Rate</span>
                    <span className="ml-1.5 text-textMuted hover:text-neonBlue transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                        <path fillRule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-7-4a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM9 9a.75.75 0 0 0 0 1.5h.25v2.75a.75.75 0 0 0 1.5 0v-3A.75.75 0 0 0 10 9H9Z" clipRule="evenodd" />
                      </svg>
                    </span>
                    {/* Tooltip */}
                    <div className="absolute right-0 bottom-full mb-2 w-64 p-3 bg-panelCharcoal border border-slate-800 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 text-[11px] text-textPrimary font-normal leading-relaxed text-left normal-case whitespace-normal z-50">
                      <div className="font-semibold text-neonBlue mb-1">Directional Metric Only</div>
                      Calculated as: <span className="font-mono text-textPrimary bg-voidBlack px-1 py-0.5 rounded">Orders / Views</span>. This represents directional user intent and does not account for absolute session conversion paths.
                    </div>
                  </div>
                </th>
              </tr>
            </thead>
            
            <tbody className="divide-y divide-slate-800 text-sm text-textPrimary">
              {data.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-textMuted bg-panelCharcoal">
                    No product analytics records found matching current criteria.
                  </td>
                </tr>
              ) : (
                data.map((item, index) => (
                  <tr 
                    key={item.product_id}
                    className={`transition-colors duration-150 hover:bg-slate-800/10 ${index % 2 === 0 ? 'bg-panelCharcoal' : 'bg-[#121217]'}`}
                  >
                    <td className="px-6 py-4">
                      <div className="font-semibold text-textPrimary hover:text-neonBlue transition-colors duration-150 cursor-pointer">
                        {item.title}
                      </div>
                      <div className="text-[10px] text-textMuted font-mono mt-0.5">{item.product_id}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 rounded bg-voidBlack border border-slate-800 text-xs font-medium text-textMuted">
                        {item.category_name}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-semibold text-textPrimary text-right">{item.views.toLocaleString()}</td>
                    <td className="px-6 py-4 text-textPrimary font-semibold text-right">{item.wishlist_count.toLocaleString()}</td>
                    <td className="px-6 py-4 text-textPrimary font-semibold text-right">{item.order_count.toLocaleString()}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end space-x-2">
                        <span className="font-bold text-textPrimary">
                          {(item.conversion_rate * 100).toFixed(2)}%
                        </span>
                        {/* Visual mini-bar */}
                        <div className="w-12 bg-voidBlack rounded-full h-1.5 border border-slate-800 overflow-hidden hidden sm:block">
                          <div 
                            className="bg-neonBlue h-full rounded-full"
                            style={{ width: `${Math.min(item.conversion_rate * 100, 100)}%` }}
                          />
                        </div>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination Footer */}
      {total > 0 && (
        <div className="flex flex-col sm:flex-row items-center justify-between bg-panelCharcoal border border-slate-800 rounded-xl p-4 gap-4 text-xs text-textPrimary">
          {/* Row selection dropdown */}
          <div className="flex items-center space-x-2 text-textMuted font-medium">
            <span>Show</span>
            <select
              value={limit}
              onChange={(e) => onLimitChange(Number(e.target.value))}
              className="bg-voidBlack border border-slate-800 rounded px-2.5 py-1 text-textPrimary focus:outline-none focus:border-neonBlue font-bold"
            >
              {[5, 10, 20, 50].map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
            <span>products</span>
            <span className="text-textMuted/60 font-normal">| Showing {((page - 1) * limit) + 1} - {Math.min(page * limit, total)} of {total}</span>
          </div>

          {/* Navigation Controls */}
          <div className="flex items-center space-x-1.5">
            {/* Prev Button */}
            <button
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
              className="px-2.5 py-1.5 rounded-lg border border-slate-800 bg-voidBlack hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-voidBlack text-textMuted hover:text-textPrimary font-semibold disabled:cursor-not-allowed transition-all"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-3.5 h-3.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
              </svg>
            </button>

            {/* Page Numbers */}
            {Array.from({ length: totalPages }, (_, idx) => idx + 1).map((pageNum) => {
              // Only render numbers close to current page for layout cleanlines
              if (pageNum === 1 || pageNum === totalPages || Math.abs(pageNum - page) <= 1) {
                const isActive = page === pageNum;
                return (
                  <button
                    key={pageNum}
                    onClick={() => onPageChange(pageNum)}
                    className={`px-3 py-1.5 rounded-lg border font-bold transition-all ${
                      isActive 
                        ? 'bg-slate-800 border-slate-700 text-textPrimary shadow-sm' 
                        : 'bg-voidBlack hover:bg-slate-800 border-slate-800 text-textMuted hover:text-textPrimary'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              } else if (pageNum === page - 2 || pageNum === page + 2) {
                return (
                  <span key={pageNum} className="text-textMuted font-bold px-1.5">
                    ...
                  </span>
                );
              }
              return null;
            })}

            {/* Next Button */}
            <button
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
              className="px-2.5 py-1.5 rounded-lg border border-slate-800 bg-voidBlack hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-voidBlack text-textMuted hover:text-textPrimary font-semibold disabled:cursor-not-allowed transition-all"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-3.5 h-3.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
