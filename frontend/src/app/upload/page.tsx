'use client';

import { useRouter } from 'next/navigation';
import { FileUploadDropzone } from '@/components/forms/file-upload-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Scale,
  FileText,
  Users,
  TrendingUp,
  Shield,
  Clock,
  CheckCircle,
  ArrowLeft,
} from 'lucide-react';
import Link from 'next/link';

export default function UploadPage() {
  const router = useRouter();

  const handleUploadSuccess = (documentId: string) => {
    // Navigation is handled by the upload hook
    console.log('Upload successful, document ID:', documentId);
  };

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button asChild variant="ghost" className="mb-4">
            <Link href="/">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Link>
          </Button>
          
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center space-x-2">
              <Scale className="h-8 w-8 text-blue-600" />
              <h1 className="text-3xl font-bold text-gray-900">
                Upload Your Legal Document
              </h1>
            </div>
            
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Get instant AI-powered analysis of your contracts, leases, and legal documents. 
              Our advanced system provides risk assessments, plain-language explanations, and expert guidance.
            </p>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-2">
            <FileUploadDropzone
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
              className="mb-8"
            />
          </div>

          {/* Info Sidebar */}
          <div className="space-y-6">
            {/* What We Analyze */}
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-600" />
                  What We Analyze
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Rental & Lease Agreements</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Employment Contracts</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Service Agreements</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Loan Documents</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Insurance Policies</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Terms of Service</span>
                </div>
              </CardContent>
            </Card>

            {/* Analysis Features */}
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  Analysis Features
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-start gap-2">
                  <Badge variant="outline" className="text-xs mt-0.5">Risk</Badge>
                  <span>Overall risk score (1-10) with detailed breakdown</span>
                </div>
                <div className="flex items-start gap-2">
                  <Badge variant="outline" className="text-xs mt-0.5">Plain</Badge>
                  <span>Legal jargon translated to everyday language</span>
                </div>
                <div className="flex items-start gap-2">
                  <Badge variant="outline" className="text-xs mt-0.5">Rights</Badge>
                  <span>Consumer protection violations identified</span>
                </div>
                <div className="flex items-start gap-2">
                  <Badge variant="outline" className="text-xs mt-0.5">Legal</Badge>
                  <span>Relevant case law and precedents</span>
                </div>
                <div className="flex items-start gap-2">
                  <Badge variant="outline" className="text-xs mt-0.5">Tips</Badge>
                  <span>Negotiation strategies and alternatives</span>
                </div>
              </CardContent>
            </Card>

            {/* AI Experts */}
            <Card className="border-0 shadow-md bg-gradient-to-br from-blue-50 to-purple-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-purple-600" />
                  AI Expert Team
                  <Badge variant="secondary" className="ml-2">CrewAI</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="space-y-2">
                  <div className="font-medium text-blue-900">Dr. Sarah Chen</div>
                  <div className="text-blue-700 text-xs">Legal Research Specialist</div>
                </div>
                <div className="space-y-2">
                  <div className="font-medium text-green-900">Maria Rodriguez</div>
                  <div className="text-green-700 text-xs">Consumer Protection Advocate</div>
                </div>
                <div className="space-y-2">
                  <div className="font-medium text-purple-900">Dr. James Thompson</div>
                  <div className="text-purple-700 text-xs">Regulatory Compliance Expert</div>
                </div>
                <div className="space-y-2">
                  <div className="font-medium text-orange-900">Alexandra Williams</div>
                  <div className="text-orange-700 text-xs">Negotiation Strategy Advisor</div>
                </div>
                <div className="space-y-2">
                  <div className="font-medium text-indigo-900">Dr. Patricia Kim</div>
                  <div className="text-indigo-700 text-xs">Alternative Solutions Finder</div>
                </div>
              </CardContent>
            </Card>

            {/* Processing Time */}
            <Card className="border-0 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-yellow-600" />
                  Processing Time
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Basic Analysis:</span>
                  <span className="font-medium">1-2 minutes</span>
                </div>
                <div className="flex justify-between">
                  <span>Enhanced Analysis:</span>
                  <span className="font-medium">3-5 minutes</span>
                </div>
                <div className="text-xs text-gray-500 mt-3">
                  Processing time depends on document length and complexity. 
                  You'll see real-time progress updates during analysis.
                </div>
              </CardContent>
            </Card>

            {/* Security Notice */}
            <Card className="border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-900">
                  <Shield className="h-5 w-5 text-green-600" />
                  Security & Privacy
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-green-800">
                <p>
                  Your documents are processed securely with enterprise-grade encryption. 
                  We don't store your files permanently and automatically delete them 
                  after analysis completion.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Sample Documents Section */}
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Don't Have a Document Ready?
          </h2>
          <p className="text-gray-600 mb-6">
            Try our analysis with these sample documents to see how LegalClarity AI works.
          </p>
          
          <div className="flex flex-wrap justify-center gap-4">
            <Button variant="outline" className="text-sm">
              <FileText className="h-4 w-4 mr-2" />
              Sample Rental Agreement
            </Button>
            <Button variant="outline" className="text-sm">
              <FileText className="h-4 w-4 mr-2" />
              Employment Contract
            </Button>
            <Button variant="outline" className="text-sm">
              <FileText className="h-4 w-4 mr-2" />
              Service Agreement
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}