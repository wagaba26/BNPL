'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';

export default function LenderLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, role } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login?redirect=/lender/dashboard');
      return;
    }

    if (role && role !== 'LENDER') {
      // Redirect to appropriate dashboard
      if (role === 'CUSTOMER') {
        router.push('/customer/dashboard');
      } else if (role === 'RETAILER') {
        router.push('/retailer/dashboard');
      } else {
        router.push('/login');
      }
    }
  }, [isAuthenticated, role, router]);

  if (!isAuthenticated || role !== 'LENDER') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return <main className="min-h-screen bg-gray-50">{children}</main>;
}

