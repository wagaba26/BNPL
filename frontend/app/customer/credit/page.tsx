'use client';

import { useCreditProfile, useCreditScoreEvents } from '@/lib/hooks/useCredit';
import {
  getEventTypeLabel,
  formatCurrency,
  formatDate,
  formatRelativeTime,
  getDeltaColorClass,
  formatDelta,
} from '@/lib/utils/creditHelpers';

export default function CreditPage() {
  const {
    data: profile,
    isLoading: profileLoading,
    error: profileError,
    refetch: refetchProfile,
  } = useCreditProfile();

  const {
    data: events,
    isLoading: eventsLoading,
    error: eventsError,
    refetch: refetchEvents,
  } = useCreditScoreEvents({ page: 1, pageSize: 5 });

  const isLoading = profileLoading || eventsLoading;
  const error = profileError || eventsError;

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Credit Dashboard</h1>
          <p className="mt-2 text-gray-600">View your credit score and activity</p>
        </div>

        {/* Loading skeletons */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="h-24 bg-gray-200 rounded"></div>
              <div className="h-24 bg-gray-200 rounded"></div>
              <div className="h-24 bg-gray-200 rounded"></div>
              <div className="h-24 bg-gray-200 rounded"></div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Credit Dashboard</h1>
          <p className="mt-2 text-gray-600">View your credit score and activity</p>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">
                Failed to load credit information
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>
                  {error.message || 'An error occurred while loading your credit data.'}
                </p>
              </div>
              <div className="mt-4">
                <button
                  onClick={() => {
                    refetchProfile();
                    refetchEvents();
                  }}
                  className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const recentEvents = events?.slice(0, 5) || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Credit Dashboard</h1>
        <p className="mt-2 text-gray-600">View your credit score and activity</p>
      </div>

      {/* Credit Profile Card */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Credit Score */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">Credit Score</h3>
            <p className="text-4xl font-bold text-gray-900">
              {profile?.score ?? 'N/A'}
            </p>
          </div>

          {/* Tier */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">Credit Tier</h3>
            <p className="text-4xl font-bold text-primary-600 capitalize">
              {profile?.tier ? `Tier ${profile.tier}` : 'N/A'}
            </p>
          </div>

          {/* Max BNPL Limit */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Max BNPL Limit
            </h3>
            <p className="text-4xl font-bold text-green-600">
              {profile?.maxBnplLimit ? formatCurrency(profile.maxBnplLimit) : 'N/A'}
            </p>
          </div>

          {/* Last Updated */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">Last Updated</h3>
            <p className="text-lg font-semibold text-gray-900">
              {profile?.lastRecalculatedAt
                ? formatRelativeTime(profile.lastRecalculatedAt)
                : 'Never'}
            </p>
            {profile?.lastRecalculatedAt && (
              <p className="text-sm text-gray-500 mt-1">
                {formatDate(profile.lastRecalculatedAt)}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Credit Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Recent Credit Activity
        </h2>

        {eventsLoading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded animate-pulse"></div>
            ))}
          </div>
        ) : eventsError ? (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">
              Failed to load credit events. Please try again.
            </p>
            <button
              onClick={() => refetchEvents()}
              className="bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700"
            >
              Retry
            </button>
          </div>
        ) : recentEvents.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No credit activity yet.</p>
            <p className="text-sm text-gray-400 mt-2">
              Your credit events will appear here as they occur.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Event
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Change
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentEvents.map((event) => (
                  <tr key={event.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{formatDate(event.createdAt)}</div>
                      <div className="text-xs text-gray-400">
                        {formatRelativeTime(event.createdAt)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {getEventTypeLabel(event.eventType)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={getDeltaColorClass(event.delta)}>
                        {formatDelta(event.delta)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className="font-medium">{event.scoreBefore}</span>
                      <span className="mx-2 text-gray-400">→</span>
                      <span className="font-semibold">{event.scoreAfter}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

