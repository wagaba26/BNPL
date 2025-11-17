"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/contexts/AuthContext";
import { CustomerSidebar } from "@/components/customer/CustomerSidebar";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function CustomerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);

  useEffect(() => {
    // Only redirect on client-side after hydration
    // Don't redirect during SSR or while still loading
    if (typeof window === 'undefined') return;
    
    // Only redirect if we're done loading and there's no user
    if (!isLoading && !user) {
      router.replace("/login");
      return;
    }

    // Only check role if we have a user
    if (!isLoading && user) {
      const normalizedRole = user.role?.toUpperCase();
      if (normalizedRole !== "CUSTOMER") {
        // Redirect to appropriate dashboard
        if (normalizedRole === "RETAILER") {
          router.replace("/retailer/dashboard");
        } else if (normalizedRole === "LENDER") {
          router.replace("/lender/dashboard");
        } else {
          router.replace("/login");
        }
        return;
      }

      // Check KYC completion for customers (skip check if already on KYC page or dashboard)
      // Allow access to dashboard and KYC page without KYC completion
      if (normalizedRole === "CUSTOMER" && pathname !== "/customer/kyc" && pathname !== "/customer/dashboard") {
        const kycCompleted = localStorage.getItem("kyc_completed");
        if (kycCompleted !== "true") {
          // Only redirect to KYC if not on dashboard or KYC page
          router.replace("/customer/kyc");
          return;
        }
      }
    }
  }, [user, isLoading, router, pathname]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  // Show loading state during initial load or if user is not authenticated
  // This ensures consistent SSR/client rendering
  if (isLoading || !user || user.role?.toUpperCase() !== "CUSTOMER") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Loading...</p>
        </div>
      </div>
    );
  }

  const navItems = [
    { label: "Dashboard", href: "/customer/dashboard" },
    { label: "Marketplace", href: "/customer/marketplace" },
    { label: "My Loans", href: "/customer/loans" },
    { label: "Credit Score", href: "/customer/credit" },
    { label: "Documents / KYC", href: "/customer/documents" },
    { label: "Profile", href: "/customer/profile" },
  ];

  const currentPage = navItems.find((item) => pathname.startsWith(item.href));
  const isKYCPage = pathname === "/customer/kyc";

  // If on KYC page, render without sidebar/nav
  if (isKYCPage) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/20 to-slate-50 flex flex-col md:flex-row">
      {/* Mobile Top Navigation */}
      <div className="md:hidden bg-white/95 backdrop-blur-xl border-b border-slate-200/60 sticky top-0 z-50 shadow-fintech">
        <div className="flex items-center justify-between px-4 py-3">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Shift</h2>
            <p className="text-xs text-slate-500 font-medium">BNPL Platform</p>
          </div>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          >
            {mobileMenuOpen ? (
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            ) : (
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            )}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="border-t border-slate-200/60 bg-white/95 backdrop-blur-xl">
            <nav className="px-2 py-2 space-y-1.5">
              {navItems.map((item) => {
                const isActive = pathname.startsWith(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`block px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                      isActive
                        ? "bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-fintech"
                        : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        )}
      </div>

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex md:w-64 md:flex-col md:border-r md:bg-white md:h-screen md:sticky md:top-0 md:shadow-sm">
        <CustomerSidebar />
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/20 to-slate-50">
        {/* Top Navbar */}
        <div className="bg-white/90 backdrop-blur-xl border-b border-slate-200/60 px-4 py-4 md:px-6 shadow-fintech sticky top-0 z-40">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                {currentPage?.label || "Customer Portal"}
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <div className="relative">
                <button
                  onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-100 transition-colors"
                >
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white text-sm font-semibold shadow-fintech">
                    {(user?.name || user?.email || "U")[0].toUpperCase()}
                  </div>
                  <span className="hidden sm:inline text-slate-700 font-medium">
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
                {profileMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-fintech-lg border border-slate-200/60 py-2 z-50 animate-slide-down backdrop-blur-xl">
                    <Link
                      href="/customer/profile"
                      onClick={() => setProfileMenuOpen(false)}
                      className="block px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                    >
                      <div className="font-semibold">View Profile</div>
                      <div className="text-xs text-slate-500 mt-0.5">Manage your account</div>
                    </Link>
                    <div className="border-t border-slate-100 my-1"></div>
                    <button
                      onClick={() => {
                        setProfileMenuOpen(false);
                        handleLogout();
                      }}
                      className="block w-full text-left px-4 py-2.5 text-sm text-danger-600 hover:bg-danger-50 transition-colors font-medium"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="flex-1 p-4 md:p-6 lg:p-8">{children}</div>
      </main>

      {/* Click outside to close profile menu */}
      {profileMenuOpen && (
        <div
          className="fixed inset-0 z-30"
          onClick={() => setProfileMenuOpen(false)}
        />
      )}
    </div>
  );
}
