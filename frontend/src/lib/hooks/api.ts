// React Query hooks for API integration

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import {
  uploadDocumentWithProgress,
  getDocumentStatus,
  getBasicAnalysis,
  getEnhancedAnalysis,
  submitQuery,
  getSystemStatus,
  handleApiError,
} from '../api/client';
import type { QueryRequest } from '../types/api';

// Upload hooks
export const useDocumentUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      file,
      enhancementEnabled,
      onProgress,
    }: {
      file: File;
      enhancementEnabled: boolean;
      onProgress?: (progress: number) => void;
    }) => uploadDocumentWithProgress(file, enhancementEnabled, onProgress),
    onSuccess: (data) => {
      // Invalidate system status to update document count
      queryClient.invalidateQueries({ queryKey: ['system-status'] });
      // Don't redirect automatically - let the component handle navigation after processing
    },
    onError: (error) => {
      console.error('Upload failed:', handleApiError(error));
    },
  });
};

// Status tracking hooks
export const useDocumentStatus = (documentId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['document-status', documentId],
    queryFn: () => getDocumentStatus(documentId),
    refetchInterval: (data) => {
      // Stop polling if completed or failed
      if (!data || data.status === 'completed' || data.status === 'failed') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
    enabled: !!documentId && enabled,
    retry: 3,
    retryDelay: 1000,
  });
};

// Analysis hooks
export const useBasicAnalysis = (documentId: string, enabled: boolean = false) => {
  return useQuery({
    queryKey: ['basic-analysis', documentId],
    queryFn: () => getBasicAnalysis(documentId),
    enabled: !!documentId && enabled,
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useEnhancedAnalysis = (documentId: string, enabled: boolean = false) => {
  return useQuery({
    queryKey: ['enhanced-analysis', documentId],
    queryFn: () => getEnhancedAnalysis(documentId),
    enabled: !!documentId && enabled,
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Smart analysis hook that tries enhanced first, falls back to basic
export const useDocumentAnalysis = (documentId: string, enabled: boolean = false) => {
  const enhancedQuery = useEnhancedAnalysis(documentId, enabled);
  const basicQuery = useBasicAnalysis(
    documentId,
    enabled && !!enhancedQuery.error && !enhancedQuery.isLoading
  );

  return {
    data: enhancedQuery.data || basicQuery.data,
    isLoading: enhancedQuery.isLoading || basicQuery.isLoading,
    error: enhancedQuery.error || basicQuery.error,
    isEnhanced: !!enhancedQuery.data,
    refetch: enhancedQuery.data ? enhancedQuery.refetch : basicQuery.refetch,
  };
};

// Q&A hooks
export const useSubmitQuery = () => {
  return useMutation({
    mutationFn: (queryData: QueryRequest) => submitQuery(queryData),
    onError: (error) => {
      console.error('Query failed:', handleApiError(error));
    },
  });
};

// Document chat hook
export const useDocumentChat = () => {
  return useMutation({
    mutationFn: ({ documentId, question }: { documentId: string; question: string }) => 
      submitQuery({ document_id: documentId, query: question }),
    onError: (error) => {
      console.error('Chat query failed:', handleApiError(error));
    },
  });
};

// System status hooks
export const useSystemStatus = () => {
  return useQuery({
    queryKey: ['system-status'],
    queryFn: getSystemStatus,
    refetchInterval: 30000, // Refresh every 30 seconds
    retry: 1,
  });
};

// Custom hook for managing upload state
export const useUploadState = () => {
  return {
    isUploading: false,
    progress: 0,
    error: null as string | null,
  };
};

// Helper hook for error handling
export const useApiErrorHandler = () => {
  return {
    handleError: (error: unknown) => {
      const message = handleApiError(error);
      // You can integrate with a toast system here
      console.error('API Error:', message);
      return message;
    },
  };
};