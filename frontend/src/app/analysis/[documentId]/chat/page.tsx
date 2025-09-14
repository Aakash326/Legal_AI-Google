'use client';

import { useParams } from 'next/navigation';
import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import {
  ArrowLeft,
  Send,
  MessageSquare,
  User,
  Bot,
  FileText,
  Sparkles,
  AlertTriangle,
  Clock,
  Eye,
} from 'lucide-react';
import Link from 'next/link';
import { useDocumentAnalysis, useDocumentChat } from '@/lib/hooks/api';
import { formatTimeAgo } from '@/lib/utils/format';
import { cn } from '@/lib/utils/format';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const params = useParams();
  const documentId = params?.documentId as string;
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    data: analysis,
    isLoading: analysisLoading,
    error: analysisError,
  } = useDocumentAnalysis(documentId, !!documentId);

  const chatMutation = useDocumentChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Add welcome message
  useEffect(() => {
    if (analysis && messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        role: 'assistant',
        content: `Hello! I'm your AI legal assistant. I've analyzed your document "${analysis.document_summary?.document_type || 'your document'}" and I'm ready to answer any questions you have about it. You can ask me about specific clauses, risk factors, legal implications, or anything else related to your document.`,
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    }
  }, [analysis, messages.length]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || chatMutation.isPending) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await chatMutation.mutateAsync({
        documentId,
        question: inputValue.trim(),
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer || 'I apologize, but I was unable to generate a response. Please try again.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error while processing your question. Please try again.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const suggestedQuestions = [
    "What are the main risk factors in this document?",
    "Can you explain the most concerning clauses in plain language?",
    "What should I negotiate before signing?",
    "Are there any consumer protection issues I should be aware of?",
    "What are my rights and obligations under this agreement?",
    "Are there any hidden fees or unfavorable terms?",
  ];

  if (analysisLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <Skeleton className="h-10 w-24 mb-6" />
            <Skeleton className="h-12 w-full max-w-2xl mb-8" />
            <div className="space-y-4">
              <Skeleton className="h-16" />
              <Skeleton className="h-20" />
              <Skeleton className="h-16" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (analysisError || !analysis) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            <Button asChild variant="ghost" className="mb-6">
              <Link href={`/analysis/${documentId}`}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Analysis
              </Link>
            </Button>

            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Unable to load document analysis. Please return to the analysis page.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <Button asChild variant="ghost">
                <Link href={`/analysis/${documentId}`}>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Analysis
                </Link>
              </Button>

              <Button asChild variant="outline">
                <Link href={`/analysis/${documentId}`}>
                  <Eye className="h-4 w-4 mr-2" />
                  View Full Analysis
                </Link>
              </Button>
            </div>

            <div className="flex items-center gap-3 mb-4">
              <MessageSquare className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Chat About Your Document
                </h1>
                <p className="text-gray-600 mt-1">
                  Ask questions about "{analysis.document_summary?.document_type || 'your document'}"
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span>Analyzed {formatTimeAgo(analysis.enhancement_timestamp || new Date().toISOString())}</span>
              <Badge variant="outline">
                {analysis.crew_ai_enhanced ? 'Enhanced Analysis' : 'Basic Analysis'}
              </Badge>
            </div>
          </div>

          <div className="grid lg:grid-cols-4 gap-6 lg:gap-8">
            {/* Chat Interface */}
            <div className="lg:col-span-3">
              <Card className="border-0 shadow-lg h-[500px] lg:h-[600px] flex flex-col">
                <CardHeader className="border-b">
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5 text-blue-600" />
                    AI Legal Assistant
                    <Badge variant="secondary" className="ml-2">
                      <Sparkles className="h-3 w-3 mr-1" />
                      CrewAI Powered
                    </Badge>
                  </CardTitle>
                </CardHeader>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={cn(
                        'flex gap-3',
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      <div
                        className={cn(
                          'flex gap-2 lg:gap-3 max-w-[85%] lg:max-w-[80%]',
                          message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                        )}
                      >
                        <div
                          className={cn(
                            'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
                            message.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-600'
                          )}
                        >
                          {message.role === 'user' ? (
                            <User className="h-4 w-4" />
                          ) : (
                            <Bot className="h-4 w-4" />
                          )}
                        </div>
                        
                        <div
                          className={cn(
                            'rounded-lg p-4',
                            message.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          )}
                        >
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">
                            {message.content}
                          </p>
                          <p className={cn(
                            'text-xs mt-2 opacity-70',
                            message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                          )}>
                            {message.timestamp.toLocaleTimeString([], { 
                              hour: '2-digit', 
                              minute: '2-digit' 
                            })}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}

                  {/* Typing indicator */}
                  {isTyping && (
                    <div className="flex gap-3 justify-start">
                      <div className="flex gap-3 max-w-[80%]">
                        <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                          <Bot className="h-4 w-4 text-gray-600" />
                        </div>
                        <div className="bg-gray-100 rounded-lg p-4">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="border-t p-4">
                  <div className="flex gap-2">
                    <Input
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask a question about your document..."
                      disabled={chatMutation.isPending}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleSendMessage}
                      disabled={!inputValue.trim() || chatMutation.isPending}
                      size="sm"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Document Info */}
              <Card className="border-0 shadow-md">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    Document Info
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                  <div>
                    <span className="text-gray-600">Title:</span>
                    <p className="font-medium mt-1">
                      {analysis.document_summary?.document_type || 'Untitled Document'}
                    </p>
                  </div>
                  
                  <div>
                    <span className="text-gray-600">Risk Score:</span>
                    <p className="font-medium mt-1">
                      {analysis.overall_risk_score?.toFixed(1) || 'N/A'}/10
                    </p>
                  </div>
                  
                  <div>
                    <span className="text-gray-600">Clauses:</span>
                    <p className="font-medium mt-1">
                      {analysis.key_clauses?.length || 0} analyzed
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Suggested Questions */}
              {messages.length <= 1 && (
                <Card className="border-0 shadow-md">
                  <CardHeader>
                    <CardTitle className="text-lg">Suggested Questions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {suggestedQuestions.map((question, index) => (
                        <button
                          key={index}
                          onClick={() => setInputValue(question)}
                          className="w-full text-left p-3 rounded-lg bg-blue-50 hover:bg-blue-100 text-sm text-blue-800 transition-colors"
                        >
                          {question}
                        </button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Tips */}
              <Card className="border-blue-200 bg-blue-50">
                <CardContent className="p-4">
                  <div className="text-sm text-blue-800">
                    <p className="font-medium mb-2">💡 Chat Tips:</p>
                    <ul className="space-y-1 text-xs">
                      <li>• Ask about specific clauses or sections</li>
                      <li>• Request plain-language explanations</li>
                      <li>• Inquire about negotiation strategies</li>
                      <li>• Ask about your rights and obligations</li>
                      <li>• Get clarification on risk factors</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}