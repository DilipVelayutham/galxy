'use client';

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { adminOrderService } from '@/lib/api';
import { Order, OrderStatus } from '@/types/admin';
import { AdminOrderTable } from '@/components/admin/AdminOrderTable';
import { getErrorMessage } from '@/utils/error';
import { X, Loader2 } from 'lucide-react';

function AdminOrdersPageContent() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // URL state variables
  const statusFilter = searchParams.get('status') || 'all';
  const urlSearch = searchParams.get('search') || '';
  const urlDateFrom = searchParams.get('date_from') || '';
  const urlDateTo = searchParams.get('date_to') || '';
  const currentPage = parseInt(searchParams.get('page') || '1', 10);
  const urlSortBy = searchParams.get('sort_by') || 'created_at';
  const urlSortOrder = (searchParams.get('sort_order') || 'desc') as 'asc' | 'desc';

  // Local state for table data and loading
  const [orders, setOrders] = useState<Order[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Local input states to avoid input lag during typing
  const [searchVal, setSearchVal] = useState(urlSearch);
  const [dateFromVal, setDateFromVal] = useState(urlDateFrom);
  const [dateToVal, setDateToVal] = useState(urlDateTo);

  // Sync local inputs when URL state changes (e.g. back navigation or clear filters)
  useEffect(() => {
    setSearchVal(urlSearch);
  }, [urlSearch]);

  useEffect(() => {
    setDateFromVal(urlDateFrom);
  }, [urlDateFrom]);

  useEffect(() => {
    setDateToVal(urlDateTo);
  }, [urlDateTo]);

  // Unified helper to push URL queries
  const updateQuery = useCallback((updates: Record<string, string | number | null>) => {
    const nextParams = new URLSearchParams(searchParams.toString());
    Object.entries(updates).forEach(([key, val]) => {
      if (val === null || val === undefined || val === '') {
        nextParams.delete(key);
      } else {
        nextParams.set(key, String(val));
      }
    });
    // Always fallback to page 1 on filter changes unless explicitly specified
    if (!('page' in updates) && updates.page !== null) {
      nextParams.set('page', '1');
    }
    router.push(`${pathname}?${nextParams.toString()}`);
  }, [searchParams, pathname, router]);

  // Debouncing search value (300ms idle timeout)
  useEffect(() => {
    const handler = setTimeout(() => {
      const currentUrlSearch = searchParams.get('search') || '';
      if (searchVal.trim() !== currentUrlSearch) {
        updateQuery({ search: searchVal.trim() });
      }
    }, 300);
    return () => clearTimeout(handler);
  }, [searchVal, searchParams, updateQuery]);

  // Fetch orders from API based on query parameters
  const fetchOrders = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await adminOrderService.getOrders({
        page: currentPage,
        limit: 10,
        status: statusFilter === 'all' ? undefined : (statusFilter as OrderStatus),
        search: urlSearch || undefined,
        date_from: urlDateFrom || undefined,
        date_to: urlDateTo || undefined,
        sort_by: urlSortBy,
        sort_order: urlSortOrder,
      });

      setOrders(response.orders);
      setTotalPages(response.pagination.totalPages);
      setTotalItems(response.pagination.total);
    } catch (err: unknown) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, statusFilter, urlSearch, urlDateFrom, urlDateTo, urlSortBy, urlSortOrder]);

  // Re-run fetch when searchParams change
  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const handleStatusFilterChange = useCallback((status: string) => {
    updateQuery({ status });
  }, [updateQuery]);

  const handleDateFromChange = useCallback((date: string) => {
    setDateFromVal(date);
    updateQuery({ date_from: date });
  }, [updateQuery]);

  const handleDateToChange = useCallback((date: string) => {
    setDateToVal(date);
    updateQuery({ date_to: date });
  }, [updateQuery]);

  const handleSortChange = useCallback((column: string) => {
    const nextOrder = urlSortBy === column && urlSortOrder === 'asc' ? 'desc' : 'asc';
    updateQuery({
      sort_by: column,
      sort_order: nextOrder,
    });
  }, [urlSortBy, urlSortOrder, updateQuery]);

  const handlePageChange = useCallback((page: number) => {
    updateQuery({ page });
  }, [updateQuery]);

  const handleClearFilters = useCallback(() => {
    setSearchVal('');
    setDateFromVal('');
    setDateToVal('');
    router.push(pathname);
  }, [pathname, router]);

  const hasActiveFilters =
    statusFilter !== 'all' ||
    urlSearch !== '' ||
    urlDateFrom !== '' ||
    urlDateTo !== '' ||
    currentPage !== 1 ||
    urlSortBy !== 'created_at' ||
    urlSortOrder !== 'desc';

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 uppercase tracking-wide">
            Order Management
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Search, filter, status lifecycle control, and final quotations.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500 font-mono">
            Total Items: <span className="text-slate-300 font-semibold">{totalItems}</span>
          </span>
          {hasActiveFilters && (
            <button
              onClick={handleClearFilters}
              type="button"
              className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold text-rose-400 hover:text-rose-300 bg-rose-950/20 border border-rose-900/50 hover:border-rose-900 rounded transition-all duration-150 uppercase tracking-wider"
            >
              <X className="w-3.5 h-3.5" />
              <span>Clear Filters</span>
            </button>
          )}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-rose-950/20 border border-rose-900/50 p-4 rounded-lg text-rose-400 text-xs" role="alert">
          <p className="font-semibold uppercase tracking-wider">Error Fetching Orders</p>
          <p className="mt-1 leading-relaxed">{error}</p>
          <button
            onClick={fetchOrders}
            type="button"
            className="mt-3 bg-rose-900 hover:bg-rose-800 text-white font-semibold py-1 px-3 rounded uppercase tracking-wider transition-colors duration-150"
          >
            Retry
          </button>
        </div>
      )}

      {/* Table Container */}
      {!error && (
        <AdminOrderTable
          orders={orders}
          isLoading={isLoading}
          statusFilter={statusFilter}
          onStatusFilterChange={handleStatusFilterChange}
          searchQuery={searchVal}
          onSearchQueryChange={setSearchVal}
          dateFrom={dateFromVal}
          onDateFromChange={handleDateFromChange}
          dateTo={dateToVal}
          onDateToChange={handleDateToChange}
          sortBy={urlSortBy}
          sortOrder={urlSortOrder}
          onSortChange={handleSortChange}
          onClearFilters={handleClearFilters}
          hasActiveFilters={hasActiveFilters}
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={totalItems}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  );
}

export default function AdminOrdersPage() {
  return (
    <Suspense fallback={
      <div className="w-full flex flex-col items-center justify-center py-24 gap-3 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <span className="text-sm font-medium animate-pulse">Loading orders dashboard...</span>
      </div>
    }>
      <AdminOrdersPageContent />
    </Suspense>
  );
}

