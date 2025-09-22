'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  AlertTriangle,
  CheckCircle,
  Shield,
  TrendingUp,
  TrendingDown,
  Minus,
  Eye,
  EyeOff,
  Info,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { cn, formatRiskLevel, getRiskColor, getRiskIcon } from '@/lib/utils/format';
import { AnalysisResult, RiskScore, ClauseAnalysis } from '@/lib/types/api';

interface RiskScoreVisualizationProps {
  analysis: AnalysisResult;
  className?: string;
  showDetails?: boolean;
}

interface RiskGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  label: string;
  className?: string;
}

function RiskGauge({ score, size = 'md', label, className }: RiskGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(score);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32',
  };

  const strokeWidth = size === 'sm' ? 6 : size === 'md' ? 8 : 10;
  const radius = size === 'sm' ? 20 : size === 'md' ? 28 : 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (animatedScore / 10) * circumference;

  return (
    <div className={cn('flex flex-col items-center space-y-2', className)}>
      <div className={cn('relative', sizeClasses[size])}>
        <svg
          className="transform -rotate-90 w-full h-full"
          viewBox="0 0 80 80"
        >
          {/* Background circle */}
          <circle
            cx="40"
            cy="40"
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx="40"
            cy="40"
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={cn(
              'transition-all duration-1000 ease-out',
              getRiskColor(score, 'gauge')
            )}
          />
        </svg>
        
        {/* Score display */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={cn(
              'font-bold',
              size === 'sm' ? 'text-lg' : size === 'md' ? 'text-xl' : 'text-2xl',
              getRiskColor(score, 'text')
            )}>
              {animatedScore.toFixed(1)}
            </div>
            <div className="text-xs text-gray-500">/ 10</div>
          </div>
        </div>
      </div>
      
      <div className="text-center">
        <div className={cn(
          'font-medium',
          size === 'sm' ? 'text-sm' : 'text-base'
        )}>
          {label}
        </div>
        <Badge
          variant="outline"
          className={cn(
            'mt-1 text-xs',
            getRiskColor(score, 'badge')
          )}
        >
          {formatRiskLevel(score)}
        </Badge>
      </div>
    </div>
  );
}

