'use client';

import { useParams, useRouter } from 'next/navigation';
import { useProducts, useCreateBNPL } from '@/lib/hooks/queries';
import { useState, useMemo } from 'react';
import { useAuth } from '@/lib/hooks/useAuth';
import Link from 'next/link';

export default function CheckoutPage() {
  const params = useParams();
  const router = useRouter();
  const productId = parseInt(params.productId as string);
  const { data: products, isLoading } = useProducts();
  const createBNPL = useCreateBNPL();
  const { isAuthenticated } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const product = useMemo(() => {
    return products?.find(p => p.id === productId);
  }, [products, productId]);

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p className="text-gray-500">Loading product details...</p>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Product not found
        </div>
      </div>
    );
  }

  // Calculate estimated deposit (20% of price)
  const estimatedDeposit = product.price * 0.20;
  const estimatedPrincipal = product.price - estimatedDeposit;
  // Estimate 3 installments (backend will create this)
  const estimatedInstallmentAmount = estimatedPrincipal / 3;

  const handleConfirm = async () => {
    if (!isAuthenticated) {
      router.push(`/register?redirect=/customer/checkout/${productId}`);
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await createBNPL.mutateAsync({ product_id: productId });
      router.push('/customer/loans');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create BNPL request. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Checkout</h1>
        <p className="mt-2 text-gray-600">Review your Shift order</p>
      </div>

      {!isAuthenticated && (
        <div className="mb-6 bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
          <p className="font-semibold mb-2">Registration Required</p>
          <p className="text-sm mb-3">
            You need to create an account to proceed with your purchase. It only takes a minute!
          </p>
          <div className="flex space-x-3">
            <Link
              href={`/register?redirect=/customer/checkout/${productId}`}
              className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors shadow-sm hover:shadow-md"
            >
              Create Account
            </Link>
            <Link
              href="/login"
              className="bg-gray-200 text-gray-800 px-4 py-2 rounded text-sm font-medium hover:bg-gray-300 transition"
            >
              Already have an account? Login
            </Link>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {product.name}
          </h2>
          {product.description && (
            <p className="text-gray-600 mb-4">{product.description}</p>
          )}
        </div>

        <div className="p-6 space-y-4">
          <div className="flex justify-between py-2">
            <span className="text-gray-600">Product Price</span>
            <span className="font-semibold text-gray-900">
              UGX {product.price.toLocaleString()}
            </span>
          </div>

          <div className="flex justify-between py-2 border-t">
            <span className="text-gray-600">Estimated Deposit (20%)</span>
            <span className="font-semibold text-primary-600">
              UGX {estimatedDeposit.toLocaleString()}
            </span>
          </div>

          <div className="flex justify-between py-2 border-t">
            <span className="text-gray-600">Amount to Finance</span>
            <span className="font-semibold text-gray-900">
              UGX {estimatedPrincipal.toLocaleString()}
            </span>
          </div>

          <div className="mt-6 pt-6 border-t">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Estimated Installment Breakdown
            </h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-2">
                3 installments of{' '}
                <span className="font-semibold text-gray-900">
                  UGX {estimatedInstallmentAmount.toLocaleString()}
                </span>{' '}
                per month
              </p>
              <p className="text-xs text-gray-500 mt-2">
                * Final amounts will be calculated when you confirm the BNPL request
              </p>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-gray-500">Total Amount</p>
                <p className="text-2xl font-bold text-gray-900">
                  UGX {product.price.toLocaleString()}
                </p>
              </div>
              <button
                onClick={handleConfirm}
                disabled={isSubmitting || !isAuthenticated}
                className="bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Processing...' : isAuthenticated ? 'Confirm BNPL' : 'Register to Continue'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <a
          href="/customer/marketplace"
          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          ← Back to Marketplace
        </a>
      </div>
    </div>
  );
}

