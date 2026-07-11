import React, { useMemo } from 'react';
import Link from 'next/link';
import { Order } from '@/types/admin';
import { Eye, Search, Calendar, X, ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown, Loader2 } from 'lucide-react';
import { formatCurrency as utilFormatCurrency } from '@/utils/currency';
import { formatDate as utilFormatDate } from '@/utils/date';
import { getStatusBadgeStyle, formatStatusLabel } from '@/utils/status';

interface AdminOrderTableProps {
  orders: Order[];
  isLoading: boolean;
  
  // Status filter state
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
  
  // Search query state
  searchQuery: string;
  onSearchQueryChange: (query: string) => void;
  
  // Date range state
  dateFrom: string;
  onDateFromChange: (date: string) => void;
  dateTo: string;
  onDateToChange: (date: string) => void;

  // Sorting state
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  onSortChange: (column: string) => void;
  
  // Clear filters
  onClearFilters: () => void;
  hasActiveFilters: boolean;

  // Pagination state
  currentPage: number;
  totalPages: number;
  totalItems: number;
  onPageChange: (page: number) => void;
}

// Static data declared outside the component for rendering efficiency
const STATUS_CHIPS = [
  { label: 'All Orders', value: 'all' },
  { label: 'Received', value: 'received' },
  { label: 'Reviewed', value: 'reviewed' },
  { label: 'Quote Sent', value: 'quote_sent' },
  { label: 'Confirmed', value: 'confirmed' },
  { label: 'In Production', value: 'in_production' },
  { label: 'Ready', value: 'ready' },
  { label: 'Out for Delivery', value: 'out_for_delivery' },
  { label: 'Delivered', value: 'delivered' },
  { label: 'Cancelled', value: 'cancelled' },
];

