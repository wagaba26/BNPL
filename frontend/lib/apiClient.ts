import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/lib/store/authStore';

// Get API base URL from environment variable
// In production on Vercel, this MUST be set in environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

// Validate that API_BASE_URL is set in production
if (!API_BASE_URL) {
  if (typeof window !== 'undefined') {
    console.error(
      'NEXT_PUBLIC_API_BASE_URL is not set. Please configure it in your Vercel environment variables.'
    );
  }
  // In production, we should throw an error, but for development we allow localhost fallback
  if (process.env.NODE_ENV === 'production') {
    throw new Error(
      'NEXT_PUBLIC_API_BASE_URL environment variable is required but not set. ' +
      'Please configure it in your Vercel project settings.'
    );
  }
}

// Fallback to localhost only in development
const finalApiBaseUrl = API_BASE_URL || (process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '');

// Log API base URL in development
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  console.log('API Base URL:', finalApiBaseUrl);
}

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: finalApiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage (AuthContext stores it there)
    const token = typeof window !== 'undefined' ? localStorage.getItem('bnpl_access_token') : null;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Custom error class for API errors
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors (server not reachable)
    if (!error.response) {
      const isNetworkError = error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || error.message?.includes('Network Error');
      const message = isNetworkError
        ? `Cannot connect to backend server at ${finalApiBaseUrl || 'configured URL'}. Please make sure the backend is running and NEXT_PUBLIC_API_BASE_URL is set correctly.`
        : `Network error: ${error.message || 'Failed to connect to server'}`;
      
      const apiError = new ApiError(message, undefined, { 
        code: error.code,
        originalError: error.message,
        url: error.config?.url,
        baseURL: finalApiBaseUrl
      });
      return Promise.reject(apiError);
    }

    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('bnpl_access_token');
        localStorage.removeItem('bnpl_user');
        window.location.href = '/login';
      }
    }

    // Create a more descriptive error
    const status = error.response?.status;
    const statusText = error.response?.statusText || 'Unknown Error';
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      `Request failed with status ${status || 'unknown'}: ${statusText}`;

    const apiError = new ApiError(message, status, error.response?.data);
    return Promise.reject(apiError);
  }
);

export default apiClient;

