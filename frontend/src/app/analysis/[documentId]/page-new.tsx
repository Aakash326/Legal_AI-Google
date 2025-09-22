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
  Clock,
  TrendingUp,
  Eye,
  CheckCircle,
  Shield,
  Users,
  Target,
} from 'lucide-react';
import Link from 'next/link';
import { useDocumentAnalysis, useDocumentStatus } from '@/lib/hooks/api';
import { RiskScoreVisualization } from '@/components/visualizations/risk-score-visualization';
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
                      {statusQuery.data?.current_step || 'Our AI experts are analyzing your legal document...'}
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
    toast.success('Report download will be available soon');
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `Legal Analysis - Document ${analysis.document_id}`,
        url: window.location.href,
      }).catch(() => {
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
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
            <Button asChild variant="ghost" size="lg">
              <Link href="/upload">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Upload
              </Link>
            </Button>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <Button
                variant="outline"
                onClick={handleShare}
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
                Download Report
              </Button>
              
              <Button asChild size="sm">
                <Link href={`/analysis/${documentId}/chat`}>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Ask Questions
                </Link>
              </Button>
            </div>
          </div>

          {/* Document Header */}
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100">
            <div className="flex items-start gap-6">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center flex-shrink-0">
                <FileText className="h-8 w-8 text-white" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-3xl font-bold text-gray-900">
                    {analysis.document_summary?.document_type || 'Legal Document Analysis'}
                  </h1>
                  <Badge variant="outline" className="font-medium">
                    {analysis.crew_ai_enhanced ? 'Enhanced Analysis' : 'Basic Analysis'}
                  </Badge>
                </div>
                <p className="text-gray-600 mb-4">
                  Document ID: {analysis.document_id.slice(0, 8)}... • 
                  {analysis.processing_stats && ` ${analysis.processing_stats.total_pages} pages • ${analysis.processing_stats.total_words} words`}
                </p>
                
                {analysis.document_explanation && (
                  <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
                    <h3 className="font-semibold text-gray-900 mb-2">Summary</h3>
                    <p className="text-gray-700 leading-relaxed">{analysis.document_explanation}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Main Analysis Area */}
          <div className="lg:col-span-3">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-4 mb-8 bg-white p-1 rounded-xl shadow-sm">
                <TabsTrigger value="overview" className="flex items-center gap-2 rounded-lg data-[state=active]:bg-blue-50 data-[state=active]:text-blue-700">
                  <Eye className="h-4 w-4" />
                  Overview
                </TabsTrigger>
                <TabsTrigger value="risks" className="flex items-center gap-2 rounded-lg data-[state=active]:bg-red-50 data-[state=active]:text-red-700">
                  <AlertTriangle className="h-4 w-4" />
                  Risks
                </TabsTrigger>
                <TabsTrigger value="legal" className="flex items-center gap-2 rounded-lg data-[state=active]:bg-purple-50 data-[state=active]:text-purple-700">
                  <Scale className="h-4 w-4" />
                  Legal
                </TabsTrigger>
                <TabsTrigger value="recommendations" className="flex items-center gap-2 rounded-lg data-[state=active]:bg-green-50 data-[state=active]:text-green-700">
                  <TrendingUp className="h-4 w-4" />
                  Actions
                </TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <RiskScoreVisualization analysis={analysis} />
                
                {analysis.practical_impact && (
                  <Card className="border-0 shadow-md">
                    <CardHeader className="pb-4">
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Target className="h-5 w-5 text-blue-600" />
                        What This Means for You
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-700 leading-relaxed text-lg">{analysis.practical_impact}</p>
                    </CardContent>
                  </Card>
                )}

                {analysis.key_provisions_explained && analysis.key_provisions_explained.length > 0 && (
                  <Card className="border-0 shadow-md">
                    <CardHeader className="pb-4">
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <FileText className="h-5 w-5 text-blue-600" />
                        Key Provisions Explained
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {analysis.key_provisions_explained.map((provision, index) => (
                          <div key={index} className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg">
                            <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">
                              {index + 1}
                            </div>
                            <p className="text-gray-700 leading-relaxed">{provision}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="risks" className="space-y-6">
                <RiskScoreVisualization 
                  analysis={analysis} 
                  showDetails={true}
                />
                
                {analysis.red_flags && analysis.red_flags.length > 0 && (
                  <Card className="border-0 shadow-md border-l-4 border-l-red-500">
                    <CardHeader className="pb-4">
                      <CardTitle className="flex items-center gap-2 text-lg text-red-700">
                        <AlertTriangle className="h-5 w-5" />
                        Red Flags Identified
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {analysis.red_flags.map((flag, index) => (
                          <div key={index} className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                            <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                            <p className="text-red-800 font-medium">{flag}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="legal" className="space-y-6">
                {analysis.legal_implications && analysis.legal_implications.length > 0 && (
                  <Card className="border-0 shadow-md">
                    <CardHeader className="pb-4">
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Scale className="h-5 w-5 text-purple-600" />
                        Legal Implications
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {analysis.legal_implications.map((implication, index) => (
                          <div key={index} className="flex items-start gap-3 p-4 bg-purple-50 border border-purple-200 rounded-lg">
                            <Scale className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                            <p className="text-purple-800">{implication}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* CrewAI Enhanced Insights */}
                {analysis.crew_ai_enhanced && analysis.legal_precedent_research && (
                  <Card className="border-0 shadow-md">
                    <CardHeader className="pb-4">
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Users className="h-5 w-5 text-indigo-600" />
                        Legal Research & Precedents
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="prose prose-sm max-w-none">
                        <p className="text-gray-700 leading-relaxed">{analysis.legal_precedent_research}</p>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-6">
                {analysis.recommendations && analysis.recommendations.length > 0 && (
                  <Card className="border-0 shadow-md border-l-4 border-l-green-500">
                    <CardHeader className="pb-4">
                      <CardTitle className="flex items-center gap-2 text-lg text-green-700">
                        <TrendingUp className="h-5 w-5" />
                        Recommended Actions
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {analysis.recommendations.map((recommendation, index) => (
                          <div key={index} className="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                            <div className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">
                              {index + 1}
                            </div>
                            <p className="text-green-800 font-medium">{recommendation}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* CrewAI Negotiation Guidance */}
                {analysis.crew_ai_enhanced && analysis.negotiation_guidance && (
                  <Card className="border-0 shadow-md">
                    <CardHeader className="pb-4">
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Users className="h-5 w-5 text-indigo-600" />
                        Negotiation Strategies
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="prose prose-sm max-w-none">
                        <p className="text-gray-700 leading-relaxed">{analysis.negotiation_guidance}</p>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Risk Score Summary */}
            <Card className="border-0 shadow-md">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg">Risk Assessment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center space-y-4">
                  <div className="text-4xl font-bold text-gray-900">
                    {analysis.overall_risk_score.toFixed(1)}/10
                  </div>
                  <Badge 
                    variant="outline"
                    className={`text-sm px-3 py-1 ${
                      analysis.overall_risk_score >= 7 ? 'border-red-300 text-red-700 bg-red-50' :
                      analysis.overall_risk_score >= 4 ? 'border-yellow-300 text-yellow-700 bg-yellow-50' :
                      'border-green-300 text-green-700 bg-green-50'
                    }`}
                  >
                    {analysis.risk_level.toUpperCase()} RISK
                  </Badge>
                  {analysis.overall_risk_explanation && (
                    <p className="text-sm text-gray-600 mt-3">{analysis.overall_risk_explanation}</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Document Stats */}
            {analysis.processing_stats && (
              <Card className="border-0 shadow-md">
                <CardHeader className="pb-4">
                  <CardTitle className="text-lg">Document Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Pages:</span>
                      <span className="font-medium">{analysis.processing_stats.total_pages}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Words:</span>
                      <span className="font-medium">{analysis.processing_stats.total_words.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Processing Time:</span>
                      <span className="font-medium">{analysis.processing_stats.processing_time.toFixed(1)}s</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Key Clauses:</span>
                      <span className="font-medium">{analysis.key_clauses?.length || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Enhanced Features */}
            {analysis.crew_ai_enhanced && (
              <Card className="border-0 shadow-md bg-gradient-to-br from-indigo-50 to-purple-50">
                <CardHeader className="pb-4">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Shield className="h-5 w-5 text-indigo-600" />
                    Enhanced Features
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>AI Legal Research</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Consumer Protection Analysis</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Compliance Assessment</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Negotiation Strategies</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
