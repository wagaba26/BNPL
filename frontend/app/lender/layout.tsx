"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/contexts/AuthContext";

export default function LenderLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push("/login");
        return;
      }

      const normalizedRole = user.role?.toUpperCase();
      if (normalizedRole !== "LENDER") {
        // Redirect to appropriate dashboard
        if (normalizedRole === "CUSTOMER") {
          router.push("/customer/dashboard");
        } else if (normalizedRole === "RETAILER") {
          router.push("/retailer/dashboard");
        } else {
          router.push("/login");
        }
      }
    }
  }, [user, isLoading, router]);

  if (isLoading || !user || user.role?.toUpperCase() !== "LENDER") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return <main className="min-h-screen bg-gray-50">{children}</main>;
}
