"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/contexts/AuthContext";

export default function LoginPage() {
  const [emailOrUsername, setEmailOrUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login, user } = useAuth();
  const router = useRouter();

  const getDashboardPath = (role: string) => {
    // Handle both uppercase and lowercase role values
    const normalizedRole = role?.toUpperCase();
    switch (normalizedRole) {
      case "CUSTOMER":
        return "/customer/dashboard";
      case "RETAILER":
        return "/retailer/dashboard";
      case "LENDER":
        return "/lender/dashboard";
      default:
        return "/";
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const success = await login(emailOrUsername, password);
      if (success) {
        // Wait a moment for auth state to update
        await new Promise((resolve) => setTimeout(resolve, 300));
        
        // Get the user from context (it should be set by now)
        // If user is available, redirect to their dashboard
        // Otherwise, wait a bit more and check again
        let currentUser = user;
        if (!currentUser) {
          await new Promise((resolve) => setTimeout(resolve, 200));
          // Try to get user from localStorage as fallback
          const storedUserStr = localStorage.getItem("bnpl_user");
          if (storedUserStr) {
            currentUser = JSON.parse(storedUserStr);
          }
        }
        
        if (currentUser && currentUser.role) {
          const dashboardPath = getDashboardPath(currentUser.role);
          router.push(dashboardPath);
          router.refresh();
        } else {
          // Fallback: redirect to home page
          router.push("/");
          router.refresh();
        }
      }
    } catch (err: any) {
      console.error("Login error in page:", err);
      const errorMessage = err?.response?.data?.detail || err?.message || "Invalid email/username or password. Please check your credentials and try again.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to Shift
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{" "}
            <Link
              href="/register"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              create a new account
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="emailOrUsername" className="sr-only">
                Email address or username
              </label>
              <input
                id="emailOrUsername"
                name="emailOrUsername"
                type="text"
                autoComplete="username"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Email address or username"
                value={emailOrUsername}
                onChange={(e) => setEmailOrUsername(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Signing in..." : "Sign in"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
