'use client';

import { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  X,
  Zap,
  Shield,
  Clock,
  Brain,
} from 'lucide-react';
import { cn, formatFileSize } from '@/lib/utils/format';
import { useDocumentUpload, useDocumentStatus } from '@/lib/hooks/api';
import { toast } from 'sonner';

interface FileUploadDropzoneProps {
  onUploadSuccess?: (documentId: string) => void;
  onUploadError?: (error: string) => void;
  className?: string;
}

const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/msword': ['.doc'],
  'text/plain': ['.txt'],
};

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export function FileUploadDropzone({
  onUploadSuccess,
  onUploadError,
  className,
}: FileUploadDropzoneProps) {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [enhancementEnabled, setEnhancementEnabled] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [processingStage, setProcessingStage] = useState<'idle' | 'uploading' | 'processing' | 'completed' | 'error'>('idle');

  const uploadMutation = useDocumentUpload();
  
  // Poll document status after upload
  const statusQuery = useDocumentStatus(
    documentId || '', 
    !!documentId && processingStage === 'processing'
  );

  // Monitor document processing status
  useEffect(() => {
    if (statusQuery.data && processingStage === 'processing') {
      const status = statusQuery.data.status;
      
      if (status === 'completed') {
        setProcessingStage('completed');
        toast.success('Analysis completed! Redirecting to results...');
        
        // Redirect to analysis page after a brief moment
        setTimeout(() => {
          router.push(`/analysis/${documentId}`);
        }, 1000);
        
        onUploadSuccess?.(documentId || '');
      } else if (status === 'failed') {
        setProcessingStage('error');
        const error = statusQuery.data.error || 'Document processing failed';
        toast.error(error);
        onUploadError?.(error);
      }
      // If status is 'processing' or 'pending', keep polling
    }
  }, [statusQuery.data, processingStage, documentId, router, onUploadSuccess, onUploadError]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setIsDragging(false);
    
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    
    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      const error = `File is too large. Maximum size is ${formatFileSize(MAX_FILE_SIZE)}.`;
      toast.error(error);
      onUploadError?.(error);
      return;
    }
    
    setSelectedFile(file);
    setUploadProgress(0);
  }, [onUploadError]);

  const onDropRejected = useCallback((rejectedFiles: any[]) => {
    setIsDragging(false);
    
    if (rejectedFiles.length > 0) {
      const { errors } = rejectedFiles[0];
      const error = errors[0]?.code === 'file-invalid-type' 
        ? 'Invalid file type. Please upload a PDF, DOCX, DOC, or TXT file.'
        : 'File upload failed. Please try again.';
      
      toast.error(error);
      onUploadError?.(error);
    }
  }, [onUploadError]);

  // Calculate state variables before using them in hooks
  const isUploading = processingStage === 'uploading';
  const isProcessing = processingStage === 'processing';
  const isCompleted = processingStage === 'completed';
  const hasError = processingStage === 'error' || uploadMutation.isError;
  const isWorking = isUploading || isProcessing;

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    onDragEnter: () => setIsDragging(true),
    onDragLeave: () => setIsDragging(false),
    accept: ACCEPTED_FILE_TYPES,
    maxFiles: 1,
    maxSize: MAX_FILE_SIZE,
    disabled: isWorking,
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setProcessingStage('uploading');
      setUploadProgress(0);
      
      const result = await uploadMutation.mutateAsync({
        file: selectedFile,
        enhancementEnabled,
        onProgress: (progress) => {
          setUploadProgress(progress);
        },
      });

      // Upload completed, now start processing phase
      const docId = result.document_id;
      setDocumentId(docId);
      setProcessingStage('processing');
      
      toast.success('Upload complete! Starting analysis...');
      
      // Note: The useEffect will handle status monitoring and redirect when complete
    } catch (error) {
      setProcessingStage('error');
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      toast.error(errorMessage);
      onUploadError?.(errorMessage);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    setDocumentId(null);
    setProcessingStage('idle');
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    const iconClass = "h-5 w-5";
    
    switch (extension) {
      case 'pdf':
        return <FileText className={cn(iconClass, "text-red-500")} />;
      case 'docx':
      case 'doc':
        return <FileText className={cn(iconClass, "text-blue-500")} />;
      case 'txt':
        return <FileText className={cn(iconClass, "text-gray-500")} />;
      default:
        return <FileText className={cn(iconClass, "text-gray-400")} />;
    }
  };

  return (
    <div className={cn("w-full max-w-2xl mx-auto space-y-6", className)}>
      {/* Dropzone */}
      <Card className="relative overflow-hidden">
        <div
          {...getRootProps()}
          className={cn(
            "relative p-8 border-2 border-dashed rounded-lg transition-all duration-200 cursor-pointer",
            "hover:border-blue-400 hover:bg-blue-50/50",
            isDragActive || isDragging 
              ? "border-blue-500 bg-blue-50 scale-[1.02]" 
              : "border-gray-300",
            isWorking && "pointer-events-none opacity-50",
            hasError && "border-red-300 bg-red-50"
          )}
        >
          <input {...getInputProps()} />
          
          <div className="text-center space-y-4">
            {/* Upload Icon */}
            <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              {isDragActive ? (
                <Upload className="h-8 w-8 text-blue-600 animate-bounce" />
              ) : (
                <Upload className="h-8 w-8 text-blue-600" />
              )}
            </div>

            {/* Main Text */}
            <div className="space-y-2">
              {isDragActive ? (
                <p className="text-lg font-medium text-blue-600">
                  Drop your document here
                </p>
              ) : (
                <div>
                  <p className="text-lg font-medium text-gray-900">
                    Drop your legal document here, or{' '}
                    <span className="text-blue-600">browse files</span>
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports PDF, DOCX, DOC, and TXT files up to {formatFileSize(MAX_FILE_SIZE)}
                  </p>
                </div>
              )}
            </div>

            {/* Supported File Types */}
            <div className="flex flex-wrap justify-center gap-2">
              {['PDF', 'DOCX', 'DOC', 'TXT'].map((type) => (
                <Badge key={type} variant="secondary" className="text-xs">
                  {type}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Selected File Display */}
      {selectedFile && (
        <Card className="p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              {getFileIcon(selectedFile.name)}
              <div>
                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
            </div>
            
            {!isWorking && !isCompleted && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFile}
                className="text-gray-400 hover:text-red-500"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Progress Bar and Status (shown during upload and processing) */}
          {isUploading && (
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 flex items-center gap-2">
                  <Upload className="h-4 w-4 animate-pulse" />
                  Uploading document...
                </span>
                <span className="font-medium">{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} className="h-2" />
            </div>
          )}

          {isProcessing && (
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-blue-600 flex items-center gap-2">
                  <Brain className="h-4 w-4 animate-pulse" />
                  {enhancementEnabled ? 'Analyzing with AI experts...' : 'Analyzing document...'}
                </span>
                <span className="text-blue-600 font-medium">
                  <Clock className="h-4 w-4 animate-spin inline mr-1" />
                  Processing
                </span>
              </div>
              <Progress value={100} className="h-2 [&>div]:animate-pulse" />
              <div className="text-xs text-gray-500">
                {statusQuery.data?.progress || 'Extracting legal clauses and assessing risks...'}
              </div>
            </div>
          )}

          {isCompleted && (
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-green-600 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4" />
                  Analysis completed!
                </span>
                <span className="text-green-600 font-medium">100%</span>
              </div>
              <Progress value={100} className="h-2 [&>div]:bg-green-500" />
              <div className="text-xs text-green-600">
                Redirecting to results...
              </div>
            </div>
          )}

          {/* Enhancement Toggle */}
          <div className="flex items-center justify-between mb-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <Zap className="h-4 w-4 text-blue-600" />
                <span className="font-medium text-gray-900">CrewAI Enhanced Analysis</span>
              </div>
              <Badge variant="outline" className="text-xs">
                5 AI Experts
              </Badge>
            </div>
            
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={enhancementEnabled}
                onChange={(e) => setEnhancementEnabled(e.target.checked)}
                disabled={isWorking}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {/* Enhancement Description */}
          {enhancementEnabled && (
            <Alert className="mb-4 border-blue-200 bg-blue-50">
              <Shield className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-sm">
                <strong>Enhanced analysis includes:</strong> Legal precedent research, consumer protection analysis, 
                compliance checking, negotiation strategies, and alternative solutions from 5 specialized AI agents.
              </AlertDescription>
            </Alert>
          )}

          {/* Upload Button */}
          <Button
            onClick={handleUpload}
            disabled={isWorking || !selectedFile}
            size="lg"
            className="w-full"
          >
            {isUploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                Uploading Document...
              </>
            ) : isProcessing ? (
              <>
                <Brain className="h-4 w-4 mr-2 animate-pulse" />
                {enhancementEnabled ? 'AI Experts Analyzing...' : 'Processing Document...'}
              </>
            ) : isCompleted ? (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Analysis Complete!
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                {enhancementEnabled ? 'Start Enhanced Analysis' : 'Start Basic Analysis'}
              </>
            )}
          </Button>

          {/* Time Estimate */}
          <p className="text-xs text-center text-gray-500 mt-2">
            {isProcessing ? (
              enhancementEnabled 
                ? 'Enhanced analysis in progress - this may take 3-5 minutes'
                : 'Basic analysis in progress - this typically takes 1-2 minutes'
            ) : isCompleted ? (
              'Analysis completed successfully!'
            ) : (
              enhancementEnabled 
                ? 'Enhanced analysis typically takes 3-5 minutes'
                : 'Basic analysis typically takes 1-2 minutes'
            )}
          </p>
        </Card>
      )}

      {/* Error Display */}
      {hasError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {uploadMutation.error?.message || 'Upload failed. Please try again.'}
          </AlertDescription>
        </Alert>
      )}

      {/* Privacy Notice */}
      <Card className="p-4 bg-gray-50 border-gray-200">
        <div className="flex items-start space-x-3">
          <Shield className="h-5 w-5 text-green-600 mt-0.5" />
          <div className="text-sm text-gray-600">
            <p className="font-medium text-gray-900 mb-1">Your Privacy is Protected</p>
            <ul className="space-y-1 text-xs">
              <li>• Documents are processed securely and deleted after analysis</li>
              <li>• No data is stored permanently on our servers</li>
              <li>• Analysis results are only accessible to you</li>
              <li>• All communications are encrypted in transit</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}