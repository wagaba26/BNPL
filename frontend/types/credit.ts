/**
 * Credit-related TypeScript types
 * These types use camelCase to match frontend conventions,
 * even though the backend may use snake_case.
 */

export interface CreditProfile {
  score: number;
  tier: string;
  maxBnplLimit: number;
  lastRecalculatedAt: string | null;
}

export interface CreditScoreEvent {
  id: string;
  eventType: string;
  delta: number;
  scoreBefore: number;
  scoreAfter: number;
  metadata?: Record<string, any> | null;
  createdAt: string;
}

export type CreditDocumentStatus = "PENDING" | "APPROVED" | "REJECTED";

export interface CreditDocument {
  id: string;
  documentType: string;
  status: CreditDocumentStatus;
  uploadedAt: string;
  reviewedAt?: string | null;
  notes?: string | null;
}

/**
 * Backend response types (snake_case) - used for API responses
 * These will be transformed to camelCase in the API layer
 */
export interface CreditProfileResponse {
  score: number;
  tier: string;
  max_bnpl_limit: number;
  last_recalculated_at: string | null;
}

export interface CreditScoreEventResponse {
  id: string;
  event_type: string;
  delta: number;
  score_before: number;
  score_after: number;
  metadata?: Record<string, any> | null;
  created_at: string;
}

export interface CreditDocumentResponse {
  id: string;
  document_type: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  uploaded_at: string;
  reviewed_at?: string | null;
  notes?: string | null;
}

/**
 * Request types for mutations
 */
export interface UploadCreditDocumentRequest {
  documentType: string;
  file: File;
}

