'use client';

import { useLoans } from '@/lib/hooks/queries';
import { format } from 'date-fns';

export default function LoansPage() {
  const { data: loans, isLoading, error } = useLoans();

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p className="text-gray-500">Loading loans...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Failed to load loans. Please try again later.
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'bg-green-100 text-green-800';
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800';
      case 'PAID':
        return 'bg-primary-100 text-primary-800';
      case 'DEFAULTED':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Loans</h1>
        <p className="mt-2 text-gray-600">
          View and manage your Shift loans
        </p>
      </div>

      {!loans || loans.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 text-lg mb-4">You don&apos;t have any loans yet.</p>
          <a
            href="/customer/marketplace"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Browse marketplace to get started
          </a>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {loans.map((loan) => (
              <li key={loan.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h3 className="text-lg font-medium text-gray-900">
                        {loan.product_name || 'Product'}
                      </h3>
                      <span
                        className={`ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          loan.status
                        )}`}
                      >
                        {loan.status}
                      </span>
                    </div>
                    <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Principal Amount</p>
                        <p className="font-semibold text-gray-900">
                          UGX {loan.principal_amount.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Outstanding Balance</p>
                        <p className="font-semibold text-gray-900">
                          UGX {loan.outstanding_balance.toLocaleString()}
                        </p>
                      </div>
                      {loan.next_payment_date && (
                        <div>
                          <p className="text-gray-500">Next Payment</p>
                          <p className="font-semibold text-gray-900">
                            {format(new Date(loan.next_payment_date), 'MMM dd, yyyy')}
                          </p>
                          {loan.next_payment_amount && (
                            <p className="text-sm text-gray-600">
                              UGX {loan.next_payment_amount.toLocaleString()}
                            </p>
                          )}
                        </div>
                      )}
                      <div>
                        <p className="text-gray-500">Progress</p>
                        <p className="font-semibold text-gray-900">
                          {loan.total_installments - loan.remaining_installments} / {loan.total_installments}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

