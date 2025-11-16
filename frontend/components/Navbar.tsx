'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/hooks/useAuth';
import { useRouter } from 'next/navigation';

interface NavbarProps {
  role: 'CUSTOMER' | 'RETAILER' | 'LENDER';
}

export function Navbar({ role }: NavbarProps) {
  const { logout, user } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const customerLinks = [
    { href: '/customer/dashboard', label: 'Dashboard' },
    { href: '/customer/marketplace', label: 'Marketplace' },
    { href: '/customer/loans', label: 'My Loans' },
    { href: '/customer/profile', label: 'Profile' },
  ];

  const retailerLinks = [
    { href: '/retailer/dashboard', label: 'Dashboard' },
    { href: '/retailer/products', label: 'Products' },
  ];

  const lenderLinks = [
    { href: '/lender/dashboard', label: 'Dashboard' },
    { href: '/lender/loans', label: 'Loans' },
  ];

  const links = role === 'CUSTOMER' ? customerLinks : role === 'RETAILER' ? retailerLinks : lenderLinks;

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href={`/${role.toLowerCase()}/dashboard`} className="text-xl font-bold text-primary-600 hover:text-primary-700 transition-colors">
                Shift
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center">
            <span className="text-gray-700 text-sm mr-4">{user?.name}</span>
            <button
              onClick={handleLogout}
              className="text-gray-500 hover:text-gray-700 text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

