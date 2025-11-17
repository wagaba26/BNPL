'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useState, useEffect, useRef } from 'react';

export function GlobalHeader() {
  const { logout, user, isAuthenticated } = useAuth();
  const router = useRouter();
  const [showMenu, setShowMenu] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false);
      }
    };

    if (showMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showMenu]);

  const handleLogout = () => {
    logout();
    router.push('/');
    setShowMenu(false);
  };

  const getDashboardLink = () => {
    if (!user) return '/login';
    switch (user.role) {
      case 'CUSTOMER':
        return '/customer/dashboard';
      case 'RETAILER':
        return '/retailer/dashboard';
      case 'LENDER':
        return '/lender/dashboard';
      default:
        return '/login';
    }
  };

  return (
    <header className="bg-white/90 backdrop-blur-xl shadow-fintech border-b border-slate-200/60 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-600 via-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-fintech group-hover:shadow-fintech-lg transition-all">
                <span className="text-white font-bold text-lg">S</span>
              </div>
              <span className="text-xl font-bold gradient-text">Shift</span>
            </Link>
            <nav className="hidden md:flex md:ml-10 md:space-x-1">
              <Link
                href="/"
                className="text-slate-600 hover:text-slate-900 hover:bg-slate-100 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
              >
                Marketplace
              </Link>
              {isAuthenticated && user?.role === 'CUSTOMER' && (
                <>
                  <Link
                    href="/customer/loans"
                    className="text-slate-600 hover:text-slate-900 hover:bg-slate-100 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
                  >
                    My Loans
                  </Link>
                  <Link
                    href="/customer/profile"
                    className="text-slate-600 hover:text-slate-900 hover:bg-slate-100 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
                  >
                    Profile
                  </Link>
                </>
              )}
            </nav>
          </div>

          <div className="flex items-center space-x-3">
            {isAuthenticated ? (
              <div className="relative" ref={menuRef}>
                <button
                  onClick={() => setShowMenu(!showMenu)}
                  className="flex items-center space-x-2 px-3 py-2 rounded-xl hover:bg-slate-100 transition-colors focus:outline-none"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white text-sm font-semibold shadow-fintech">
                    {(user?.name || user?.email || 'U')[0].toUpperCase()}
                  </div>
                  <span className="hidden sm:inline text-sm font-medium text-slate-700">
                    {user?.name || user?.email}
                  </span>
                  <svg
                    className="w-4 h-4 text-slate-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>

                {showMenu && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-fintech-lg py-2 z-50 border border-slate-200/60 animate-slide-down backdrop-blur-xl">
                    <Link
                      href={getDashboardLink()}
                      onClick={() => setShowMenu(false)}
                      className="block px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                    >
                      <div className="font-semibold">Dashboard</div>
                      <div className="text-xs text-slate-500 mt-0.5">Go to your dashboard</div>
                    </Link>
                    <div className="border-t border-slate-100 my-1"></div>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2.5 text-sm text-danger-600 hover:bg-danger-50 transition-colors font-medium"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  href="/login"
                  className="text-slate-700 hover:text-slate-900 px-4 py-2 text-sm font-medium rounded-xl hover:bg-slate-100 transition-colors"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="bg-gradient-to-r from-primary-600 to-primary-500 text-white px-5 py-2 rounded-xl text-sm font-semibold hover:from-primary-700 hover:to-primary-600 transition-all shadow-fintech hover:shadow-fintech-lg"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

