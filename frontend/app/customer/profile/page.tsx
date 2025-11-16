'use client';

import { useAuth } from '@/lib/hooks/useAuth';
import { useState } from 'react';

export default function ProfilePage() {
  const { user } = useAuth();
  const [uploading, setUploading] = useState<string | null>(null);

  const handleFileUpload = async (type: string, file: File) => {
    setUploading(type);
    // Mock upload - in real app, this would call an API
    setTimeout(() => {
      setUploading(null);
      alert(`${type} uploaded successfully (mock)`);
    }, 1500);
  };

  const documentTypes = [
    {
      id: 'mobile-money',
      label: 'Mobile Money Statement',
      description: 'Upload your mobile money transaction history',
    },
    {
      id: 'bank-statement',
      label: 'Bank Statement',
      description: 'Upload your bank statement (last 3 months)',
    },
    {
      id: 'proof-of-address',
      label: 'Proof of Address',
      description: 'Upload utility bill or rental agreement',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
        <p className="mt-2 text-gray-600">
          Manage your account information and documents
        </p>
      </div>

      {/* User Information */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Personal Information
          </h2>
        </div>
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Full Name
            </label>
            <p className="text-gray-900">{user?.name}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <p className="text-gray-900">{user?.email || 'N/A'}</p>
          </div>
          {user?.phone && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone
              </label>
              <p className="text-gray-900">{user.phone}</p>
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Role
            </label>
            <p className="text-gray-900">{user?.role}</p>
          </div>
        </div>
      </div>

      {/* Document Upload Section */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Document Verification
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Uploading more verified information may improve your credit score
            and unlock more products.
          </p>
        </div>
        <div className="p-6 space-y-6">
          {documentTypes.map((doc) => (
            <div key={doc.id} className="border rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900 mb-1">
                    {doc.label}
                  </h3>
                  <p className="text-sm text-gray-600">{doc.description}</p>
                </div>
                <div className="ml-4">
                  <label className="cursor-pointer">
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          handleFileUpload(doc.id, file);
                        }
                      }}
                      disabled={uploading === doc.id}
                    />
                    <span
                      className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md ${
                        uploading === doc.id
                          ? 'bg-gray-400 text-white cursor-not-allowed'
                          : 'bg-primary-600 text-white hover:bg-primary-700 font-medium shadow-sm hover:shadow-md transition-colors'
                      }`}
                    >
                      {uploading === doc.id ? 'Uploading...' : 'Upload'}
                    </span>
                  </label>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

