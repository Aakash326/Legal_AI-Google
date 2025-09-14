import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Scale,
  FileText,
  Shield,
  Zap,
  Users,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Upload,
  Clock,
  Eye,
} from 'lucide-react';

export default function Home() {
  return (
    <div className="space-y-16 py-8">
      {/* Hero Section */}
      <section className="container mx-auto px-4 text-center space-y-8">
        <div className="max-w-3xl mx-auto space-y-6">
          <Badge variant="outline" className="mb-4 px-4 py-1">
            <Zap className="h-3 w-3 mr-2" />
            Powered by Advanced AI Agents
          </Badge>
          
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 leading-tight">
            Make Legal Documents
            <span className="text-blue-600 block">Understandable</span>
          </h1>
          
          <p className="text-xl text-gray-600 leading-relaxed max-w-2xl mx-auto">
            Upload any contract, lease, or legal document and get instant AI-powered analysis with risk assessments, plain-language explanations, and expert guidance.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="px-8 py-3">
              <Link href="/upload">
                <Upload className="h-5 w-5 mr-2" />
                Analyze Your Document
              </Link>
            </Button>
            
            <Button asChild variant="outline" size="lg" className="px-8 py-3">
              <Link href="/demo">
                <Eye className="h-5 w-5 mr-2" />
                View Demo
              </Link>
            </Button>
          </div>
          
          <div className="flex items-center justify-center gap-8 text-sm text-gray-500 mt-8">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Free Analysis</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-500" />
              <span>Secure & Private</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-green-500" />
              <span>Results in Minutes</span>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How LegalClarity AI Works
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our advanced AI system analyzes your documents through multiple expert lenses to provide comprehensive insights.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                <Upload className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">1. Upload Document</h3>
              <p className="text-gray-600">
                Simply drag and drop your PDF, DOCX, or TXT file. We support contracts, leases, and most legal documents.
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <Users className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">2. AI Expert Analysis</h3>
              <p className="text-gray-600">
                5 specialized AI agents analyze your document: Legal Researcher, Consumer Advocate, Compliance Expert, Negotiation Advisor, and Solutions Finder.
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto">
                <FileText className="h-8 w-8 text-yellow-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">3. Get Insights</h3>
              <p className="text-gray-600">
                Receive detailed analysis with risk scores, plain-language explanations, negotiation strategies, and alternative options.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Powerful Features for Everyone
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Whether you're a consumer, small business owner, or just need to understand a legal document, we've got you covered.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                Risk Assessment
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Get clear risk scores (1-10) for your entire document and individual clauses with color-coded warnings.
              </p>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-green-600" />
                Plain Language Explanations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Complex legal jargon translated into everyday language you can actually understand.
              </p>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-purple-600" />
                Consumer Protection Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Identify unfair practices, hidden fees, and violations of consumer protection laws.
              </p>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Scale className="h-5 w-5 text-red-600" />
                Legal Precedent Research
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Discover how similar clauses have been interpreted in court cases and legal precedents.
              </p>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-600" />
                Compliance Checking
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Verify compliance with federal and state regulations, including CFPB, FTC, and industry-specific rules.
              </p>
            </CardContent>
          </Card>
          
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-indigo-600" />
                Negotiation Strategies
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Get tactical advice on which terms to negotiate, leverage points, and alternative language suggestions.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center space-y-8">
          <div className="max-w-2xl mx-auto space-y-4">
            <h2 className="text-3xl font-bold">
              Ready to Understand Your Legal Documents?
            </h2>
            <p className="text-xl text-blue-100">
              Join thousands of people who are making better informed legal decisions with LegalClarity AI.
            </p>
          </div>
          
          <Button asChild size="lg" variant="secondary" className="px-8 py-3">
            <Link href="/upload">
              <Upload className="h-5 w-5 mr-2" />
              Start Your Free Analysis
            </Link>
          </Button>
          
          <p className="text-sm text-blue-200">
            No registration required • Analysis typically takes 2-5 minutes • Your documents are not stored
          </p>
        </div>
      </section>
    </div>
  );
}