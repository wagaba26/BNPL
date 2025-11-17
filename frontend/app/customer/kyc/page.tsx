'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import Link from 'next/link';

export default function KYCPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    idNumber: '',
    dateOfBirth: '',
    address: '',
    city: '',
    country: '',
    postalCode: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Validate required fields
      if (!formData.idNumber || formData.idNumber.trim() === '') {
        setError('ID Number is required');
        setLoading(false);
        return;
      }

      if (!formData.dateOfBirth || formData.dateOfBirth.trim() === '') {
        setError('Date of Birth is required');
        setLoading(false);
        return;
      }

      if (!formData.address || formData.address.trim() === '') {
        setError('Address is required');
        setLoading(false);
        return;
      }

      if (!formData.city || formData.city.trim() === '') {
        setError('City is required');
        setLoading(false);
        return;
      }

      if (!formData.country || formData.country.trim() === '') {
        setError('Country is required');
        setLoading(false);
        return;
      }

      // Store KYC completion in localStorage
      localStorage.setItem('kyc_completed', 'true');
      localStorage.setItem('kyc_data', JSON.stringify({
        ...formData,
        completedAt: new Date().toISOString(),
      }));

      // Redirect to dashboard
      router.push('/customer/dashboard');
    } catch (err: any) {
      console.error('KYC submission error:', err);
      setError(err.message || 'Failed to complete KYC. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Check if KYC is already completed
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const kycCompleted = localStorage.getItem('kyc_completed');
      if (kycCompleted === 'true') {
        router.push('/customer/dashboard');
      }
    }
  }, [router]);

  // Redirect if not authenticated
  if (!isLoading && !user) {
    router.push('/login');
    return null;
  }

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/40 to-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/40 to-slate-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center">
          <Link href="/" className="inline-flex items-center space-x-3 mb-8 group">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-600 via-primary-500 to-accent-500 rounded-2xl flex items-center justify-center shadow-fintech-lg group-hover:shadow-fintech transition-all">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <span className="text-3xl font-bold gradient-text">Shift</span>
          </Link>
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-3">
            Complete Your KYC
          </h2>
          <p className="text-slate-600 text-lg">
            Please provide your information to complete your account setup
          </p>
        </div>

        <Card className="shadow-fintech-lg border-slate-200/60 backdrop-blur-sm">
          <CardHeader>
            <h3 className="text-xl font-bold text-slate-900">Know Your Customer (KYC) Information</h3>
            <p className="text-sm text-slate-600 mt-2">
              This information is required to verify your identity and enable full access to our services.
            </p>
          </CardHeader>
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
                <div>
                  <label htmlFor="idNumber" className="block text-sm font-semibold text-slate-700 mb-2">
                    ID Number / National ID <span className="text-red-500">*</span>
                  </label>
                  <Input
                    id="idNumber"
                    name="idNumber"
                    type="text"
                    required
                    placeholder="Enter your ID number"
                    value={formData.idNumber}
                    onChange={handleChange}
                    className="w-full"
                  />
                </div>

                <div>
                  <label htmlFor="dateOfBirth" className="block text-sm font-semibold text-slate-700 mb-2">
                    Date of Birth <span className="text-red-500">*</span>
                  </label>
                  <Input
                    id="dateOfBirth"
                    name="dateOfBirth"
                    type="date"
                    required
                    value={formData.dateOfBirth}
                    onChange={handleChange}
                    className="w-full"
                  />
                </div>

                <div>
                  <label htmlFor="address" className="block text-sm font-semibold text-slate-700 mb-2">
                    Street Address <span className="text-red-500">*</span>
                  </label>
                  <Input
                    id="address"
                    name="address"
                    type="text"
                    required
                    placeholder="Enter your street address"
                    value={formData.address}
                    onChange={handleChange}
                    className="w-full"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="city" className="block text-sm font-semibold text-slate-700 mb-2">
                      City <span className="text-red-500">*</span>
                    </label>
                    <Input
                      id="city"
                      name="city"
                      type="text"
                      required
                      placeholder="Enter your city"
                      value={formData.city}
                      onChange={handleChange}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label htmlFor="postalCode" className="block text-sm font-semibold text-slate-700 mb-2">
                      Postal Code
                    </label>
                    <Input
                      id="postalCode"
                      name="postalCode"
                      type="text"
                      placeholder="Enter postal code (optional)"
                      value={formData.postalCode}
                      onChange={handleChange}
                      className="w-full"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="country" className="block text-sm font-semibold text-slate-700 mb-2">
                    Country <span className="text-red-500">*</span>
                  </label>
                  <Input
                    id="country"
                    name="country"
                    type="text"
                    required
                    placeholder="Enter your country"
                    value={formData.country}
                    onChange={handleChange}
                    className="w-full"
                  />
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-start">
                  <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="text-sm text-blue-800">
                    <p className="font-semibold mb-1">Why we need this information:</p>
                    <p className="text-blue-700">
                      KYC verification helps us comply with financial regulations and protect your account. 
                      Your information is securely stored and will only be used for verification purposes.
                    </p>
                  </div>
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                isLoading={loading}
                className="w-full"
                size="lg"
              >
                {loading ? 'Completing KYC...' : 'Complete KYC & Continue'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

