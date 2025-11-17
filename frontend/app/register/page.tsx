'use client';

import { useState, Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';
import { authApi } from '@/lib/api/auth';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

type UserRole = 'CUSTOMER' | 'RETAILER' | 'LENDER';

function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const login = useAuthStore((state) => state.login);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('CUSTOMER');
  const [adminCode, setAdminCode] = useState('');
  const [tradingLicense, setTradingLicense] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Additional KYC fields based on role
  // Customer-specific fields
  const [nationalId, setNationalId] = useState('');
  
  // Retailer-specific fields
  const [businessRegistrationNumber, setBusinessRegistrationNumber] = useState('');
  const [storeCity, setStoreCity] = useState('');
  const [storeCountry, setStoreCountry] = useState('');
  
  // Lender-specific fields
  const [licenseNumber, setLicenseNumber] = useState('');
  const [contactPersonName, setContactPersonName] = useState('');
  const [contactPhone, setContactPhone] = useState('');

  // Debug: Log role changes
  useEffect(() => {
    console.log('Role changed to:', role);
  }, [role]);

  const getRedirectPath = (userRole: UserRole | string) => {
    const normalizedRole = typeof userRole === 'string' ? userRole.toUpperCase() : userRole;
    switch (normalizedRole) {
      case 'CUSTOMER':
        return '/customer/dashboard'; // Changed from /customer/kyc - allow direct dashboard access
      case 'RETAILER':
        return '/retailer/dashboard';
      case 'LENDER':
        return '/lender/dashboard';
      default:
        return '/customer/dashboard';
    }
  };

  const redirectPath = searchParams?.get('redirect') || getRedirectPath(role);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email || email.trim() === '') {
        setError('Email is required for registration');
        setLoading(false);
        return;
      }
      if (!emailRegex.test(email)) {
        setError('Please enter a valid email address');
        setLoading(false);
        return;
      }

      if (!name || name.trim() === '') {
        setError('Name is required');
        setLoading(false);
        return;
      }

      if (!password || password.length < 6) {
        setError('Password must be at least 6 characters');
        setLoading(false);
        return;
      }

      // Validate phone format (basic check - at least 10 digits)
      if (phone && phone.trim() !== '') {
        const phoneDigits = phone.replace(/\D/g, '');
        if (phoneDigits.length < 10) {
          setError('Phone number must be at least 10 digits');
          setLoading(false);
          return;
        }
      }

      // Customer-specific validations
      if (role === 'CUSTOMER') {
        if (!nationalId || nationalId.trim() === '') {
          setError('National ID or Passport Number is required for customer registration');
          setLoading(false);
          return;
        }
      }

      // Retailer-specific validations
      if (role === 'RETAILER') {
        if (!tradingLicense || tradingLicense.trim() === '') {
          setError('Trading license is required for retailer registration. Please provide your valid trading license number for due diligence verification.');
          setLoading(false);
          return;
        }
        if (!storeCity || storeCity.trim() === '') {
          setError('Store location (city) is required');
          setLoading(false);
          return;
        }
        if (!storeCountry || storeCountry.trim() === '') {
          setError('Store location (country) is required');
          setLoading(false);
          return;
        }
      }

      // Lender-specific validations
      if (role === 'LENDER') {
        if (!adminCode || adminCode.trim() === '') {
          setError('Admin code is required for lender registration. Please contact support for due diligence verification.');
          setLoading(false);
          return;
        }
        if (!licenseNumber || licenseNumber.trim() === '') {
          setError('License/Registration Number is required for lender registration');
          setLoading(false);
          return;
        }
        if (!contactPersonName || contactPersonName.trim() === '') {
          setError('Contact Person Name is required for lender registration');
          setLoading(false);
          return;
        }
        if (!contactPhone || contactPhone.trim() === '') {
          setError('Contact Phone is required for lender registration');
          setLoading(false);
          return;
        }
        // Validate lender contact phone
        const contactPhoneDigits = contactPhone.replace(/\D/g, '');
        if (contactPhoneDigits.length < 10) {
          setError('Contact phone number must be at least 10 digits');
          setLoading(false);
          return;
        }
      }

      console.log('Registering with:', { name, email, role, hasAdminCode: !!adminCode });

      // ROLE PERSISTENCE: The selected role is included in the registration payload
      // This role will be stored in the backend and returned in the user object after registration
      // The role is then persisted in the auth store (Zustand) and localStorage for use in redirects
      const registerData = {
        name,
        email,
        password,
        role: role, // Role is explicitly included - this is stored in the user's account
        ...(phone ? { phone } : {}),
        // Customer-specific fields
        ...(role === 'CUSTOMER' && nationalId ? { national_id: nationalId } : {}),
        // Retailer-specific fields
        ...(role === 'RETAILER' && tradingLicense ? { trading_license: tradingLicense } : {}),
        ...(role === 'RETAILER' && businessRegistrationNumber ? { business_registration_number: businessRegistrationNumber } : {}),
        ...(role === 'RETAILER' && storeCity ? { store_city: storeCity } : {}),
        ...(role === 'RETAILER' && storeCountry ? { store_country: storeCountry } : {}),
        // Lender-specific fields
        ...(role === 'LENDER' && adminCode ? { admin_code: adminCode } : {}),
        ...(role === 'LENDER' && licenseNumber ? { license_number: licenseNumber } : {}),
        ...(role === 'LENDER' && contactPersonName ? { contact_person_name: contactPersonName } : {}),
        ...(role === 'LENDER' && contactPhone ? { contact_phone: contactPhone } : {}),
      };
      
      console.log('Registration data being sent:', registerData);

      console.log('Sending registration request...');
      const response = await authApi.register(registerData);
      console.log('Registration successful:', response);
      console.log('User role from response:', response.user.role);

      // ROLE PERSISTENCE IN AUTH: Store the user (with role) in the auth store
      // The role is now part of the user object and will be used for all subsequent role-based operations
      login(response.access_token, response.user);

      // ROLE-BASED REDIRECT: After successful registration, redirect user to their role-specific dashboard
      // The role comes from the response.user.role which was set during registration
      const userRole = (response.user.role as string).toUpperCase() as UserRole;
      console.log('Normalized role for redirect:', userRole);
      
      // Determine redirect path based on role
      let finalRedirectPath = '/customer/dashboard'; // Default
      if (userRole === 'CUSTOMER') {
        finalRedirectPath = '/customer/dashboard';
      } else if (userRole === 'RETAILER') {
        finalRedirectPath = '/retailer/dashboard';
      } else if (userRole === 'LENDER') {
        finalRedirectPath = '/lender/dashboard';
      }
      
      console.log('Redirecting to:', finalRedirectPath);
      router.push(finalRedirectPath);
    } catch (err: any) {
      console.error('Registration error:', err);
      console.error('Error details:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message,
        url: err.config?.url,
        baseURL: err.config?.baseURL,
      });
      
      // Better error messages
      let errorMessage = 'Registration failed. Please try again.';
      
      if (!err.response) {
        // Network error - backend not reachable
        const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
        errorMessage = `Cannot connect to the backend server at ${apiUrl}. Please ensure:
          - The backend server is running
          - NEXT_PUBLIC_API_BASE_URL is set correctly in your .env.local file
          - You have an active internet connection`;
      } else if (err.response?.status === 400) {
        errorMessage = err.response?.data?.detail || 'Invalid registration data. Please check your information and try again.';
      } else if (err.response?.status === 403) {
        errorMessage = err.response?.data?.detail || 'Registration not authorized. Please check your credentials.';
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error occurred. Please try again later or contact support.';
      } else {
        errorMessage = err.response?.data?.detail || err.message || 'Registration failed. Please try again.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
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
            Create your account
          </h2>
          <p className="text-slate-600 text-lg">
            Register to join the Shift platform
          </p>
        </div>

        {/* Getting Started Information */}
        <div className="mb-6 space-y-4">
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Getting Started</h3>
            <div className="space-y-4">
              {role === 'CUSTOMER' && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-slate-800">For Customers:</h4>
                  <ul className="text-sm text-slate-600 space-y-1 list-disc list-inside">
                    <li>Create an account with your email and personal information</li>
                    <li>Complete your profile to get started with BNPL services</li>
                    <li>Browse products and shop with flexible payment options</li>
                    <li>Build your credit profile as you make purchases</li>
                  </ul>
                </div>
              )}
              {role === 'RETAILER' && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-slate-800">For Retailers:</h4>
                  <ul className="text-sm text-slate-600 space-y-1 list-disc list-inside">
                    <li>You must provide a valid trading license number for registration</li>
                    <li>This is part of our due diligence process to verify your business</li>
                    <li>Once registered, you can list products and offer BNPL to customers</li>
                    <li>Manage your products, orders, and payouts from your dashboard</li>
                  </ul>
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-xs text-blue-800">
                      <strong>Note:</strong> Trading license verification is required. Please ensure you have your valid trading license number ready before registering.
                    </p>
                  </div>
                </div>
              )}
              {role === 'LENDER' && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-slate-800">For Lenders:</h4>
                  <ul className="text-sm text-slate-600 space-y-1 list-disc list-inside">
                    <li>Lender registration requires an admin code for due diligence verification</li>
                    <li>Contact support to obtain the admin code before registering</li>
                    <li>We perform thorough due diligence on all lending institutions</li>
                    <li>Once approved, you can manage loans and set interest rates</li>
                  </ul>
                  <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <p className="text-xs text-amber-800">
                      <strong>Important:</strong> Lender registration requires pre-approval. Please contact our support team to obtain the admin code and complete the due diligence process.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
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
                {/* Role Selection */}
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    I want to register as <span className="text-primary-600">({role})</span>
                  </label>
                  <div className="grid grid-cols-3 gap-2" role="group" aria-label="Select registration role">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('Setting role to CUSTOMER');
                        // ROLE SELECTION: Clear all role-specific fields when switching roles
                        setRole('CUSTOMER');
                        setAdminCode('');
                        setTradingLicense('');
                        setNationalId('');
                        setBusinessRegistrationNumber('');
                        setStoreCity('');
                        setStoreCountry('');
                        setLicenseNumber('');
                        setContactPersonName('');
                        setContactPhone('');
                      }}
                      aria-pressed={role === 'CUSTOMER'}
                      className={`px-4 py-3 rounded-xl text-sm font-medium transition-all cursor-pointer border-2 relative z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                        role === 'CUSTOMER'
                          ? 'bg-primary-600 text-white shadow-lg border-primary-600'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200'
                      }`}
                    >
                      Customer
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('Setting role to RETAILER');
                        // ROLE SELECTION: Clear all role-specific fields when switching roles
                        setRole('RETAILER');
                        setAdminCode('');
                        setTradingLicense('');
                        setNationalId('');
                        setBusinessRegistrationNumber('');
                        setStoreCity('');
                        setStoreCountry('');
                        setLicenseNumber('');
                        setContactPersonName('');
                        setContactPhone('');
                      }}
                      aria-pressed={role === 'RETAILER'}
                      className={`px-4 py-3 rounded-xl text-sm font-medium transition-all cursor-pointer border-2 relative z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                        role === 'RETAILER'
                          ? 'bg-primary-600 text-white shadow-lg border-primary-600'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200'
                      }`}
                    >
                      Retailer
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('Setting role to LENDER');
                        // ROLE SELECTION: Clear all role-specific fields when switching roles
                        setRole('LENDER');
                        setAdminCode('');
                        setTradingLicense('');
                        setNationalId('');
                        setBusinessRegistrationNumber('');
                        setStoreCity('');
                        setStoreCountry('');
                        setLicenseNumber('');
                        setContactPersonName('');
                        setContactPhone('');
                      }}
                      aria-pressed={role === 'LENDER'}
                      className={`px-4 py-3 rounded-xl text-sm font-medium transition-all cursor-pointer border-2 relative z-10 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                        role === 'LENDER'
                          ? 'bg-primary-600 text-white shadow-lg border-primary-600'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border-slate-200'
                      }`}
                    >
                      Lender
                    </button>
                  </div>
                  {role === 'LENDER' && (
                    <p className="mt-2 text-xs text-slate-500">
                      Lender registration requires admin approval and due diligence verification.
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="name" className="block text-sm font-semibold text-slate-700 mb-2">
                    {role === 'RETAILER' ? 'Business Name' : role === 'LENDER' ? 'Institution Name' : 'Full Name'}
                  </label>
                  <Input
                    id="name"
                    name="name"
                    type="text"
                    required
                    placeholder={role === 'RETAILER' ? 'Enter business name' : role === 'LENDER' ? 'Enter institution name' : 'Enter your full name'}
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full"
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-semibold text-slate-700 mb-2">
                    Email Address <span className="text-red-500">*</span>
                  </label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full"
                  />
                </div>

                <div>
                  <label htmlFor="phone" className="block text-sm font-semibold text-slate-700 mb-2">
                    Phone Number <span className="text-gray-400 text-xs">(Optional)</span>
                  </label>
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    autoComplete="tel"
                    placeholder="Enter your phone number (optional)"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
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
                    autoComplete="new-password"
                    required
                    placeholder="Create a password (min. 6 characters)"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full"
                    minLength={6}
                  />
                </div>

                {/* Customer-specific KYC fields */}
                {role === 'CUSTOMER' && (
                  <div>
                    <label htmlFor="nationalId" className="block text-sm font-semibold text-slate-700 mb-2">
                      National ID / Passport Number <span className="text-red-500">*</span>
                    </label>
                    <Input
                      id="nationalId"
                      name="nationalId"
                      type="text"
                      required
                      placeholder="Enter your National ID or Passport Number"
                      value={nationalId}
                      onChange={(e) => setNationalId(e.target.value)}
                      className="w-full"
                    />
                    <p className="mt-1 text-xs text-slate-500">
                      Required for identity verification and KYC compliance.
                    </p>
                  </div>
                )}

                {/* Retailer-specific KYC fields */}
                {role === 'RETAILER' && (
                  <>
                    <div>
                      <label htmlFor="tradingLicense" className="block text-sm font-semibold text-slate-700 mb-2">
                        Trading License Number <span className="text-red-500">*</span>
                      </label>
                      <Input
                        id="tradingLicense"
                        name="tradingLicense"
                        type="text"
                        required
                        placeholder="Enter your trading license number"
                        value={tradingLicense}
                        onChange={(e) => setTradingLicense(e.target.value)}
                        className="w-full"
                      />
                      <p className="mt-1 text-xs text-slate-500">
                        A valid trading license is required for retailer registration. This is part of our due diligence process to verify your business.
                      </p>
                    </div>

                    <div>
                      <label htmlFor="businessRegistrationNumber" className="block text-sm font-semibold text-slate-700 mb-2">
                        Business Registration Number <span className="text-gray-400 text-xs">(Optional)</span>
                      </label>
                      <Input
                        id="businessRegistrationNumber"
                        name="businessRegistrationNumber"
                        type="text"
                        placeholder="Enter your business registration number (optional)"
                        value={businessRegistrationNumber}
                        onChange={(e) => setBusinessRegistrationNumber(e.target.value)}
                        className="w-full"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="storeCity" className="block text-sm font-semibold text-slate-700 mb-2">
                          Store City <span className="text-red-500">*</span>
                        </label>
                        <Input
                          id="storeCity"
                          name="storeCity"
                          type="text"
                          required
                          placeholder="Enter city"
                          value={storeCity}
                          onChange={(e) => setStoreCity(e.target.value)}
                          className="w-full"
                        />
                      </div>
                      <div>
                        <label htmlFor="storeCountry" className="block text-sm font-semibold text-slate-700 mb-2">
                          Store Country <span className="text-red-500">*</span>
                        </label>
                        <Input
                          id="storeCountry"
                          name="storeCountry"
                          type="text"
                          required
                          placeholder="Enter country"
                          value={storeCountry}
                          onChange={(e) => setStoreCountry(e.target.value)}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </>
                )}

                {/* Lender-specific KYC fields */}
                {role === 'LENDER' && (
                  <>
                    <div>
                      <label htmlFor="adminCode" className="block text-sm font-semibold text-slate-700 mb-2">
                        Admin Code <span className="text-red-500">*</span>
                      </label>
                      <Input
                        id="adminCode"
                        name="adminCode"
                        type="text"
                        required
                        placeholder="Enter admin code for lender registration"
                        value={adminCode}
                        onChange={(e) => setAdminCode(e.target.value)}
                        className="w-full"
                      />
                      <p className="mt-1 text-xs text-slate-500">
                        Contact support to obtain the admin code for lender registration and due diligence verification.
                      </p>
                    </div>

                    <div>
                      <label htmlFor="licenseNumber" className="block text-sm font-semibold text-slate-700 mb-2">
                        License/Registration Number <span className="text-red-500">*</span>
                      </label>
                      <Input
                        id="licenseNumber"
                        name="licenseNumber"
                        type="text"
                        required
                        placeholder="Enter your license or registration number"
                        value={licenseNumber}
                        onChange={(e) => setLicenseNumber(e.target.value)}
                        className="w-full"
                      />
                    </div>

                    <div>
                      <label htmlFor="contactPersonName" className="block text-sm font-semibold text-slate-700 mb-2">
                        Contact Person Name <span className="text-red-500">*</span>
                      </label>
                      <Input
                        id="contactPersonName"
                        name="contactPersonName"
                        type="text"
                        required
                        placeholder="Enter contact person's full name"
                        value={contactPersonName}
                        onChange={(e) => setContactPersonName(e.target.value)}
                        className="w-full"
                      />
                    </div>

                    <div>
                      <label htmlFor="contactPhone" className="block text-sm font-semibold text-slate-700 mb-2">
                        Contact Phone <span className="text-red-500">*</span>
                      </label>
                      <Input
                        id="contactPhone"
                        name="contactPhone"
                        type="tel"
                        required
                        placeholder="Enter contact phone number"
                        value={contactPhone}
                        onChange={(e) => setContactPhone(e.target.value)}
                        className="w-full"
                      />
                    </div>
                  </>
                )}
              </div>

              <Button
                type="submit"
                disabled={loading}
                isLoading={loading}
                className="w-full"
                size="lg"
              >
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </form>

            <div className="mt-8 text-center pt-6 border-t border-slate-200">
              <p className="text-sm text-slate-600">
                Already have an account?{' '}
                <Link
                  href="/login"
                  className="font-semibold text-primary-600 hover:text-primary-700 transition-colors"
                >
                  Sign in here →
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-primary-50/30 to-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Loading...</p>
        </div>
      </div>
    }>
      <RegisterForm />
    </Suspense>
  );
}
