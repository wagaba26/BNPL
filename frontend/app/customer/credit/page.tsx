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
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';

// Circular Progress Component
function CircularScore({ score, maxScore = 850 }: { score: number; maxScore?: number }) {
  const percentage = Math.min((score / maxScore) * 100, 100);
  const circumference = 2 * Math.PI * 70; // radius = 70
  const offset = circumference - (percentage / 100) * circumference;

  const getScoreColor = (score: number) => {
    if (score >= 700) return 'text-green-600';
    if (score >= 600) return 'text-indigo-600';
    if (score >= 500) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRingColor = (score: number) => {
    if (score >= 700) return 'stroke-green-600';
    if (score >= 600) return 'stroke-indigo-600';
    if (score >= 500) return 'stroke-yellow-600';
    return 'stroke-red-600';
  };

  return (
    <div className="relative w-48 h-48 mx-auto">
      <svg className="transform -rotate-90 w-48 h-48">
        {/* Background circle */}
        <circle
          cx="96"
          cy="96"
          r="70"
          stroke="currentColor"
          strokeWidth="12"
          fill="transparent"
          className="text-gray-200"
        />
        {/* Progress circle */}
        <circle
          cx="96"
          cy="96"
          r="70"
          stroke="currentColor"
          strokeWidth="12"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={`${getRingColor(score)} transition-all duration-1000`}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <p className={`text-4xl font-bold ${getScoreColor(score)}`}>{score}</p>
          <p className="text-xs text-gray-500 mt-1">out of {maxScore}</p>
        </div>
      </div>
    </div>
  );
}

export default function CreditPage() {
  const {
    data: profile,
    isLoading: profileLoading,
    error: profileError,
    refetch: refetchProfile,
  } = useCreditProfile();

  const eventsQuery = useCreditScoreEvents({ page: 1, pageSize: 10 });
  const {
    data: events,
    isLoading: eventsLoading,
    error: eventsError,
  } = eventsQuery;
  const refetchEvents = eventsQuery.refetch;

  const isLoading = profileLoading || eventsLoading;
  const error = profileError || eventsError;

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto w-full">
        <PageHeader title="Credit Score" description="View your credit score and activity" />
        <div className="space-y-6">
          <Card>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[1, 2, 3, 4].map((i) => (
                  <Skeleton key={i} className="h-24" />
                ))}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <Skeleton className="h-64" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto w-full">
        <PageHeader title="Credit Score" description="View your credit score and activity" />
        <Card>
          <CardContent className="p-6">
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
                <h3 className="text-sm font-semibold text-red-800">
                  Failed to load credit information
                </h3>
                <p className="mt-1 text-sm text-red-700">
                  {error.message || 'An error occurred while loading your credit data.'}
                </p>
                <div className="mt-4">
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => {
                      refetchProfile();
                      refetchEvents();
                    }}
                  >
                    Try Again
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const recentEvents = events?.slice(0, 10) || [];

  return (
    <div className="max-w-7xl mx-auto w-full">
      <PageHeader
        title="Credit Score"
        description="View your credit score and activity"
      />

      {/* Credit Score Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Circular Score Visualization */}
        <Card>
          <CardContent className="p-6 text-center">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-6">
              Credit Score
            </h3>
            {profile?.score ? (
              <CircularScore score={profile.score} />
            ) : (
              <div className="h-48 flex items-center justify-center">
                <p className="text-gray-500">No score available</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tier and Limit Card */}
        <Card>
          <CardContent className="p-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                  Credit Tier
                </h3>
                {profile?.tier ? (
                  <Badge variant="info" className="text-base px-4 py-2">
                    Tier {profile.tier}
                  </Badge>
                ) : (
                  <p className="text-gray-500">N/A</p>
                )}
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                  Max BNPL Limit
                </h3>
                {profile?.maxBnplLimit ? (
                  <p className="text-3xl font-bold text-green-600">
                    {formatCurrency(profile.maxBnplLimit)}
                  </p>
                ) : (
                  <p className="text-gray-500">N/A</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Last Updated Card */}
        <Card>
          <CardContent className="p-6">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
              Last Updated
            </h3>
            {profile?.lastRecalculatedAt ? (
              <div className="space-y-2">
                <p className="text-2xl font-bold text-gray-900">
                  {formatRelativeTime(profile.lastRecalculatedAt)}
                </p>
                <p className="text-sm text-gray-500">
                  {formatDate(profile.lastRecalculatedAt)}
                </p>
              </div>
            ) : (
              <p className="text-gray-500">Never</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Credit Activity */}
      <Card>
        <CardContent className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Recent Credit Activity</h2>

          {eventsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-16" />
              ))}
            </div>
          ) : eventsError ? (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">
                Failed to load credit events. Please try again.
              </p>
              <Button variant="primary" size="sm" onClick={() => refetchEvents?.()}>
                Retry
              </Button>
            </div>
          ) : recentEvents.length === 0 ? (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-gray-500 mb-2">No credit activity yet.</p>
              <p className="text-sm text-gray-400">
                Your credit events will appear here as they occur.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Timeline */}
              <div className="relative">
                {recentEvents.map((event, index) => {
                  const isPositive = event.delta > 0;
                  const isNegative = event.delta < 0;

                  return (
                    <div key={event.id} className="relative flex gap-4 pb-6 last:pb-0">
                      {/* Timeline Line */}
                      {index < recentEvents.length - 1 && (
                        <div className="absolute left-4 top-12 bottom-0 w-0.5 bg-gray-200" />
                      )}

                      {/* Timeline Dot */}
                      <div className="relative z-10 flex-shrink-0">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                            isPositive
                              ? 'bg-green-50 border-green-500'
                              : isNegative
                              ? 'bg-red-50 border-red-500'
                              : 'bg-gray-50 border-gray-500'
                          }`}
                        >
                          {isPositive ? (
                            <svg
                              className="w-4 h-4 text-green-600"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          ) : isNegative ? (
                            <svg
                              className="w-4 h-4 text-red-600"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                              />
                            </svg>
                          ) : (
                            <div className="w-2 h-2 rounded-full bg-gray-500" />
                          )}
                        </div>
                      </div>

                      {/* Event Content */}
                      <div className="flex-1 bg-gray-50 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="text-sm font-semibold text-gray-900">
                              {getEventTypeLabel(event.eventType)}
                            </p>
                            <p className="text-xs text-gray-500 mt-0.5">
                              {formatDate(event.createdAt)} • {formatRelativeTime(event.createdAt)}
                            </p>
                          </div>
                          <span className={getDeltaColorClass(event.delta)}>
                            {formatDelta(event.delta)}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-gray-600">Score:</span>
                          <span className="font-medium text-gray-900">{event.scoreBefore}</span>
                          <svg
                            className="w-4 h-4 text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M9 5l7 7-7 7"
                            />
                          </svg>
                          <span className="font-bold text-gray-900">{event.scoreAfter}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
