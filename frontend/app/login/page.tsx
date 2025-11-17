"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/contexts/AuthContext";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

// Role type definition - matches the backend enum
type UserRole = "CUSTOMER" | "RETAILER" | "LENDER";

export default function LoginPage() {
  const [emailOrUsername, setEmailOrUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  // Role selection state - for UI purposes and potential filtering
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null);
  const { login, user } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const success = await login(emailOrUsername, password);
      if (success) {
        // Wait a moment for user state to update and token to be stored
        await new Promise((resolve) => setTimeout(resolve, 500));
        
        // ROLE-BASED REDIRECT: After successful login, redirect user to their role-specific dashboard
        // The role is stored in the user object returned from the auth API and persisted in localStorage
        // This ensures users are automatically routed to the correct dashboard based on their account role
        let redirectPath = "/";
        if (typeof window !== 'undefined') {
          const storedUserStr = localStorage.getItem('bnpl_user');
          if (storedUserStr) {
            try {
              const storedUser = JSON.parse(storedUserStr);
              const role = storedUser.role?.toUpperCase();
              console.log("Redirecting based on role:", role);
              if (role === "CUSTOMER") {
                // Always redirect to dashboard - KYC check is handled in the layout
                redirectPath = "/customer/dashboard";
              } else if (role === "RETAILER") {
                redirectPath = "/retailer/dashboard";
              } else if (role === "LENDER") {
                redirectPath = "/lender/dashboard";
              }
            } catch (e) {
              console.error("Error parsing stored user:", e);
            }
          } else {
            // If no user in localStorage, check context
            if (user) {
              const role = user.role?.toUpperCase();
              if (role === "CUSTOMER") {
                // Always redirect to dashboard - KYC check is handled in the layout
                redirectPath = "/customer/dashboard";
              } else if (role === "RETAILER") {
                redirectPath = "/retailer/dashboard";
              } else if (role === "LENDER") {
                redirectPath = "/lender/dashboard";
              }
            }
          }
        }
        
        console.log("Redirecting to:", redirectPath);
        router.push(redirectPath);
        // Don't call refresh immediately - let the navigation happen first
      } else {
        setError("Login failed. Please try again.");
      }
    } catch (err: any) {
      console.error("Login error in page:", err);
      console.error("Error details:", {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message,
        url: err.config?.url,
        baseURL: err.config?.baseURL,
      });
      
      // Better error messages
      let errorMessage = "Login failed. Please try again.";
      
      if (!err.response) {
        // Network error - backend not reachable
        const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || (process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : 'configured API URL');
        errorMessage = `Cannot connect to the backend server${apiUrl ? ` at ${apiUrl}` : ''}. Please ensure:
          - The backend server is running
          - NEXT_PUBLIC_API_BASE_URL is set correctly${process.env.NODE_ENV === 'development' ? ' in your .env.local file' : ' in your deployment environment variables'}
          - You have an active internet connection`;
      } else if (err.response?.status === 401) {
        errorMessage = err.response?.data?.detail || "Invalid email/username or password. Please check your credentials and try again.";
      } else if (err.response?.status === 400) {
        errorMessage = err.response?.data?.detail || "Invalid request. Please check your input and try again.";
      } else if (err.response?.status === 500) {
        errorMessage = "Server error occurred. Please try again later or contact support.";
      } else {
        errorMessage = err.response?.data?.detail || err.message || "Login failed. Please try again.";
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/40 to-slate-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-primary-200/20 rounded-full -mr-48 -mt-48 blur-3xl"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-accent-200/20 rounded-full -ml-48 -mb-48 blur-3xl"></div>
      
      <div className="max-w-md w-full space-y-8 animate-fade-in relative z-10">
        <div className="text-center">
          <Link href="/" className="inline-flex items-center space-x-3 mb-8 group">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-600 via-primary-500 to-accent-500 rounded-2xl flex items-center justify-center shadow-fintech-lg group-hover:shadow-fintech transition-all">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <span className="text-3xl font-bold gradient-text">Shift</span>
          </Link>
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-3">
            Welcome back
          </h2>
          <p className="text-slate-600 text-lg">
            Sign in to your account to continue
          </p>
        </div>

        <Card className="shadow-fintech-lg border-slate-200/60 backdrop-blur-sm">
          <CardContent className="p-8 md:p-10">
            <form className="space-y-6" onSubmit={handleSubmit}>
              {error && (
                <div className="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3.5 rounded-xl flex items-start space-x-3 shadow-sm">
                  <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm font-medium">{error}</span>
                </div>
              )}

              <div className="space-y-4">
                {/* Role Selection - helps users identify which account type they're logging into */}
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    I am logging in as <span className="text-primary-600">({selectedRole || "Select role"})</span>
                  </label>
                  <div className="grid grid-cols-3 gap-2" role="group" aria-label="Select login role">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setSelectedRole("CUSTOMER");
                      }}
                      aria-pressed={selectedRole === "CUSTOMER"}
                      className={`px-4 py-3 rounded-xl text-sm font-medium transition-all cursor-pointer border-2 relative z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                        selectedRole === "CUSTOMER"
                          ? "bg-primary-600 text-white shadow-lg border-primary-600"
                          : "bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200"
                      }`}
                    >
                      Customer
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setSelectedRole("RETAILER");
                      }}
                      aria-pressed={selectedRole === "RETAILER"}
                      className={`px-4 py-3 rounded-xl text-sm font-medium transition-all cursor-pointer border-2 relative z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                        selectedRole === "RETAILER"
                          ? "bg-primary-600 text-white shadow-lg border-primary-600"
                          : "bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200"
                      }`}
                    >
                      Retailer
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setSelectedRole("LENDER");
                      }}
                      aria-pressed={selectedRole === "LENDER"}
                      className={`px-4 py-3 rounded-xl text-sm font-medium transition-all cursor-pointer border-2 relative z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                        selectedRole === "LENDER"
                          ? "bg-primary-600 text-white shadow-lg border-primary-600"
                          : "bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200"
                      }`}
                    >
                      Lender
                    </button>
                  </div>
                  <p className="mt-2 text-xs text-slate-500">
                    Select your account type to continue. Your role is determined by your account.
                  </p>
                </div>

                <div>
                  <label htmlFor="emailOrUsername" className="block text-sm font-semibold text-slate-700 mb-2">
                    Email or Username
                  </label>
                  <Input
                    id="emailOrUsername"
                    name="emailOrUsername"
                    type="text"
                    autoComplete="username"
                    required
                    placeholder="Enter your email or username"
                    value={emailOrUsername}
                    onChange={(e) => setEmailOrUsername(e.target.value)}
                    className="w-full"
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-semibold text-slate-700 mb-2">
                    Password
                  </label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full"
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                isLoading={isLoading}
                className="w-full"
                size="lg"
              >
                {isLoading ? "Signing in..." : "Sign in"}
              </Button>
            </form>

            <div className="mt-8 text-center pt-6 border-t border-slate-200">
              <p className="text-sm text-slate-600">
                Don&apos;t have an account?{" "}
                <Link
                  href="/register"
                  className="font-semibold text-primary-600 hover:text-primary-700 transition-colors"
                >
                  Create one now →
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
