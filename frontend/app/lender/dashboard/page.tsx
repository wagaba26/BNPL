'use client';

import { useLenderStats } from '@/lib/hooks/queries';

export default function LenderDashboard() {
  const { data: stats, isLoading, error } = useLenderStats();

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p className="text-gray-500">Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Failed to load dashboard data. Please try again later.
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Lender Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Overview of your loan portfolio
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">
            Active Loans
          </h3>
          <p className="text-3xl font-bold text-gray-900">
            {stats?.active_loans_count || 0}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">
            Total Principal Outstanding
          </h3>
          <p className="text-3xl font-bold text-primary-600">
            UGX {stats?.total_principal_outstanding.toLocaleString() || '0'}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">
            Total Interest Earned
          </h3>
          <p className="text-3xl font-bold text-green-600">
            UGX {stats?.total_interest_earned.toLocaleString() || '0'}
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <a
          href="/lender/loans"
          className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors shadow-md hover:shadow-lg inline-block"
        >
          View All Loans
        </a>
      </div>
    </div>
  );
}

