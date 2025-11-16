'use client';

import { useAuth } from '@/lib/hooks/useAuth';
import { useCreditProfile } from '@/lib/hooks/queries';
import { useLoans } from '@/lib/hooks/queries';

export const dynamic = 'force-dynamic';

export default function CustomerDashboard() {
  const { user } = useAuth();
  const { data: creditProfile, isLoading: profileLoading } = useCreditProfile();
  const { data: loans, isLoading: loansLoading } = useLoans();

  const activeLoans = loans?.filter((loan) => loan.status === 'ACTIVE') || [];
  const pendingLoans = loans?.filter((loan) => loan.status === 'PENDING') || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.name}!
        </h1>
          <p className="mt-2 text-gray-600">
          Here&apos;s your Shift overview
        </p>
      </div>

      {/* Credit Profile Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Credit Profile
        </h2>
        {profileLoading ? (
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-500">Loading credit profile...</p>
          </div>
        ) : creditProfile ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Credit Score
              </h3>
              <p className="text-3xl font-bold text-gray-900">
                {creditProfile.score}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Credit Tier
              </h3>
              <p className="text-3xl font-bold text-primary-600">
                {creditProfile.tier}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Max BNPL Limit
              </h3>
              <p className="text-3xl font-bold text-green-600">
                UGX {creditProfile.max_bnpl_limit.toLocaleString()}
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-500">No credit profile available</p>
          </div>
        )}
      </div>

      {/* Loans Summary */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          My Loans
        </h2>
        {loansLoading ? (
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-500">Loading loans...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Active Loans
              </h3>
              <p className="text-3xl font-bold text-gray-900">
                {activeLoans.length}
              </p>
              {activeLoans.length > 0 && (
                <p className="text-sm text-gray-500 mt-2">
                  Total outstanding: UGX{' '}
                  {activeLoans
                    .reduce((sum, loan) => {
                      const unpaidInstallments = loan.installments.filter(i => !i.paid);
                      return sum + unpaidInstallments.reduce((s, i) => s + i.amount, 0);
                    }, 0)
                    .toLocaleString()}
                </p>
              )}
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                Pending Loans
              </h3>
              <p className="text-3xl font-bold text-yellow-600">
                {pendingLoans.length}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Quick Actions
        </h2>
        <div className="flex space-x-4">
          <a
            href="/customer/marketplace"
            className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors shadow-md hover:shadow-lg"
          >
            Browse Marketplace
          </a>
          <a
            href="/customer/loans"
            className="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300 transition"
          >
            View All Loans
          </a>
        </div>
      </div>
    </div>
  );
}

