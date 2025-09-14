// Utility functions for formatting data

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Risk level formatting
export const getRiskColorByLevel = (riskLevel: 'low' | 'medium' | 'high' | 'critical') => {
  const colors = {
    low: 'text-green-600 bg-green-50 border-green-200',
    medium: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    high: 'text-orange-600 bg-orange-50 border-orange-200',
    critical: 'text-red-600 bg-red-50 border-red-200',
  };
  return colors[riskLevel] || colors.low;
};

export const getRiskBadgeColor = (riskLevel: 'low' | 'medium' | 'high' | 'critical') => {
  const colors = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  };
  return colors[riskLevel] || colors.low;
};

// Score formatting
export const formatRiskScore = (score: number): string => {
  return score.toFixed(1);
};

export const getRiskLevelFromScore = (score: number): 'low' | 'medium' | 'high' | 'critical' => {
  if (score <= 3) return 'low';
  if (score <= 6) return 'medium';
  if (score <= 8) return 'high';
  return 'critical';
};

// Time formatting
export const formatTimeAgo = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
};

export const formatDuration = (seconds: number): string => {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  if (remainingSeconds === 0) return `${minutes}m`;
  return `${minutes}m ${remainingSeconds}s`;
};

// File formatting
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

export const getFileTypeFromName = (filename: string): string => {
  const extension = filename.split('.').pop()?.toLowerCase();
  const types: Record<string, string> = {
    pdf: 'PDF Document',
    docx: 'Word Document',
    doc: 'Word Document',
    txt: 'Text File',
  };
  return types[extension || ''] || 'Unknown File';
};

// Text formatting
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
};

export const capitalizeFirst = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1);
};

export const formatClauseType = (type: string): string => {
  return type
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => capitalizeFirst(word))
    .join(' ');
};

// Progress formatting
export const getProgressColor = (progress: number): string => {
  if (progress < 25) return 'bg-red-500';
  if (progress < 50) return 'bg-orange-500';
  if (progress < 75) return 'bg-yellow-500';
  return 'bg-green-500';
};

// Status formatting
export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    pending: 'text-gray-500 bg-gray-100',
    processing: 'text-blue-600 bg-blue-100',
    completed: 'text-green-600 bg-green-100',
    failed: 'text-red-600 bg-red-100',
  };
  return colors[status] || colors.pending;
};

export const formatStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: 'Waiting to Start',
    processing: 'Processing...',
    completed: 'Completed',
    failed: 'Failed',
  };
  return statusMap[status] || capitalizeFirst(status);
};

// Additional risk utilities for visualization
export function formatRiskLevel(riskScore: number): string {
  if (riskScore <= 3) return 'Low Risk';
  if (riskScore <= 7) return 'Medium Risk';
  return 'High Risk';
}

export function getRiskColor(riskScore: number, type: 'text' | 'background' | 'border' | 'badge' | 'gauge'): string {
  const isLow = riskScore <= 3;
  const isMedium = riskScore > 3 && riskScore <= 7;
  const isHigh = riskScore > 7;

  switch (type) {
    case 'text':
      if (isLow) return 'text-green-600';
      if (isMedium) return 'text-yellow-600';
      return 'text-red-600';
    
    case 'background':
      if (isLow) return 'bg-green-600';
      if (isMedium) return 'bg-yellow-600';
      return 'bg-red-600';
    
    case 'border':
      if (isLow) return 'border-green-200 bg-green-50';
      if (isMedium) return 'border-yellow-200 bg-yellow-50';
      return 'border-red-200 bg-red-50';
    
    case 'badge':
      if (isLow) return 'text-green-700 border-green-300';
      if (isMedium) return 'text-yellow-700 border-yellow-300';
      return 'text-red-700 border-red-300';
    
    case 'gauge':
      if (isLow) return 'text-green-500';
      if (isMedium) return 'text-yellow-500';
      return 'text-red-500';
    
    default:
      return '';
  }
}

export function getRiskIcon(riskScore: number): any {
  // This will be imported as needed in components
  return null;
}