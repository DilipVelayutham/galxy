'use client';

import React, { useState, useEffect } from 'react';
import Layout from '../../../../components/shared/Layout';
import Loading from '../../../../components/shared/Loading';
import ErrorState from '../../../../components/shared/ErrorState';
import FilterBar from '../../../../components/shared/FilterBar';
import AIUsageStats from '../../../../components/admin/AIUsageStats';
import { API_BASE_URL } from '../../../../components/shared/ApiClient';

interface AIUsageStatsData {
  total_generations: number;
  successful: number;
  failed: number;
  avg_generation_time_ms: number;
  cache_hit_rate?: number;
  generations_by_category: {
    category_id: string;
    category_name: string;
    count: number;
  }[];
}

export default function AIUsageAnalyticsPage() {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<AIUsageStatsData | null>(null);
  
  // Local state to sync with FilterBar selections
  const [filters, setFilters] = useState({
    category_id: '',
    date_from: '',
    date_to: '',
  });

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const queryParams = new URLSearchParams();
      if (filters.category_id) queryParams.append('category_id', filters.category_id);
      if (filters.date_from) queryParams.append('date_from', filters.date_from);
      if (filters.date_to) queryParams.append('date_to', filters.date_to);

      const url = `${API_BASE_URL}/api/admin/analytics/ai-usage?${queryParams.toString()}`;
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
      });
      
      const result = await response.json();
      
      if (response.ok && result.success) {
        setStats(result.data);
      } else {
        setError(result?.message || 'Failed to fetch AI usage analytics data.');
      }
    } catch (err: any) {
      setError(err?.message || 'An error occurred while loading dashboard statistics.');
    } finally {
      setLoading(false);
    }
  };

  // Re-fetch when filters change
  useEffect(() => {
    fetchStats();
  }, [filters]);

  const handleFilterChange = (dateFrom: string, dateTo: string, categoryId: string) => {
    setFilters({
      date_from: dateFrom,
      date_to: dateTo,
      category_id: categoryId,
    });
  };

  return (
    <Layout title="AI Usage Analytics" activeTab="analytics-ai-usage">
      <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 text-galxy-primary">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-galxy-charcoal pb-5 space-y-4 md:space-y-0">
          <div>
            <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-galxy-violet via-galxy-primary to-galxy-blue tracking-tight">
              AI Generation Analytics
            </h1>
            <p className="text-galxy-muted mt-2 text-sm md:text-base">
              Monitor and evaluate artificial intelligence prompts, latency metrics, cache ratios, and response errors.
            </p>
          </div>
        </div>

        {/* Shared Filter Bar component */}
        <div className="bg-galxy-charcoal border border-galxy-charcoal/60 rounded-xl p-4 shadow-xl backdrop-blur-md">
          <FilterBar onFilter={handleFilterChange} />
        </div>

        {/* Dynamic State Rendering */}
        {loading ? (
          <Loading />
        ) : error ? (
          <div className="h-96 flex items-center justify-center">
            <ErrorState message={error} onRetry={fetchStats} />
          </div>
        ) : stats ? (
          <AIUsageStats stats={stats} />
        ) : (
          <div className="text-center text-galxy-muted py-16">
            No statistics data found matching the current filters.
          </div>
        )}
      </div>
    </Layout>
  );
}
