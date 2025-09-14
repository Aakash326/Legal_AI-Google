'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  FileText,
  Eye,
  Search,
  Users,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap,
  RefreshCw,
  ArrowRight,
} from 'lucide-react';
import { useDocumentStatus } from '@/lib/hooks/api';
import { cn, formatDuration, getStatusColor, formatStatusText } from '@/lib/utils/format';
import { DocumentStatus } from '@/lib/types/api';
import Link from 'next/link';

interface ProcessingStatusTrackerProps {
  documentId: string;
  onComplete?: (status: DocumentStatus) => void;
  onError?: (error: string) => void;
  className?: string;
}

const PROCESSING_STEPS = [
  {
    key: 'document_extraction',
    icon: FileText,
    label: 'Extracting Document Text',
    description: 'Reading and parsing your document content',
    estimatedTime: 15,
  },
  {
    key: 'legal_analysis',
    icon: Search,
    label: 'Analyzing Legal Clauses',
    description: 'Identifying and categorizing legal terms',
    estimatedTime: 30,
  },
  {
    key: 'risk_assessment',
    icon: Eye,
    label: 'Risk Assessment',
    description: 'Calculating risk scores and identifying issues',
    estimatedTime: 20,
  },
  {
    key: 'crew_enhancement',
    icon: Users,
    label: 'AI Expert Analysis',
    description: '5 specialized agents providing expert insights',
    estimatedTime: 180,
  },
];

