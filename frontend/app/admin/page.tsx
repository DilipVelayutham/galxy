'use client';
import React, { useEffect, useState } from 'react';
import Layout from '../../components/shared/Layout';
import FilterBar from '../../components/shared/FilterBar';
import Loading from '../../components/shared/Loading';
import ErrorState from '../../components/shared/ErrorState';
import { ApiClient } from '../../components/shared/ApiClient';
import OrdersByStatusChart from '../../components/admin/OrdersByStatusChart';
import TopCategoriesChart from '../../components/admin/TopCategoriesChart';
import StatCard from '../../components/admin/StatCard';

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async (dateFrom?: string, dateTo?: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await ApiClient.getDashboardStats(dateFrom, dateTo);
      setStats(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleFilter = (dateFrom: string, dateTo: string, categoryId: string) => {
    // categoryId is not currently used by the stats API, but we pass dateFrom and dateTo
    fetchStats(dateFrom, dateTo);
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-[#F4F4F7]">Dashboard</h2>
        </div>

        <FilterBar onFilter={handleFilter} />

        {loading && <Loading />}

        {error && <ErrorState message={error} />}

        {/* Stats Grid */}
        {!loading && !error && stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Orders"
              value={stats.total_orders_in_range}
            />
            <StatCard
              title="Est. Revenue"
              value={`$${stats.estimated_revenue_in_range.toLocaleString()}`}
              isEstimate={true}
              accentColor="#18E7FF"
            />
            <StatCard
              title="Pending Reviews"
              value={stats.pending_review_count}
              href="/admin/orders"
              accentColor="#FF3366"
            />
            <StatCard
              title="Reviews To Moderate"
              value={stats.pending_reviews_to_moderate}
              href="/admin/reviews"
              accentColor="#FFB020"
            />
          </div>
        )}

        {/* Charts */}
        {!loading && !error && stats && (
          <div className="mt-8 flex flex-col gap-6">
            <OrdersByStatusChart data={stats.orders_by_status} />
            <TopCategoriesChart data={stats.top_categories} />
          </div>
        )}
      </div>
    </Layout>
  );
}
