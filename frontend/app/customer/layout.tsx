'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';

export default function CustomerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, role } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      const currentPath = typeof window !== 'undefined' ? window.location.pathname : '/customer/dashboard';
      router.push('/login?redirect=' + encodeURIComponent(currentPath));
      return;
    }

    if (role && role !== 'CUSTOMER') {
      // Redirect to appropriate dashboard
      if (role === 'RETAILER') {
        router.push('/retailer/dashboard');
      } else if (role === 'LENDER') {
        router.push('/lender/dashboard');
      } else {
        router.push('/login');
      }
    }
  }, [isAuthenticated, role, router]);

  if (!isAuthenticated || role !== 'CUSTOMER') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return <main className="min-h-screen bg-gray-50">{children}</main>;
}

