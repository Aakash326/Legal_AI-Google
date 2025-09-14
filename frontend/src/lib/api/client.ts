// API Client for LegalClarity AI Backend

import axios, { AxiosError } from 'axios';
import type {
  UploadResponse,
  DocumentStatus,
  DocumentAnalysis,
  QueryRequest,
  QueryResponse,
  SystemStatus
} from '../types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use((config) => {
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Document Upload Functions
export const uploadDocument = async (
  file: File,
  enhancementEnabled: boolean = true
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (enhancementEnabled) {
    formData.append('use_crew_enhancement', 'true');
    const response = await apiClient.post<UploadResponse>('/upload/enhanced', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } else {
    const response = await apiClient.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};

// Status Tracking Functions
export const getDocumentStatus = async (documentId: string): Promise<DocumentStatus> => {
  const response = await apiClient.get<DocumentStatus>(`/status/${documentId}`);
  return response.data;
};

// Analysis Results Functions
export const getBasicAnalysis = async (documentId: string): Promise<DocumentAnalysis> => {
  const response = await apiClient.get<DocumentAnalysis>(`/analysis/${documentId}`);
  return response.data;
};

export const getEnhancedAnalysis = async (documentId: string): Promise<DocumentAnalysis> => {
  const response = await apiClient.get<DocumentAnalysis>(`/analysis/${documentId}/enhanced`);
  return response.data;
};

// Q&A Functions
export const submitQuery = async (queryData: QueryRequest): Promise<QueryResponse> => {
  const response = await apiClient.post<QueryResponse>('/query', queryData);
  return response.data;
};

// System Status Functions
export const getSystemStatus = async (): Promise<SystemStatus> => {
  const response = await apiClient.get<SystemStatus>('/system/status');
  return response.data;
};

export const getHealthCheck = async (): Promise<{ status: string; timestamp: string }> => {
  const response = await apiClient.get('/health');
  return response.data;
};

// Error handling utilities
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 404) {
      return 'Document not found. Please check the document ID.';
    } else if (error.response?.status === 422) {
      return 'Document is still being processed. Please wait and try again.';
    } else if (error.response?.status === 413) {
      return 'File is too large. Please upload a file smaller than 50MB.';
    } else if (error.response?.status === 415) {
      return 'Unsupported file type. Please upload a PDF, DOCX, or TXT file.';
    } else if (error.response?.status === 429) {
      return 'Too many requests. Please wait a moment and try again.';
    } else if (error.response?.status >= 500) {
      return 'Server error. Please try again later or contact support.';
    } else if (error.response?.data?.message) {
      return error.response.data.message;
    }
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred. Please try again.';
};

// Upload progress tracking
export const uploadDocumentWithProgress = async (
  file: File,
  enhancementEnabled: boolean = true,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const endpoint = enhancementEnabled ? '/upload/enhanced' : '/upload';
  
  if (enhancementEnabled) {
    formData.append('use_crew_enhancement', 'true');
  }
  
  const response = await apiClient.post<UploadResponse>(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });
  
  return response.data;
};