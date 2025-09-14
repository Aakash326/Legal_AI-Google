import Link from 'next/link';
import { Scale } from 'lucide-react';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full border-t bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and Description */}
          <div className="col-span-1 md:col-span-2">
            <Link href="/" className="flex items-center space-x-2 mb-4">
              <Scale className="h-6 w-6 text-blue-600" />
              <span className="font-bold text-lg text-gray-900">LegalClarity AI</span>
            </Link>
            <p className="text-gray-600 text-sm max-w-md">
              Making legal documents understandable for everyday people through advanced AI analysis and expert insights.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Quick Links</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <Link href="/upload" className="hover:text-gray-900 transition-colors">
                  Upload Document
                </Link>
              </li>
              <li>
                <Link href="/history" className="hover:text-gray-900 transition-colors">
                  Document History
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="hover:text-gray-900 transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-gray-900 transition-colors">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Support</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <Link href="/help" className="hover:text-gray-900 transition-colors">
                  Help Center
                </Link>
              </li>
              <li>
                <a 
                  href="mailto:support@legalclarity.ai" 
                  className="hover:text-gray-900 transition-colors"
                >
                  Contact Support
                </a>
              </li>
              <li>
                <Link href="/faq" className="hover:text-gray-900 transition-colors">
                  FAQ
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex flex-col sm:flex-row justify-between items-center text-sm text-gray-600">
            <div className="mb-4 sm:mb-0">
              <p>&copy; {currentYear} LegalClarity AI. All rights reserved.</p>
            </div>
            
            <div className="flex items-center space-x-6">
              <p className="text-xs">
                <strong className="text-red-600">Disclaimer:</strong> This is not legal advice. 
                Consult a qualified attorney for legal matters.
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}