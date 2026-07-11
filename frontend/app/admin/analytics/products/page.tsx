'use client';

import React, { useState, useEffect } from 'react';
import Layout from '../../../../components/shared/Layout';
import Loading from '../../../../components/shared/Loading';
import ErrorState from '../../../../components/shared/ErrorState';
import FilterBar from '../../../../components/shared/FilterBar';
import ProductAnalyticsTable from '../../../../components/admin/ProductAnalyticsTable';
import { API_BASE_URL } from '../../../../components/shared/ApiClient';

interface ProductAnalyticsItem {
  product_id: string;
  title: string;
  category_name: string;
  views: number;
  wishlist_count: number;
  order_count: number;
  conversion_rate: number;
}

export default function ProductAnalyticsPage() {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ProductAnalyticsItem[]>([]);

  // Page, limit, total states for pagination
  const [page, setPage] = useState<number>(1);
  const [limit, setLimit] = useState<number>(10);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(0);

  // Sorting state (default: "views")
  const [sort, setSort] = useState<string>('views');

  // FilterBar selections
  const [filters, setFilters] = useState({
    category_id: '',
    date_from: '',
    date_to: '',
  });

  const fetchProductAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const queryParams = new URLSearchParams();
      if (filters.category_id) queryParams.append('category_id', filters.category_id);
      if (filters.date_from) queryParams.append('date_from', filters.date_from);
      if (filters.date_to) queryParams.append('date_to', filters.date_to);
      if (sort) queryParams.append('sort', sort);
      queryParams.append('page', page.toString());
      queryParams.append('limit', limit.toString());

      const url = `${API_BASE_URL}/api/admin/analytics/products?${queryParams.toString()}`;
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.statusText}`);
      }

      const result = await response.json();

      if (result && result.success) {
        setData(result.data);
        setPage(result.page);
        setLimit(result.limit);
        setTotal(result.total);
        setTotalPages(result.totalPages);
      } else {
        setError(result?.message || 'Failed to fetch product analytics data.');
      }
    } catch (err: any) {
      setError(err?.message || 'An error occurred while loading product analytics.');
    } finally {
      setLoading(false);
    }
  };

  // Re-fetch when filters, sorting, or pagination changes
  useEffect(() => {
    fetchProductAnalytics();
  }, [filters, sort, page, limit]);

  const handleFilter = (dateFrom: string, dateTo: string, categoryId: string) => {
    setFilters({
      category_id: categoryId,
      date_from: dateFrom ? `${dateFrom}T00:00:00Z` : '',
      date_to: dateTo ? `${dateTo}T23:59:59Z` : '',
    });
    setPage(1); // Reset to page 1 on new filter search
  };

  const handleSortChange = (newSort: string) => {
    setSort(newSort);
    setPage(1); // Reset to page 1 on sort change
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handleLimitChange = (newLimit: number) => {
    setLimit(newLimit);
    setPage(1); // Reset to page 1 when count changes
  };

  return (
    <Layout>
      <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 text-textPrimary">

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-slate-800 pb-5 space-y-4 md:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-textPrimary tracking-tight">
              Product Performance Analytics
            </h1>
            <p className="text-textMuted mt-2 text-sm md:text-base">
              Track product popularity, wishlist inclusions, order conversion rates, and performance across categories.
            </p>
          </div>
        </div>

        {/* Filter Bar */}
        <FilterBar onFilter={handleFilter} />

        {/* Dynamic Table State Render */}
        {loading ? (
          <div className="h-96 flex items-center justify-center">
            <Loading />
          </div>
        ) : error ? (
          <div className="h-96 flex items-center justify-center">
            <ErrorState message={error} />
          </div>
        ) : (
          <ProductAnalyticsTable
            data={data}
            page={page}
            limit={limit}
            total={total}
            totalPages={totalPages}
            sort={sort}
            onSortChange={handleSortChange}
            onPageChange={handlePageChange}
            onLimitChange={handleLimitChange}
          />
        )}
      </div>
    </Layout>
  );
}
