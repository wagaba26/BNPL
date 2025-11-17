'use client';

import { useState, useRef, useEffect } from 'react';
import { useCreditDocuments, useUploadCreditDocument } from '@/lib/hooks/useCredit';
import { CREDIT_DOCUMENT_TYPES } from '@/lib/creditConstants';
import { formatDate, formatRelativeTime } from '@/lib/utils/creditHelpers';
import type { CreditDocument } from '@/types/credit';

function DocumentStatusBadge({ status }: { status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'NOT_UPLOADED' }) {
  const statusConfig = {
    APPROVED: {
      label: 'Approved',
      className: 'bg-green-100 text-green-800',
    },
    PENDING: {
      label: 'Pending review',
      className: 'bg-yellow-100 text-yellow-800',
    },
    REJECTED: {
      label: 'Rejected',
      className: 'bg-red-100 text-red-800',
    },
    NOT_UPLOADED: {
      label: 'Not uploaded',
      className: 'bg-gray-100 text-gray-800',
    },
  };

  const config = statusConfig[status] || statusConfig.NOT_UPLOADED;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className}`}
    >
      {config.label}
    </span>
  );
}

function DocumentRow({
  documentType,
  existingDocument,
  onUpload,
  isUploading,
}: {
  documentType: { id: string; label: string; description?: string };
  existingDocument?: CreditDocument;
  onUpload: (file: File) => void;
  isUploading: boolean;
}) {
  const [showUploadInput, setShowUploadInput] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'NOT_UPLOADED' =
    existingDocument?.status || 'NOT_UPLOADED';

  const canUpload = status === 'NOT_UPLOADED' || status === 'REJECTED';
  const showUploadAgain = status === 'PENDING' || status === 'APPROVED';

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUploadClick = () => {
    if (selectedFile) {
      onUpload(selectedFile);
      setSelectedFile(null);
      setShowUploadInput(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleCancel = () => {
    setSelectedFile(null);
    setShowUploadInput(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {documentType.label}
            </h3>
            <DocumentStatusBadge status={status} />
          </div>
          {documentType.description && (
            <p className="text-sm text-gray-600 mb-2">{documentType.description}</p>
          )}

          {existingDocument && (
            <div className="mt-2 space-y-1">
              <p className="text-xs text-gray-500">
                Uploaded: {formatRelativeTime(existingDocument.uploadedAt)} (
                {formatDate(existingDocument.uploadedAt)})
              </p>
              {existingDocument.reviewedAt && (
                <p className="text-xs text-gray-500">
                  Reviewed: {formatRelativeTime(existingDocument.reviewedAt)} (
                  {formatDate(existingDocument.reviewedAt)})
                </p>
              )}
              {existingDocument.notes && (
                <p className="text-xs text-red-600 mt-1">
                  Notes: {existingDocument.notes}
                </p>
              )}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2 md:w-auto w-full">
          {!showUploadInput ? (
            <>
              {canUpload && (
                <button
                  onClick={() => setShowUploadInput(true)}
                  disabled={isUploading}
                  className="bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {status === 'REJECTED' ? 'Re-upload' : 'Upload'}
                </button>
              )}
              {showUploadAgain && (
                <button
                  onClick={() => setShowUploadInput(true)}
                  disabled={isUploading}
                  className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Upload again
                </button>
              )}
            </>
          ) : (
            <div className="flex flex-col gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                onChange={handleFileSelect}
                className="text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              />
              {selectedFile && (
                <div className="flex gap-2">
                  <button
                    onClick={handleUploadClick}
                    disabled={isUploading}
                    className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isUploading ? 'Uploading...' : 'Confirm Upload'}
                  </button>
                  <button
                    onClick={handleCancel}
                    disabled={isUploading}
                    className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function DocumentsPage() {
  const {
    data: documents,
    isLoading,
    error,
    refetch,
  } = useCreditDocuments();

  const uploadDocument = useUploadCreditDocument();
  const [uploadingDocumentType, setUploadingDocumentType] = useState<string | null>(null);
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [showErrorToast, setShowErrorToast] = useState(false);

  // Auto-dismiss success toast
  useEffect(() => {
    if (uploadDocument.isSuccess) {
      setShowSuccessToast(true);
      const timer = setTimeout(() => {
        setShowSuccessToast(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [uploadDocument.isSuccess]);

  // Auto-dismiss error toast
  useEffect(() => {
    if (uploadDocument.isError) {
      setShowErrorToast(true);
      const timer = setTimeout(() => {
        setShowErrorToast(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [uploadDocument.isError]);

  // Create a map of document type ID to document for quick lookup
  const documentMap = new Map<string, CreditDocument>();
  documents?.forEach((doc) => {
    documentMap.set(doc.documentType, doc);
  });

  const handleUpload = async (documentTypeId: string, file: File) => {
    setUploadingDocumentType(documentTypeId);
    try {
      await uploadDocument.mutateAsync({
        documentType: documentTypeId,
        file,
      });
      // Success message will be handled by the UI state
    } catch (error) {
      // Error is handled by the mutation state
      console.error('Upload failed:', error);
    } finally {
      // Clear uploading state after a delay to allow UI to update
      setTimeout(() => {
        setUploadingDocumentType(null);
      }, 1000);
    }
  };

  const handleDocumentUpload = (documentTypeId: string) => {
    return (file: File) => {
      handleUpload(documentTypeId, file);
    };
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Document Upload</h1>
        <p className="mt-2 text-gray-600">
          Upload documents to improve your credit score and unlock more BNPL products
        </p>
      </div>

      {/* Info Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-blue-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-blue-800">
              Improve your credit score
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                Upload verified documents to increase your credit score and unlock higher
                BNPL limits. Approved documents help lenders assess your creditworthiness
                and may improve your credit tier.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Documents List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="bg-white border border-gray-200 rounded-lg p-4 animate-pulse">
              <div className="h-20 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">
                Failed to load documents
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>
                  {error.message || 'An error occurred while loading your documents.'}
                </p>
              </div>
              <div className="mt-4">
                <button
                  onClick={() => refetch()}
                  className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : documents && documents.length === 0 && CREDIT_DOCUMENT_TYPES.length > 0 ? (
        <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No documents uploaded</h3>
          <p className="mt-1 text-sm text-gray-500">
            Start by uploading your mobile money statement or bank statement to begin
            building your credit profile.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {CREDIT_DOCUMENT_TYPES.map((docType) => {
            const existingDoc = documentMap.get(docType.id);
            const isUploadingForThisType =
              uploadDocument.isPending && uploadingDocumentType === docType.id;

            return (
              <DocumentRow
                key={docType.id}
                documentType={docType}
                existingDocument={existingDoc}
                onUpload={handleDocumentUpload(docType.id)}
                isUploading={isUploadingForThisType}
              />
            );
          })}
        </div>
      )}

      {/* Success Message */}
      {showSuccessToast && uploadDocument.isSuccess && (
        <div className="fixed bottom-4 right-4 bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg max-w-sm z-50">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-green-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-green-800">
                Document uploaded successfully!
              </p>
              <p className="mt-1 text-sm text-green-700">
                Your document is being reviewed. You'll be notified once it's processed.
              </p>
            </div>
            <button
              onClick={() => setShowSuccessToast(false)}
              className="ml-4 flex-shrink-0 text-green-400 hover:text-green-600"
            >
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Error Message */}
      {showErrorToast && uploadDocument.isError && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg max-w-sm z-50">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-red-800">Upload failed</p>
              <p className="mt-1 text-sm text-red-700">
                {uploadDocument.error?.message ||
                  'Failed to upload document. Please try again.'}
              </p>
            </div>
            <button
              onClick={() => setShowErrorToast(false)}
              className="ml-4 flex-shrink-0 text-red-400 hover:text-red-600"
            >
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

