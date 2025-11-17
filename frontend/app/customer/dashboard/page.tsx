'use client';

import { useAuth } from '@/lib/hooks/useAuth';
import { useCreditProfile } from '@/lib/hooks/queries';
import { useLoans } from '@/lib/hooks/queries';
import { Card, CardContent } from '@/components/ui/Card';
import { PageHeader } from '@/components/ui/PageHeader';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

export default function CustomerDashboard() {
  const { user } = useAuth();
  const { data: creditProfile, isLoading: profileLoading } = useCreditProfile();
  const { data: loans, isLoading: loansLoading } = useLoans();

  const activeLoans = loans?.filter((loan) => loan.status === 'ACTIVE') || [];
  const pendingLoans = loans?.filter((loan) => loan.status === 'PENDING') || [];
  const totalOutstanding = activeLoans.reduce(
    (sum, loan) => sum + (loan.total_amount - loan.deposit_amount),
    0
  );

  return (
    <div className="max-w-7xl mx-auto w-full space-y-8">
      {/* Welcome Header */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary-500 to-accent-500 p-8 md:p-10 text-white shadow-fintech-lg">
        <div className="relative z-10">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            Welcome back, {user?.name || 'there'}! 👋
          </h1>
          <p className="text-primary-100 text-lg">
            Here's your financial overview at a glance
          </p>
        </div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-accent-400/20 rounded-full -ml-24 -mb-24 blur-2xl"></div>
      </div>

      {/* Key Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Credit Score Card */}
        <Card hover className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary-100/30 rounded-full -mr-16 -mt-16 blur-2xl"></div>
          <CardContent className="p-6 relative z-10">
            {profileLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-8 w-16" />
              </div>
            ) : creditProfile ? (
              <>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Credit Score
                  </p>
                  <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center">
                    <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <p className="text-5xl font-bold text-slate-900 mb-4 count-up">
                  {creditProfile.score}
                </p>
                <div className="mt-4 h-2.5 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary-600 to-accent-500 rounded-full transition-all duration-1000"
                    style={{
                      width: `${Math.min((creditProfile.score / 850) * 100, 100)}%`,
                    }}
                  />
                </div>
                <p className="text-xs text-slate-500 mt-2">Out of 850</p>
              </>
            ) : (
              <p className="text-slate-500">No credit profile</p>
            )}
          </CardContent>
        </Card>

        {/* Tier Card */}
        <Card hover className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-accent-100/30 rounded-full -mr-16 -mt-16 blur-2xl"></div>
          <CardContent className="p-6 relative z-10">
            {profileLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-8 w-12" />
              </div>
            ) : creditProfile ? (
              <>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Credit Tier
                  </p>
                  <div className="w-10 h-10 rounded-xl bg-accent-100 flex items-center justify-center">
                    <svg className="w-5 h-5 text-accent-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                    </svg>
                  </div>
                </div>
                <p className="text-5xl font-bold bg-gradient-to-r from-primary-600 to-accent-500 bg-clip-text text-transparent mb-2 count-up">
                  {creditProfile.tier}
                </p>
                <p className="text-sm text-slate-500">
                  Current tier level
                </p>
              </>
            ) : (
              <p className="text-slate-500">No tier available</p>
            )}
          </CardContent>
        </Card>

        {/* Max BNPL Limit Card */}
        <Card hover className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-success-100/30 rounded-full -mr-16 -mt-16 blur-2xl"></div>
          <CardContent className="p-6 relative z-10">
            {profileLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-8 w-24" />
              </div>
            ) : creditProfile ? (
              <>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Max BNPL Limit
                  </p>
                  <div className="w-10 h-10 rounded-xl bg-success-100 flex items-center justify-center">
                    <svg className="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <p className="text-3xl font-bold text-success-600 mb-2 count-up">
                  UGX {creditProfile.max_bnpl_limit.toLocaleString()}
                </p>
                <p className="text-sm text-slate-500">
                  Available credit
                </p>
              </>
            ) : (
              <p className="text-slate-500">No limit available</p>
            )}
          </CardContent>
        </Card>

        {/* Active Loans Count Card */}
        <Card hover className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-warning-100/30 rounded-full -mr-16 -mt-16 blur-2xl"></div>
          <CardContent className="p-6 relative z-10">
            {loansLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-28" />
                <Skeleton className="h-8 w-12" />
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Active Loans
                  </p>
                  <div className="w-10 h-10 rounded-xl bg-warning-100 flex items-center justify-center">
                    <svg className="w-5 h-5 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
                <p className="text-5xl font-bold text-slate-900 mb-2 count-up">
                  {activeLoans.length}
                </p>
                {totalOutstanding > 0 && (
                  <p className="text-sm text-slate-500">
                    UGX {totalOutstanding.toLocaleString()} outstanding
                  </p>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Loans Summary Section */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Loan Summary</h2>
            <p className="text-slate-500 mt-1">Track your active and pending loans</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card hover>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-success-100 flex items-center justify-center">
                    <svg className="w-6 h-6 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900">Active Loans</h3>
                </div>
                <span className="px-3 py-1.5 bg-success-100 text-success-700 rounded-full text-xs font-bold">
                  {activeLoans.length}
                </span>
              </div>
              {loansLoading ? (
                <Skeleton className="h-16" />
              ) : activeLoans.length > 0 ? (
                <div className="space-y-4">
                  <div className="p-4 bg-slate-50 rounded-xl">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-600">Total Outstanding</span>
                      <span className="text-2xl font-bold text-slate-900">
                        UGX {totalOutstanding.toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <Link href="/customer/loans">
                    <Button variant="primary" size="md" className="w-full">
                      View All Loans →
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-slate-500 text-sm">No active loans</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card hover>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-warning-100 flex items-center justify-center">
                    <svg className="w-6 h-6 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900">Pending Loans</h3>
                </div>
                <span className="px-3 py-1.5 bg-warning-100 text-warning-700 rounded-full text-xs font-bold">
                  {pendingLoans.length}
                </span>
              </div>
              {loansLoading ? (
                <Skeleton className="h-16" />
              ) : pendingLoans.length > 0 ? (
                <div className="space-y-4">
                  <div className="p-4 bg-slate-50 rounded-xl">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-600">Awaiting Approval</span>
                      <span className="text-2xl font-bold text-slate-900">
                        {pendingLoans.length} loan{pendingLoans.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                  <Link href="/customer/loans">
                    <Button variant="outline" size="md" className="w-full">
                      View Details →
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-slate-500 text-sm">No pending loans</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Quick Actions */}
      <Card className="gradient-card">
        <CardContent className="p-8">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Quick Actions</h2>
          <div className="flex flex-wrap gap-4">
            <Link href="/customer/marketplace">
              <Button variant="primary" size="lg" className="shadow-lg">
                🛍️ Browse Marketplace
              </Button>
            </Link>
            <Link href="/customer/loans">
              <Button variant="secondary" size="lg">
                📋 View All Loans
              </Button>
            </Link>
            <Link href="/customer/credit">
              <Button variant="outline" size="lg">
                💳 Check Credit Score
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
