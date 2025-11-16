'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';

export default function RetailerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, role } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      const currentPath = typeof window !== 'undefined' ? window.location.pathname : '/retailer/dashboard';
      router.push('/login?redirect=' + encodeURIComponent(currentPath));
      return;
    }

    if (role && role !== 'RETAILER') {
      // Redirect to appropriate dashboard
      if (role === 'CUSTOMER') {
        router.push('/customer/dashboard');
      } else if (role === 'LENDER') {
        router.push('/lender/dashboard');
      } else {
        router.push('/login');
      }
    }
  }, [isAuthenticated, role, router]);

  if (!isAuthenticated || role !== 'RETAILER') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return <main className="min-h-screen bg-gray-50">{children}</main>;
}

