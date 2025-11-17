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

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push("/login");
        return;
      }

      if (user.role !== "customer") {
        // Redirect to appropriate dashboard
        if (user.role === "retailer") {
          router.push("/retailer/dashboard");
        } else if (user.role === "lender") {
          router.push("/lender/dashboard");
        } else {
          router.push("/login");
        }
      }
    }
  }, [user, isLoading, router]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (isLoading || !user || user.role !== "customer") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Loading...</p>
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

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Mobile Top Navigation */}
      <div className="md:hidden bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="flex items-center justify-between px-4 py-3">
          <h2 className="text-lg font-semibold text-gray-900">BNPL Platform</h2>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
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
          <div className="border-t border-gray-200 bg-white">
            <nav className="px-2 py-2 space-y-1">
              {navItems.map((item) => {
                const isActive = pathname.startsWith(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`block px-3 py-2 rounded-md text-sm transition-colors ${
                      isActive
                        ? "bg-gray-900 text-white"
                        : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
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
      <aside className="hidden md:flex md:w-64 md:flex-col md:border-r md:bg-white md:h-screen md:sticky md:top-0">
        <CustomerSidebar />
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-h-screen">
        {/* Optional Header */}
        <div className="bg-white border-b border-gray-200 px-4 py-3 md:px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h1 className="text-lg font-semibold text-gray-900">
                {navItems.find((item) => pathname.startsWith(item.href))
                  ?.label || "Customer Portal"}
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600 hidden sm:inline">
                {user?.fullName || user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                  />
                </svg>
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="flex-1 p-4 md:p-6">{children}</div>
      </main>
    </div>
  );
}
