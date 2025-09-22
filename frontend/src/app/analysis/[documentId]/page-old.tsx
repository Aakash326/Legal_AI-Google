'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import {
  ArrowLeft,
  Download,
  MessageSquare,
  Share2,
  FileText,
  AlertTriangle,
  Scale,
  Users,
  Clock,
  TrendingUp,
  Eye,
  CheckCircle,
} from 'lucide-react';
import Link from 'next/link';
import { useDocumentAnalysis, useDocumentStatus } from '@/lib/hooks/api';
import { RiskScoreVisualization } from '@/components/visualizations/risk-score-visualization';
import { formatTimeAgo, formatFileSize } from '@/lib/utils/format';
import { toast } from 'sonner';

export default function AnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const documentId = params?.documentId as string;
  const [activeTab, setActiveTab] = useState('overview');

  // Try to get document status first to check if processing is complete
  const statusQuery = useDocumentStatus(documentId, !!documentId);
  const isProcessing = statusQuery.data?.status === 'processing' || statusQuery.data?.status === 'pending';
  
  const {
    data: analysis,
    isLoading,
    error,
    refetch,
  } = useDocumentAnalysis(documentId, !!documentId && !isProcessing);

  // Show processing state when document is still being analyzed
  if (isProcessing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            <Button asChild variant="ghost" className="mb-6">
              <Link href="/upload">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Upload
              </Link>
            </Button>

            <Card className="border-0 shadow-lg">
              <CardContent className="p-8 text-center">
                <div className="space-y-6">
                  {/* Processing Animation */}
                  <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                    <Clock className="h-8 w-8 text-blue-600 animate-spin" />
                  </div>

                  {/* Status */}
                  <div className="space-y-2">
                    <h1 className="text-2xl font-bold text-gray-900">
                      Analyzing Your Document
                    </h1>
                    <p className="text-gray-600">
                      {statusQuery.data?.progress || 'Our AI experts are analyzing your legal document...'}
                    </p>
                  </div>

                  {/* Progress Steps */}
                  <div className="space-y-3 text-left bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm text-gray-700">Document uploaded successfully</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Clock className="h-5 w-5 text-blue-600 animate-pulse" />
                      <span className="text-sm text-gray-700">Extracting legal clauses and assessing risks</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Clock className="h-5 w-5 text-gray-400" />
                      <span className="text-sm text-gray-500">Generating recommendations and insights</span>
                    </div>
                  </div>

                  {/* Time Estimate */}
                  <div className="text-xs text-gray-500">
                    Analysis typically takes 1-3 minutes depending on document complexity
                  </div>

                  {/* Auto-refresh Notice */}
                  <div className="text-xs text-blue-600">
                    This page will automatically refresh when analysis is complete
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          {/* Header Skeleton */}
          <div className="mb-8">
            <div className="flex items-center gap-4 mb-6">
              <Skeleton className="h-10 w-24" />
              <Skeleton className="h-8 w-48" />
            </div>
            <Skeleton className="h-12 w-full max-w-2xl" />
          </div>

          {/* Content Skeleton */}
          <div className="grid lg:grid-cols-4 gap-8">
            <div className="lg:col-span-3 space-y-6">
              <Skeleton className="h-96" />
              <Skeleton className="h-64" />
            </div>
            <div className="space-y-4">
              <Skeleton className="h-32" />
              <Skeleton className="h-48" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            <Button asChild variant="ghost" className="mb-6">
              <Link href="/upload">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Upload
              </Link>
            </Button>

            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                {error instanceof Error ? error.message : 'Failed to load analysis results.'}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => refetch()}
                  className="ml-4"
                >
                  Try Again
                </Button>
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </div>
    );
  }

  const handleDownloadReport = () => {
    // TODO: Implement PDF report generation
    toast.success('Report download will be available soon');
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `Legal Analysis - Document ${analysis.document_id}`,
        url: window.location.href,
      }).catch(() => {
        // Fallback to copying URL
        navigator.clipboard.writeText(window.location.href);
        toast.success('Analysis URL copied to clipboard');
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Analysis URL copied to clipboard');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <Button asChild variant="ghost">
              <Link href="/upload">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Upload
              </Link>
            </Button>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
              <Button
                variant="outline"
                onClick={handleShare}
                className="hidden sm:flex"
                size="sm"
              >
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </Button>
              
              <Button
                variant="outline"
                onClick={handleDownloadReport}
                size="sm"
              >
                <Download className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Download Report</span>
                <span className="sm:hidden">Download</span>
              </Button>
              
              <Button asChild size="sm">
                <Link href={`/analysis/${documentId}/chat`}>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  <span className="hidden sm:inline">Ask Questions</span>
                  <span className="sm:hidden">Chat</span>
                </Link>
              </Button>
            </div>
          </div>

          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  {analysis.document_summary?.document_type || 'Legal Document Analysis'}
                </h1>
                <div className="flex items-center gap-4 text-sm text-gray-500 mt-2">
                  <span>Document ID: {analysis.document_id.slice(0, 8)}...</span>
                  <Badge variant="outline" className="font-medium">
                    {analysis.crew_ai_enhanced ? 'Enhanced Analysis' : 'Basic Analysis'}
                  </Badge>
                </div>
              </div>
            </div>

            {analysis.document_explanation && (
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <FileText className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900 mb-3">Document Summary</h2>
                    <p className="text-gray-700 leading-relaxed text-lg">{analysis.document_explanation}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="grid lg:grid-cols-4 gap-6 lg:gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 mb-6">
                <TabsTrigger value="overview" className="flex items-center gap-1 lg:gap-2 text-xs lg:text-sm">
                  <Eye className="h-3 w-3 lg:h-4 lg:w-4" />
                  <span className="hidden sm:inline">Overview</span>
                  <span className="sm:hidden">Risk</span>
                </TabsTrigger>
                <TabsTrigger value="risks" className="flex items-center gap-1 lg:gap-2 text-xs lg:text-sm">
                  <AlertTriangle className="h-3 w-3 lg:h-4 lg:w-4" />
                  <span className="hidden sm:inline">Risk Analysis</span>
                  <span className="sm:hidden">Analysis</span>
                </TabsTrigger>
                <TabsTrigger value="legal" className="flex items-center gap-1 lg:gap-2 text-xs lg:text-sm">
                  <Scale className="h-3 w-3 lg:h-4 lg:w-4" />
                  <span className="hidden sm:inline">Legal Insights</span>
                  <span className="sm:hidden">Legal</span>
                </TabsTrigger>
                <TabsTrigger value="recommendations" className="flex items-center gap-1 lg:gap-2 text-xs lg:text-sm">
                  <TrendingUp className="h-3 w-3 lg:h-4 lg:w-4" />
                  <span className="hidden sm:inline">Recommendations</span>
                  <span className="sm:hidden">Tips</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <RiskScoreVisualization analysis={analysis} />
                
                {/* AI-Generated Document Explanation */}
                {(analysis.document_explanation || analysis.practical_impact) && (
                  <Card className="border-0 shadow-md">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5 text-blue-600" />
                        Document Analysis Summary
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {analysis.document_explanation && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-3">What This Document Is About:</h4>
                          <div className="space-y-4">
                            {analysis.document_explanation.split(/[.!?]+/).filter(sentence => sentence.trim()).map((sentence, index) => (
                              <p key={index} className="text-gray-700 leading-relaxed mb-4 text-sm">
                                {sentence.trim()}.
                              </p>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {analysis.practical_impact && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-3">Practical Impact:</h4>
                          <div className="space-y-4">
                            {analysis.practical_impact.split(/[.!?]+/).filter(sentence => sentence.trim()).map((sentence, index) => (
                              <p key={index} className="text-gray-700 leading-relaxed mb-4 text-sm">
                                {sentence.trim()}.
                              </p>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {analysis.key_provisions_explained && analysis.key_provisions_explained.length > 0 && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-2">Key Provisions Explained:</h4>
                          <ul className="space-y-2">
                            {analysis.key_provisions_explained.map((provision, index) => (
                              <li key={index} className="flex items-start gap-2">
                                <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                                <span className="text-gray-700">{provision}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="risks" className="space-y-6">
                <RiskScoreVisualization 
                  analysis={analysis} 
                  showDetails={true}
                />
                
                {/* Consumer Protection Issues */}
                {analysis.consumer_protection_violations && analysis.consumer_protection_violations.length > 0 && (
                  <Card className="border-0 shadow-md">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-red-600" />
                        Consumer Protection Concerns
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {analysis.consumer_protection_violations.map((violation, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                            <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                            <p className="text-sm text-red-800">{violation}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="legal" className="space-y-6">
                {/* AI-Generated Legal Implications */}
                {analysis.legal_implications && analysis.legal_implications.length > 0 && (
                  <Card className="border-0 shadow-md">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Scale className="h-5 w-5 text-blue-600" />
                        Legal Implications
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {analysis.legal_implications.map((implication, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <Scale className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                            <p className="text-sm text-blue-800">{implication}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Clause-by-Clause Summary */}
                {analysis.clause_by_clause_summary && analysis.clause_by_clause_summary.length > 0 && (
                  <Card className="border-0 shadow-md">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5 text-green-600" />
                        Clause-by-Clause Summary
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {analysis.clause_by_clause_summary.map((summary, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                            <div className="w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0">
                              {index + 1}
                            </div>
                            <p className="text-sm text-green-800">{summary}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Legal Precedents */}
                {analysis.legal_precedents && analysis.legal_precedents.length > 0 && (
                  <Card className="border-0 shadow-md">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Scale className="h-5 w-5 text-blue-600" />
                        Relevant Legal Precedents
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {analysis.legal_precedents.map((precedent, index) => (
                          <div key={index} className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                            <h4 className="font-medium text-blue-900 mb-2">
                              {precedent.case_name || `Precedent ${index + 1}`}
                            </h4>
                            <p className="text-sm text-blue-800 mb-2">
                              {precedent.relevance || precedent.summary}
                            </p>
                            {precedent.citation && (
                              <p className="text-xs text-blue-600 font-mono">
                                {precedent.citation}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Compliance Issues */}
                {analysis.compliance_issues && analysis.compliance_issues.length > 0 && (
                  <Card className="border-0 shadow-md">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-orange-600" />
                        Compliance Concerns
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {analysis.compliance_issues.map((issue, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                            <AlertTriangle className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
                            <div>
                              <p className="text-sm text-orange-800 font-medium">
                                {issue.regulation || 'Compliance Issue'}
                              </p>
                              <p className="text-sm text-orange-700 mt-1">
                                {issue.description || issue}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-6">
                {/* Negotiation Strategies */}
                {analysis.negotiation_strategies && analysis.negotiation_strategies.length > 0 && (
                  <Card className="border-0 shadow-md">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-green-600" />
                        Negotiation Strategies
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {analysis.negotiation_strategies.map((strategy, index) => (
                          <div key={index} className="p-4 bg-green-50 border border-green-200 rounded-lg">
                            <h4 className="font-medium text-green-900 mb-2">
                              {strategy.title || `Strategy ${index + 1}`}
                            </h4>
                            <p className="text-sm text-green-800 mb-3">
                              {strategy.description || strategy}
                            </p>
                            {strategy.priority && (
                              <Badge variant="outline" className="text-green-700 border-green-300">
                                {strategy.priority} Priority
                              </Badge>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Alternative Solutions */}
                {analysis.alternative_solutions && analysis.alternative_solutions.length > 0 && (
                  <Card className="border-0 shadow-md">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Users className="h-5 w-5 text-purple-600" />
                        Alternative Solutions
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {analysis.alternative_solutions.map((solution, index) => (
                          <div key={index} className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                            <h4 className="font-medium text-purple-900 mb-2">
                              {solution.title || `Solution ${index + 1}`}
                            </h4>
                            <p className="text-sm text-purple-800 mb-3">
                              {solution.description || solution}
                            </p>
                            {solution.feasibility && (
                              <div className="flex items-center gap-2">
                                <span className="text-xs text-purple-600">Feasibility:</span>
                                <Badge variant="outline" className="text-purple-700 border-purple-300">
                                  {solution.feasibility}
                                </Badge>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button asChild size="sm" className="w-full">
                  <Link href={`/analysis/${documentId}/chat`}>
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Ask Questions
                  </Link>
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDownloadReport}
                  className="w-full"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Report
                </Button>
                
                <Button asChild variant="outline" size="sm" className="w-full">
                  <Link href="/upload">
                    <FileText className="h-4 w-4 mr-2" />
                    Analyze Another Document
                  </Link>
                </Button>
              </CardContent>
            </Card>

            {/* Analysis Stats */}
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="text-lg">Analysis Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Processing Time:</span>
                    <span className="font-medium">
                      {analysis.processing_time ? `${analysis.processing_time}s` : 'N/A'}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Clauses Analyzed:</span>
                    <span className="font-medium">
                      {analysis.clause_analysis?.length || 0}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Enhancement:</span>
                    <Badge variant={analysis.enhancement_enabled ? 'default' : 'outline'}>
                      {analysis.enhancement_enabled ? 'CrewAI Enhanced' : 'Basic'}
                    </Badge>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Created:</span>
                    <span className="font-medium">
                      {formatTimeAgo(analysis.created_at || new Date().toISOString())}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card className="border-blue-200 bg-blue-50">
              <CardContent className="p-4">
                <div className="text-sm text-blue-800">
                  <p className="font-medium mb-2">💡 Next Steps:</p>
                  <ul className="space-y-1 text-xs">
                    <li>• Review high-risk clauses in detail</li>
                    <li>• Consider negotiation strategies provided</li>
                    <li>• Ask specific questions using the chat feature</li>
                    <li>• Download report for your records</li>
                    <li>• Consult with a legal professional for complex issues</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}