function ClauseRiskItem({ clause, index }: { clause: ClauseAnalysis; index: number }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const riskScore = clause.risk_score || 5;

  return (
    <div className={cn(
      'border rounded-lg p-4 transition-all duration-200',
      getRiskColor(riskScore, 'border')
    )}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <div className={cn(
              'w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold text-white',
              getRiskColor(riskScore, 'background')
            )}>
              {index + 1}
            </div>
            <h4 className="font-medium text-gray-900 truncate">
              {clause.clause_title || `Clause ${index + 1}`}
            </h4>
          </div>
          
          <p className="text-sm text-gray-600 mb-3">
            {clause.plain_language_explanation || clause.analysis}
          </p>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Risk Level:</span>
              <Badge
                variant="outline"
                className={cn(
                  'text-xs',
                  getRiskColor(riskScore, 'badge')
                )}
              >
                {formatRiskLevel(riskScore)}
              </Badge>
            </div>
            
            {clause.consumer_protection_issues && clause.consumer_protection_issues.length > 0 && (
              <div className="flex items-center gap-1">
                <AlertTriangle className="h-4 w-4 text-orange-500" />
                <span className="text-xs text-orange-600">
                  {clause.consumer_protection_issues.length} issue(s)
                </span>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <RiskGauge
            score={riskScore}
            size="sm"
            label=""
            className="flex-shrink-0"
          />
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex-shrink-0"
          >
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
      
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
          {clause.negotiation_points && clause.negotiation_points.length > 0 && (
            <div>
              <h5 className="text-sm font-medium text-gray-900 mb-2">Negotiation Points:</h5>
              <ul className="text-sm text-gray-600 space-y-1">
                {clause.negotiation_points.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <TrendingUp className="h-3 w-3 text-blue-500 mt-0.5 flex-shrink-0" />
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {clause.consumer_protection_issues && clause.consumer_protection_issues.length > 0 && (
            <div>
              <h5 className="text-sm font-medium text-gray-900 mb-2">Consumer Protection Issues:</h5>
              <ul className="text-sm text-gray-600 space-y-1">
                {clause.consumer_protection_issues.map((issue, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <AlertTriangle className="h-3 w-3 text-red-500 mt-0.5 flex-shrink-0" />
                    <span>{issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {clause.alternative_language && (
            <div>
              <h5 className="text-sm font-medium text-gray-900 mb-2">Suggested Alternative Language:</h5>
              <div className="p-3 bg-green-50 border border-green-200 rounded text-sm text-green-800">
                {clause.alternative_language}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function RiskScoreVisualization({
  analysis,
  className,
  showDetails = true,
}: RiskScoreVisualizationProps) {
  const [showAllClauses, setShowAllClauses] = useState(false);
  const [visibleClauses, setVisibleClauses] = useState(3);

  const overallRisk = analysis.overall_risk_score || 5;
  const clauses = analysis.clause_analysis || [];
  const riskBreakdown = analysis.risk_breakdown || {};

  // Calculate risk distribution
  const riskDistribution = {
    low: clauses.filter(c => (c.risk_score || 5) <= 3).length,
    medium: clauses.filter(c => (c.risk_score || 5) > 3 && (c.risk_score || 5) <= 7).length,
    high: clauses.filter(c => (c.risk_score || 5) > 7).length,
  };

  const displayedClauses = showAllClauses ? clauses : clauses.slice(0, visibleClauses);
  const hasMoreClauses = clauses.length > visibleClauses;

  return (
    <div className={cn('space-y-6', className)}>
      {/* Overall Risk Score Card */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-blue-600" />
            Overall Risk Assessment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Main Risk Gauge */}
            <div className="flex-shrink-0 flex justify-center lg:justify-start">
              <RiskGauge
                score={overallRisk}
                size="lg"
                label="Overall Risk"
              />
            </div>
            
            {/* Risk Breakdown */}
            <div className="flex-1 space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Risk Breakdown</h3>
              
              {/* Risk Categories */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="text-2xl font-bold text-green-600 mb-1">
                    {riskDistribution.low}
                  </div>
                  <div className="text-sm text-green-700">Low Risk Clauses</div>
                </div>
                
                <div className="text-center p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <div className="text-2xl font-bold text-yellow-600 mb-1">
                    {riskDistribution.medium}
                  </div>
                  <div className="text-sm text-yellow-700">Medium Risk Clauses</div>
                </div>
                
                <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className="text-2xl font-bold text-red-600 mb-1">
                    {riskDistribution.high}
                  </div>
                  <div className="text-sm text-red-700">High Risk Clauses</div>
                </div>
              </div>

              {/* Key Risk Factors */}
              {Object.keys(riskBreakdown).length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Key Risk Factors</h4>
                  <div className="space-y-2">
                    {Object.entries(riskBreakdown).map(([factor, score]) => (
                      <div key={factor} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 capitalize">
                          {factor.replace(/_/g, ' ')}
                        </span>
                        <div className="flex items-center gap-2">
                          <Progress 
                            value={(score as number) * 10} 
                            className="w-20 h-2" 
                          />
                          <span className="text-sm font-medium w-8">
                            {(score as number).toFixed(1)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Risk Summary */}
          <Alert className={cn(
            'mt-6',
            overallRisk <= 3 ? 'border-green-200 bg-green-50' :
            overallRisk <= 7 ? 'border-yellow-200 bg-yellow-50' :
            'border-red-200 bg-red-50'
          )}>
            <div className="flex items-start gap-3">
              {overallRisk <= 3 ? (
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              ) : overallRisk <= 7 ? (
                <Info className="h-5 w-5 text-yellow-600 mt-0.5" />
              ) : (
                <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              )}
              <AlertDescription className={cn(
                'text-sm leading-relaxed',
                overallRisk <= 3 ? 'text-green-800' :
                overallRisk <= 7 ? 'text-yellow-800' :
                'text-red-800'
              )}>
                {/* Use AI-generated explanation if available, otherwise fall back to template */}
                {analysis.overall_risk_explanation ? (
                  <div className="space-y-4">
                    {analysis.overall_risk_explanation.split(/[.!?]+/).filter(sentence => sentence.trim()).map((sentence, index) => (
                      <p key={index} className="leading-relaxed text-sm mb-3">
                        {sentence.trim()}.
                      </p>
                    ))}
                  </div>
                ) : analysis.document_explanation ? (
                  <div className="space-y-4">
                    {analysis.document_explanation.split(/[.!?]+/).filter(sentence => sentence.trim()).map((sentence, index) => (
                      <p key={index} className="leading-relaxed text-sm mb-3">
                        {sentence.trim()}.
                      </p>
                    ))}
                  </div>
                ) : (
                  <>
                    {overallRisk <= 3 && (
                      <span>
                        This document appears to be <strong>relatively safe</strong> with minimal risk factors. 
                        Most clauses are standard and favor fair treatment.
                      </span>
                    )}
                    {overallRisk > 3 && overallRisk <= 7 && (
                      <span>
                        This document contains <strong>moderate risk</strong> factors that warrant attention. 
                        Review highlighted clauses carefully and consider negotiation.
                      </span>
                    )}
                    {overallRisk > 7 && (
                      <span>
                        This document contains <strong>significant risk</strong> factors that require immediate attention. 
                        Strong consideration should be given to negotiation or seeking legal counsel.
                      </span>
                    )}
                  </>
                )}
              </AlertDescription>
            </div>
          </Alert>
        </CardContent>
      </Card>

      {/* Detailed Clause Analysis */}
      {showDetails && clauses.length > 0 && (
        <Card className="border-0 shadow-md">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-orange-600" />
                Clause-by-Clause Analysis
              </CardTitle>
              <Badge variant="outline">
                {clauses.length} clause{clauses.length !== 1 ? 's' : ''} analyzed
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {displayedClauses.map((clause, index) => (
                <ClauseRiskItem
                  key={index}
                  clause={clause}
                  index={index}
                />
              ))}
              
              {hasMoreClauses && !showAllClauses && (
                <div className="text-center pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setShowAllClauses(true)}
                    className="w-full"
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    Show {clauses.length - visibleClauses} More Clauses
                  </Button>
                </div>
              )}
              
              {showAllClauses && hasMoreClauses && (
                <div className="text-center pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setShowAllClauses(false)}
                    className="w-full"
                  >
                    <EyeOff className="h-4 w-4 mr-2" />
                    Show Less
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}