export function ProcessingStatusTracker({
  documentId,
  onComplete,
  onError,
  className,
}: ProcessingStatusTrackerProps) {
  const [startTime] = useState(Date.now());
  const [elapsedTime, setElapsedTime] = useState(0);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  const {
    data: status,
    isLoading,
    error,
    refetch,
  } = useDocumentStatus(documentId, !!documentId);

  // Update elapsed time every second
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedTime(Date.now() - startTime);
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  // Handle status changes
  useEffect(() => {
    if (status) {
      // Determine current step based on status
      if (status.current_step) {
        const stepIndex = PROCESSING_STEPS.findIndex(step => 
          status.current_step.toLowerCase().includes(step.key) ||
          status.current_step.toLowerCase().includes(step.label.toLowerCase())
        );
        if (stepIndex !== -1) {
          setCurrentStepIndex(stepIndex);
        }
      }

      // Handle completion
      if (status.status === 'completed') {
        onComplete?.(status);
      }

      // Handle errors
      if (status.status === 'failed' && status.error_message) {
        onError?.(status.error_message);
      }
    }
  }, [status, onComplete, onError]);

  // Handle query errors
  useEffect(() => {
    if (error) {
      onError?.(error instanceof Error ? error.message : 'Failed to get status');
    }
  }, [error, onError]);

  if (isLoading && !status) {
    return (
      <Card className={cn("w-full max-w-2xl mx-auto", className)}>
        <CardContent className="p-6">
          <div className="flex items-center justify-center space-x-2">
            <RefreshCw className="h-5 w-5 animate-spin text-blue-600" />
            <span className="text-gray-600">Connecting to analysis server...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  const progress = status.progress || 0;
  const isCompleted = status.status === 'completed';
  const isFailed = status.status === 'failed';
  const isProcessing = status.status === 'processing';

  // Calculate estimated time remaining
  const totalEstimatedTime = PROCESSING_STEPS.reduce((sum, step, index) => {
    if (index <= currentStepIndex) {
      return sum + step.estimatedTime;
    }
    return sum;
  }, 0);

  const remainingSteps = PROCESSING_STEPS.slice(currentStepIndex + 1);
  const estimatedTimeRemaining = remainingSteps.reduce((sum, step) => sum + step.estimatedTime, 0);

  return (
    <div className={cn("w-full max-w-2xl mx-auto space-y-6", className)}>
      {/* Main Status Card */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              {isCompleted ? (
                <CheckCircle className="h-6 w-6 text-green-600" />
              ) : isFailed ? (
                <AlertCircle className="h-6 w-6 text-red-600" />
              ) : (
                <div className="relative">
                  <Zap className="h-6 w-6 text-blue-600" />
                  {isProcessing && (
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-600 rounded-full animate-ping" />
                  )}
                </div>
              )}
              <span className="text-xl">
                {isCompleted ? 'Analysis Complete!' : 
                 isFailed ? 'Analysis Failed' : 
                 'Analyzing Your Document'}
              </span>
            </CardTitle>
            
            <Badge 
              variant={isCompleted ? 'default' : isFailed ? 'destructive' : 'secondary'}
              className={cn(
                isCompleted && 'bg-green-600 hover:bg-green-700',
                isProcessing && 'bg-blue-600 hover:bg-blue-700'
              )}
            >
              {formatStatusText(status.status)}
            </Badge>
          </div>
          
          {status.current_step && !isCompleted && !isFailed && (
            <p className="text-gray-600 mt-2">{status.current_step}</p>
          )}
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Progress Bar */}
          {!isFailed && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Progress</span>
                <span className="font-medium">{Math.round(progress)}%</span>
              </div>
              <Progress 
                value={progress} 
                className={cn(
                  "h-3 transition-all duration-500",
                  isCompleted && "[&>div]:bg-green-600"
                )}
              />
            </div>
          )}

          {/* Time Information */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-gray-400" />
              <div>
                <div className="text-gray-600">Elapsed Time</div>
                <div className="font-medium">{formatDuration(elapsedTime / 1000)}</div>
              </div>
            </div>
            
            {!isCompleted && !isFailed && estimatedTimeRemaining > 0 && (
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-blue-400" />
                <div>
                  <div className="text-gray-600">Est. Remaining</div>
                  <div className="font-medium text-blue-600">
                    {formatDuration(estimatedTimeRemaining)}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Error Message */}
          {isFailed && status.error_message && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{status.error_message}</AlertDescription>
            </Alert>
          )}

          {/* Success Actions */}
          {isCompleted && (
            <div className="flex flex-col sm:flex-row gap-3">
              <Button asChild size="lg" className="flex-1">
                <Link href={`/analysis/${documentId}`}>
                  <Eye className="h-4 w-4 mr-2" />
                  View Analysis Results
                </Link>
              </Button>
              
              <Button asChild variant="outline" size="lg">
                <Link href={`/analysis/${documentId}/chat`}>
                  Ask Questions
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Link>
              </Button>
            </div>
          )}

          {/* Retry Button for Failed Status */}
          {isFailed && (
            <Button
              onClick={() => refetch()}
              variant="outline"
              className="w-full"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry Analysis
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Processing Steps */}
      {!isCompleted && !isFailed && (
        <Card className="border-0 shadow-md">
          <CardHeader>
            <CardTitle className="text-lg">Processing Steps</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {PROCESSING_STEPS.map((step, index) => {
                const isCurrentStep = index === currentStepIndex;
                const isCompletedStep = index < currentStepIndex || (isCompleted && index <= currentStepIndex);
                const isPendingStep = index > currentStepIndex;
                
                const StepIcon = step.icon;
                
                return (
                  <div
                    key={step.key}
                    className={cn(
                      "flex items-start space-x-4 p-3 rounded-lg transition-all duration-300",
                      isCurrentStep && "bg-blue-50 border border-blue-200",
                      isCompletedStep && !isCurrentStep && "bg-green-50 border border-green-200",
                      isPendingStep && "bg-gray-50 border border-gray-200"
                    )}
                  >
                    {/* Icon */}
                    <div className={cn(
                      "flex items-center justify-center w-8 h-8 rounded-full",
                      isCompletedStep && !isCurrentStep && "bg-green-100",
                      isCurrentStep && "bg-blue-100",
                      isPendingStep && "bg-gray-100"
                    )}>
                      {isCompletedStep && !isCurrentStep ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : (
                        <StepIcon className={cn(
                          "h-5 w-5",
                          isCurrentStep && "text-blue-600 animate-pulse",
                          isCompletedStep && !isCurrentStep && "text-green-600",
                          isPendingStep && "text-gray-400"
                        )} />
                      )}
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className={cn(
                        "font-medium",
                        isCurrentStep && "text-blue-900",
                        isCompletedStep && !isCurrentStep && "text-green-900",
                        isPendingStep && "text-gray-500"
                      )}>
                        {step.label}
                      </div>
                      <div className={cn(
                        "text-sm mt-1",
                        isCurrentStep && "text-blue-700",
                        isCompletedStep && !isCurrentStep && "text-green-700",
                        isPendingStep && "text-gray-400"
                      )}>
                        {step.description}
                      </div>
                      
                      {/* Current step indicator */}
                      {isCurrentStep && (
                        <div className="flex items-center mt-2 text-xs text-blue-600">
                          <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse mr-2" />
                          Processing...
                        </div>
                      )}
                    </div>
                    
                    {/* Time estimate */}
                    <div className={cn(
                      "text-xs font-medium px-2 py-1 rounded",
                      isCurrentStep && "text-blue-600 bg-blue-100",
                      isCompletedStep && !isCurrentStep && "text-green-600 bg-green-100",
                      isPendingStep && "text-gray-500 bg-gray-100"
                    )}>
                      {isCompletedStep && !isCurrentStep ? '✓' : `~${step.estimatedTime}s`}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Tips Card */}
      {!isCompleted && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-2">💡 While you wait:</p>
              <ul className="space-y-1 text-xs">
                <li>• Keep this page open to see real-time progress</li>
                <li>• Enhanced analysis with CrewAI takes longer but provides deeper insights</li>
                <li>• You'll be able to ask questions about your document once analysis is complete</li>
                <li>• Results are automatically saved and you can return anytime</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}