export const AdminOrderTable: React.FC<AdminOrderTableProps> = ({
  orders,
  isLoading,
  statusFilter,
  onStatusFilterChange,
  searchQuery,
  onSearchQueryChange,
  dateFrom,
  onDateFromChange,
  dateTo,
  onDateToChange,
  sortBy,
  sortOrder,
  onSortChange,
  onClearFilters,
  hasActiveFilters,
  currentPage,
  totalPages,
  totalItems,
  onPageChange,
}) => {

  const renderSortIndicator = (columnName: string) => {
    if (sortBy !== columnName) {
      return <ArrowUpDown className="w-3 h-3 ml-1 text-slate-600 inline-block animate-pulse" />;
    }
    return sortOrder === 'asc' ? (
      <ArrowUp className="w-3 h-3 ml-1 text-blue-400 inline-block" />
    ) : (
      <ArrowDown className="w-3 h-3 ml-1 text-blue-400 inline-block" />
    );
  };

  // Performance Optimization: Memoize the table rows to prevent redundant DOM operations
  // when local states like searchQuery change on keystroke.
  const renderedTableRows = useMemo(() => {
    return orders.map((order) => (
      <tr
        key={order.id}
        className="hover:bg-slate-900/40 transition-colors duration-150 group border-b border-slate-900/40"
      >
        <td className="py-2.5 px-4 font-mono font-medium text-slate-200">
          {order.order_number}
        </td>
        <td className="py-2.5 px-4">
          <div className="flex flex-col">
            <span className="font-medium text-slate-300">{order.customer.name}</span>
            <span className="text-[10px] text-slate-500">{order.customer.email}</span>
          </div>
        </td>
        <td className="py-2.5 px-4 text-slate-400 font-mono">
          {order.customer.phone}
        </td>
        <td className="py-2.5 px-4">
          <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ${getStatusBadgeStyle(order.status)}`}>
            {formatStatusLabel(order.status)}
          </span>
        </td>
        <td className="py-2.5 px-4 text-right font-mono font-medium text-slate-300">
          {utilFormatCurrency(order.estimated_total)}
        </td>
        <td className="py-2.5 px-4 text-right font-mono font-medium text-emerald-400">
          {utilFormatCurrency(order.final_quoted_price)}
        </td>
        <td className="py-2.5 px-4 text-slate-400 font-medium">
          {utilFormatDate(order.created_at)}
        </td>
        <td className="py-2.5 px-4 text-center">
          <Link
            href={`/admin/orders/${order.id}`}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-medium text-blue-400 bg-blue-950/40 hover:bg-blue-900/40 border border-blue-900 hover:border-blue-700 rounded transition-all duration-150 focus:ring-1 focus:ring-blue-500 focus:outline-none"
          >
            <Eye className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Details</span>
          </Link>
        </td>
      </tr>
    ));
  }, [orders]);

  // Keypress event listener for table sorting headers (a11y)
  const handleSortKeyPress = (column: string, e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSortChange(column);
    }
  };

  return (
    <div className="space-y-4">
      {/* Controls: Search, Date Range, Status Chips */}
      <div className="space-y-4 bg-slate-950 border border-slate-800 p-4 rounded-lg">
        {/* Status Chips */}
        <div>
          <span className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2.5">
            Filter by Status
          </span>
          <div className="flex flex-wrap gap-1.5" role="group" aria-label="Filter orders by status">
            {STATUS_CHIPS.map((chip) => {
              const isActive = statusFilter === chip.value;
              const badgeStyle = getStatusBadgeStyle(chip.value);
              return (
                <button
                  key={chip.value}
                  type="button"
                  onClick={() => onStatusFilterChange(chip.value)}
                  aria-pressed={isActive}
                  className={`px-2.5 py-1 text-[11px] font-semibold rounded uppercase tracking-wider border transition-all duration-150 select-none focus:outline-none focus:ring-1 focus:ring-slate-700 ${
                    isActive
                      ? `${badgeStyle} shadow-sm ring-1 ring-slate-800`
                      : 'bg-slate-900/60 text-slate-400 border-slate-800/80 hover:bg-slate-900 hover:text-slate-200'
                  }`}
                >
                  {chip.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Input Controls Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 pt-2 border-t border-slate-900 text-xs">
          {/* Unified Search Input */}
          <div className="relative">
            <label htmlFor="search-orders-input" className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
              Search Orders
            </label>
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
              <input
                id="search-orders-input"
                type="text"
                placeholder="Search order #, customer name, phone..."
                value={searchQuery}
                onChange={(e) => onSearchQueryChange(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 rounded pl-8 pr-2.5 py-1.5 focus:border-blue-500 focus:outline-none placeholder-slate-600"
              />
            </div>
          </div>

          {/* Date Range Start (Constraint: Cannot be after dateTo) */}
          <div>
            <label htmlFor="date-from-input" className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
              Date From
            </label>
            <div className="relative">
              <Calendar className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-500 pointer-events-none" aria-hidden="true" />
              <input
                id="date-from-input"
                type="date"
                value={dateFrom}
                max={dateTo || undefined}
                onChange={(e) => onDateFromChange(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 rounded pl-8 pr-2.5 py-1.5 focus:border-blue-500 focus:outline-none font-mono"
              />
            </div>
          </div>

          {/* Date Range End (Constraint: Cannot be before dateFrom) */}
          <div>
            <label htmlFor="date-to-input" className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
              Date To
            </label>
            <div className="relative">
              <Calendar className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-500 pointer-events-none" aria-hidden="true" />
              <input
                id="date-to-input"
                type="date"
                value={dateTo}
                min={dateFrom || undefined}
                onChange={(e) => onDateToChange(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 rounded pl-8 pr-2.5 py-1.5 focus:border-blue-500 focus:outline-none font-mono"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main Table */}
      {isLoading ? (
        <div className="w-full flex items-center justify-center py-12 border border-slate-800 rounded-lg bg-slate-950" role="status" aria-live="polite">
          <div className="flex items-center space-x-2 text-slate-400">
            <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
            <span className="text-sm font-medium">Loading orders...</span>
          </div>
        </div>
      ) : orders.length === 0 ? (
        <div className="w-full text-center py-16 border border-dashed border-slate-850 rounded-lg bg-slate-950">
          <p className="text-slate-400 text-sm">No orders match the selected filter criteria.</p>
          {hasActiveFilters && (
            <button
              onClick={onClearFilters}
              type="button"
              className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-400 bg-rose-950/20 border border-rose-900 rounded hover:bg-rose-950/40 transition-colors uppercase tracking-wider"
            >
              <X className="w-3.5 h-3.5" />
              <span>Clear Filters</span>
            </button>
          )}
        </div>
      ) : (
        <div className="w-full overflow-x-auto border border-slate-800 rounded-lg bg-slate-950">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 uppercase font-semibold select-none">
                <th 
                  onClick={() => onSortChange('order_number')}
                  onKeyDown={(e) => handleSortKeyPress('order_number', e)}
                  role="columnheader"
                  tabIndex={0}
                  aria-sort={sortBy === 'order_number' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                  className="py-2.5 px-4 font-medium tracking-wider cursor-pointer hover:text-slate-200 transition-colors focus:bg-slate-900/80 focus:outline-none"
                >
                  <span className="flex items-center">
                    Order Number {renderSortIndicator('order_number')}
                  </span>
                </th>
                <th className="py-2.5 px-4 font-medium tracking-wider" role="columnheader">Customer</th>
                <th className="py-2.5 px-4 font-medium tracking-wider" role="columnheader">Phone</th>
                <th className="py-2.5 px-4 font-medium tracking-wider" role="columnheader">Status</th>
                <th 
                  onClick={() => onSortChange('estimated_total')}
                  onKeyDown={(e) => handleSortKeyPress('estimated_total', e)}
                  role="columnheader"
                  tabIndex={0}
                  aria-sort={sortBy === 'estimated_total' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                  className="py-2.5 px-4 font-medium tracking-wider text-right cursor-pointer hover:text-slate-200 transition-colors focus:bg-slate-900/80 focus:outline-none"
                >
                  <span className="flex items-center justify-end">
                    Estimated Total {renderSortIndicator('estimated_total')}
                  </span>
                </th>
                <th 
                  onClick={() => onSortChange('final_quoted_price')}
                  onKeyDown={(e) => handleSortKeyPress('final_quoted_price', e)}
                  role="columnheader"
                  tabIndex={0}
                  aria-sort={sortBy === 'final_quoted_price' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                  className="py-2.5 px-4 font-medium tracking-wider text-right cursor-pointer hover:text-slate-200 transition-colors focus:bg-slate-900/80 focus:outline-none"
                >
                  <span className="flex items-center justify-end">
                    Final Quote {renderSortIndicator('final_quoted_price')}
                  </span>
                </th>
                <th 
                  onClick={() => onSortChange('created_at')}
                  onKeyDown={(e) => handleSortKeyPress('created_at', e)}
                  role="columnheader"
                  tabIndex={0}
                  aria-sort={sortBy === 'created_at' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                  className="py-2.5 px-4 font-medium tracking-wider cursor-pointer hover:text-slate-200 transition-colors focus:bg-slate-900/80 focus:outline-none"
                >
                  <span className="flex items-center">
                    Created Date {renderSortIndicator('created_at')}
                  </span>
                </th>
                <th className="py-2.5 px-4 font-medium tracking-wider text-center" role="columnheader">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {renderedTableRows}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination Footer */}
      {!isLoading && orders.length > 0 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-850 pt-4 text-xs select-none">
          <div className="text-slate-400">
            Showing Page <span className="text-slate-200 font-semibold">{currentPage}</span> of{' '}
            <span className="text-slate-200 font-semibold">{totalPages}</span>{' '}
            <span className="text-slate-500 font-mono">({totalItems} items total)</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onPageChange(Math.max(currentPage - 1, 1))}
              disabled={currentPage === 1}
              type="button"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 font-semibold text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 rounded transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed uppercase tracking-wider focus:outline-none focus:ring-1 focus:ring-slate-700"
            >
              <ChevronLeft className="w-4 h-4" aria-hidden="true" />
              <span>Previous</span>
            </button>
            <button
              onClick={() => onPageChange(Math.min(currentPage + 1, totalPages))}
              disabled={currentPage === totalPages}
              type="button"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 font-semibold text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 rounded transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed uppercase tracking-wider focus:outline-none focus:ring-1 focus:ring-slate-700"
            >
              <span>Next</span>
              <ChevronRight className="w-4 h-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
