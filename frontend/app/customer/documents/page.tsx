'use client';

import { useState, useRef, useEffect } from 'react';
import { useCreditDocuments, useUploadCreditDocument } from '@/lib/hooks/useCredit';
import { CREDIT_DOCUMENT_TYPES } from '@/lib/creditConstants';
import { formatDate, formatRelativeTime } from '@/lib/utils/creditHelpers';
import type { CreditDocument } from '@/types/credit';
import { PageHeader } from '@/components/ui/PageHeader';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';

function DocumentStatusBadge({
  status,
}: {
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'NOT_UPLOADED';
}) {
  const statusConfig = {
    APPROVED: { label: 'Approved', variant: 'success' as const },
    PENDING: { label: 'Pending review', variant: 'warning' as const },
    REJECTED: { label: 'Rejected', variant: 'danger' as const },
    NOT_UPLOADED: { label: 'Not uploaded', variant: 'default' as const },
  };

  const config = statusConfig[status] || statusConfig.NOT_UPLOADED;

  return <Badge variant={config.variant}>{config.label}</Badge>;
}

function DocumentCard({
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
    <Card hover>
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-lg font-bold text-gray-900">{documentType.label}</h3>
              <DocumentStatusBadge status={status} />
            </div>
            {documentType.description && (
              <p className="text-sm text-gray-600 mb-3">{documentType.description}</p>
            )}

            {existingDocument && (
              <div className="mt-3 space-y-1.5">
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
                  <p className="text-xs text-red-600 mt-2 font-medium">
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
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => setShowUploadInput(true)}
                    disabled={isUploading}
                  >
                    {status === 'REJECTED' ? 'Re-upload' : 'Upload'}
                  </Button>
                )}
                {showUploadAgain && (
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setShowUploadInput(true)}
                    disabled={isUploading}
                  >
                    Upload again
                  </Button>
                )}
              </>
            ) : (
              <div className="flex flex-col gap-2 min-w-[200px]">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                  onChange={handleFileSelect}
                  className="text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
                />
                {selectedFile && (
                  <div className="flex gap-2">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={handleUploadClick}
                      disabled={isUploading}
                      isLoading={isUploading}
                      className="flex-1"
                    >
                      {isUploading ? 'Uploading...' : 'Confirm Upload'}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleCancel}
                      disabled={isUploading}
                    >
                      Cancel
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
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
      await refetch();
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
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
    <div className="max-w-7xl mx-auto w-full">
      <PageHeader
        title="Document Upload"
        description="Upload documents to improve your credit score and unlock more BNPL products"
      />

      {/* Info Card */}
      <Card className="mb-6 border-indigo-200 bg-indigo-50">
        <CardContent className="p-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-indigo-600"
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
              <h3 className="text-sm font-semibold text-indigo-900">
                Improve your credit score
              </h3>
              <div className="mt-2 text-sm text-indigo-800">
                <p>
                  Upload verified documents to increase your credit score and unlock higher
                  BNPL limits. Approved documents help lenders assess your creditworthiness
                  and may improve your credit tier.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documents List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-20" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : error ? (
        <Card>
          <CardContent className="p-6">
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
                <h3 className="text-sm font-semibold text-red-800">
                  Failed to load documents
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error.message || 'An error occurred while loading your documents.'}</p>
                </div>
                <div className="mt-4">
                  <Button variant="danger" size="sm" onClick={() => refetch()}>
                    Try Again
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : documents && documents.length === 0 && CREDIT_DOCUMENT_TYPES.length > 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-4"
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
            <h3 className="mt-2 text-lg font-semibold text-gray-900">No documents uploaded</h3>
            <p className="mt-1 text-sm text-gray-500">
              Start by uploading your mobile money statement or bank statement to begin
              building your credit profile.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {CREDIT_DOCUMENT_TYPES.map((docType) => {
            const existingDoc = documentMap.get(docType.id);
            const isUploadingForThisType =
              uploadDocument.isPending && uploadingDocumentType === docType.id;

            return (
              <DocumentCard
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

      {/* Success Toast */}
      {showSuccessToast && uploadDocument.isSuccess && (
        <div className="fixed bottom-4 right-4 bg-white border border-green-200 rounded-xl shadow-lg p-4 max-w-sm z-50">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-green-600"
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
              <p className="text-sm font-semibold text-green-800">
                Document uploaded successfully!
              </p>
              <p className="mt-1 text-sm text-green-700">
                Your document is being reviewed. You&apos;ll be notified once it&apos;s processed.
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

      {/* Error Toast */}
      {showErrorToast && uploadDocument.isError && (
        <div className="fixed bottom-4 right-4 bg-white border border-red-200 rounded-xl shadow-lg p-4 max-w-sm z-50">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-600"
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
              <p className="text-sm font-semibold text-red-800">Upload failed</p>
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
