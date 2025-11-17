"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/contexts/AuthContext";

export default function RetailerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Only redirect on client-side after hydration
    if (typeof window === 'undefined') return;
    
    if (!isLoading) {
      if (!user) {
        router.replace("/login");
        return;
      }

      const normalizedRole = user.role?.toUpperCase();
      if (normalizedRole !== "RETAILER") {
        // Redirect to appropriate dashboard
        if (normalizedRole === "CUSTOMER") {
          router.replace("/customer/dashboard");
        } else if (normalizedRole === "LENDER") {
          router.replace("/lender/dashboard");
        } else {
          router.replace("/login");
        }
      }
    }
  }, [user, isLoading, router]);

  if (isLoading || !user || user.role?.toUpperCase() !== "RETAILER") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return <main className="min-h-screen bg-gray-50">{children}</main>;
}
