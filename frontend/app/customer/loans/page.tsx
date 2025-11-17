'use client';

import { useLoans } from '@/lib/hooks/queries';
import { format } from 'date-fns';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import Link from 'next/link';

export default function LoansPage() {
  const { data: loans, isLoading, error } = useLoans();

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return <Badge variant="success">Active</Badge>;
      case 'PENDING':
        return <Badge variant="warning">Pending</Badge>;
      case 'PAID':
        return <Badge variant="info">Paid</Badge>;
      case 'DEFAULTED':
        return <Badge variant="danger">Defaulted</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto w-full">
        <PageHeader title="My Loans" description="View and manage your BNPL loans" />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-6 w-48 mb-4" />
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Skeleton className="h-16" />
                  <Skeleton className="h-16" />
                  <Skeleton className="h-16" />
                  <Skeleton className="h-16" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto w-full">
        <PageHeader title="My Loans" description="View and manage your BNPL loans" />
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
                  Failed to load loans
                </h3>
                <p className="mt-1 text-sm text-red-700">
                  Please try again later.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto w-full">
      <PageHeader
        title="My Loans"
        description="View and manage your BNPL loans"
      />

      {!loans || loans.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
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
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No loans yet
            </h3>
            <p className="text-gray-500 mb-6">
              You don&apos;t have any loans yet. Start shopping to get started!
            </p>
            <Link href="/customer/marketplace">
              <Button variant="primary">Browse Marketplace</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {loans.map((loan) => {
            const outstandingBalance = loan.total_amount - loan.deposit_amount;
            const nextInstallment = loan.installments?.find((i) => !i.paid);
            const paidCount = loan.installments?.filter((i) => i.paid).length || 0;
            const totalInstallments = loan.installments?.length || 0;

            return (
              <Card key={loan.id} hover>
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                    {/* Left Section */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-4">
                        <h3 className="text-lg font-bold text-gray-900">
                          Product #{loan.product_id}
                        </h3>
                        {getStatusBadge(loan.status)}
                      </div>

                      {/* Loan Details Grid */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                            Principal Amount
                          </p>
                          <p className="text-base font-bold text-gray-900">
                            UGX {loan.principal_amount.toLocaleString()}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                            Outstanding
                          </p>
                          <p className="text-base font-bold text-gray-900">
                            UGX {outstandingBalance.toLocaleString()}
                          </p>
                        </div>

                        {nextInstallment?.due_date && (
                          <div>
                            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                              Next Payment
                            </p>
                            <p className="text-base font-bold text-gray-900">
                              {format(new Date(nextInstallment.due_date), 'MMM dd, yyyy')}
                            </p>
                            {nextInstallment.amount && (
                              <p className="text-sm text-gray-600 mt-0.5">
                                UGX {nextInstallment.amount.toLocaleString()}
                              </p>
                            )}
                          </div>
                        )}

                        <div>
                          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                            Progress
                          </p>
                          <p className="text-base font-bold text-gray-900">
                            {paidCount} / {totalInstallments}
                          </p>
                          <div className="mt-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-indigo-600 rounded-full transition-all"
                              style={{
                                width: `${(paidCount / totalInstallments) * 100}%`,
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Right Section - Action Button */}
                    <div className="flex items-center">
                      <Button variant="ghost" size="sm">
                        View Details
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
