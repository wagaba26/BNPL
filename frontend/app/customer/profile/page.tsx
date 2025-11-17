'use client';

import { useAuth } from '@/lib/hooks/useAuth';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <div className="max-w-4xl mx-auto w-full">
      <PageHeader
        title="Profile"
        description="Manage your account information and documents"
      />

      {/* User Information Card */}
      <Card className="mb-6">
        <CardHeader>
          <h2 className="text-xl font-bold text-gray-900">Personal Information</h2>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Full Name
              </label>
              <div className="px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-900">
                {user?.name || 'N/A'}
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Email Address
              </label>
              <div className="px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-900">
                {user?.email || 'N/A'}
              </div>
            </div>
            {user?.phone && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Phone Number
                </label>
                <div className="px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-900">
                  {user.phone}
                </div>
              </div>
            )}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Account Role
              </label>
              <div className="px-4 py-2.5">
                <Badge variant="info">{user?.role || 'N/A'}</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account Settings Card */}
      <Card className="mb-6">
        <CardHeader>
          <h2 className="text-xl font-bold text-gray-900">Account Settings</h2>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Change Password</h3>
              <p className="text-sm text-gray-600 mt-0.5">
                Update your password to keep your account secure
              </p>
            </div>
            <Button variant="secondary" size="sm">
              Change Password
            </Button>
          </div>
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Notification Preferences</h3>
              <p className="text-sm text-gray-600 mt-0.5">
                Manage how you receive notifications
              </p>
            </div>
            <Button variant="secondary" size="sm">
              Manage
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Document Verification Card */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-bold text-gray-900">Document Verification</h2>
          <p className="text-sm text-gray-600 mt-2">
            Uploading more verified information may improve your credit score and unlock more
            products.
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-base font-semibold text-gray-900 mb-1">
                    Mobile Money Statement
                  </h3>
                  <p className="text-sm text-gray-600">
                    Upload your mobile money transaction history
                  </p>
                </div>
                <div className="ml-4">
                  <Button variant="primary" size="sm">
                    Upload
                  </Button>
                </div>
              </div>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-base font-semibold text-gray-900 mb-1">
                    Bank Statement
                  </h3>
                  <p className="text-sm text-gray-600">
                    Upload your bank statement (last 3 months)
                  </p>
                </div>
                <div className="ml-4">
                  <Button variant="primary" size="sm">
                    Upload
                  </Button>
                </div>
              </div>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-base font-semibold text-gray-900 mb-1">
                    Proof of Address
                  </h3>
                  <p className="text-sm text-gray-600">
                    Upload utility bill or rental agreement
                  </p>
                </div>
                <div className="ml-4">
                  <Button variant="primary" size="sm">
                    Upload
                  </Button>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 mb-4">
              For more document upload options, visit the{' '}
              <a
                href="/customer/documents"
                className="text-indigo-600 hover:text-indigo-700 font-medium"
              >
                Documents / KYC page
              </a>
              .
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
