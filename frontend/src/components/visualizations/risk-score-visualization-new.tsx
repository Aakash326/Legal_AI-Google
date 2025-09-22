'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import {
  AlertTriangle,
  CheckCircle,
  Shield,
  TrendingUp,
  TrendingDown,
  Minus,
  Info,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { cn, formatRiskLevel, getRiskColor } from '@/lib/utils/format';
import { DocumentAnalysis } from '@/lib/types/api';

interface RiskScoreVisualizationProps {
  analysis: DocumentAnalysis;
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

  const getRiskGaugeColor = (score: number) => {
    if (score >= 7) return 'text-red-500';
    if (score >= 4) return 'text-yellow-500';
    return 'text-green-500';
  };

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
              getRiskGaugeColor(score)
            )}
          />
        </svg>
        
        {/* Score display */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={cn(
              'font-bold',
              size === 'sm' ? 'text-lg' : size === 'md' ? 'text-xl' : 'text-2xl',
              getRiskGaugeColor(score)
            )}>
              {animatedScore.toFixed(1)}
            </div>
            <div className="text-xs text-gray-500">/ 10</div>
          </div>
        </div>
      </div>
      
      {label && (
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
              score >= 7 ? 'border-red-300 text-red-700 bg-red-50' :
              score >= 4 ? 'border-yellow-300 text-yellow-700 bg-yellow-50' :
              'border-green-300 text-green-700 bg-green-50'
            )}
          >
            {score >= 7 ? 'HIGH' : score >= 4 ? 'MEDIUM' : 'LOW'} RISK
          </Badge>
        </div>
      )}
    </div>
  );
}

export function RiskScoreVisualization({
  analysis,
  className,
  showDetails = false,
}: RiskScoreVisualizationProps) {
  const [showRiskBreakdown, setShowRiskBreakdown] = useState(false);

  const overallRisk = analysis.overall_risk_score || 5;
  const riskCategories = analysis.risk_categories || [];
  const keyClauses = analysis.key_clauses || [];

  // Calculate risk distribution from categories
  const riskDistribution = {
    low: riskCategories.filter(c => c.score <= 3).length,
    medium: riskCategories.filter(c => c.score > 3 && c.score <= 7).length,
    high: riskCategories.filter(c => c.score > 7).length,
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Main Risk Score Card */}
      <Card className="border-0 shadow-lg bg-gradient-to-br from-white to-gray-50">
        <CardHeader className="pb-6">
          <CardTitle className="flex items-center gap-2 text-xl">
            <Shield className="h-6 w-6 text-blue-600" />
            Risk Assessment Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col lg:flex-row gap-8 items-center lg:items-start">
            {/* Main Risk Gauge */}
            <div className="flex-shrink-0">
              <RiskGauge
                score={overallRisk}
                size="lg"
                label="Overall Risk Score"
              />
            </div>
            
            {/* Risk Summary */}
            <div className="flex-1 space-y-6">
              {/* Risk Level Description */}
              <div className="text-center lg:text-left">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Risk Level: {overallRisk >= 7 ? 'High' : overallRisk >= 4 ? 'Medium' : 'Low'}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {analysis.overall_risk_explanation || 
                    (overallRisk >= 7 ? 'This document contains several high-risk clauses that require careful attention.' :
                     overallRisk >= 4 ? 'This document has moderate risk factors that should be reviewed.' :
                     'This document appears to have relatively low risk overall.')}
                </p>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-xl border border-green-100">
                  <div className="text-xl font-bold text-green-600 mb-1">
                    {riskDistribution.low}
                  </div>
                  <div className="text-xs text-green-700 font-medium">Low Risk</div>
                </div>
                
                <div className="text-center p-4 bg-yellow-50 rounded-xl border border-yellow-100">
                  <div className="text-xl font-bold text-yellow-600 mb-1">
                    {riskDistribution.medium}
                  </div>
                  <div className="text-xs text-yellow-700 font-medium">Medium Risk</div>
                </div>
                
                <div className="text-center p-4 bg-red-50 rounded-xl border border-red-100">
                  <div className="text-xl font-bold text-red-600 mb-1">
                    {riskDistribution.high}
                  </div>
                  <div className="text-xs text-red-700 font-medium">High Risk</div>
                </div>
              </div>

              {/* Toggle Risk Breakdown */}
              {riskCategories.length > 0 && (
                <Button
                  variant="outline"
                  onClick={() => setShowRiskBreakdown(!showRiskBreakdown)}
                  className="w-full lg:w-auto"
                  size="sm"
                >
                  {showRiskBreakdown ? 'Hide' : 'Show'} Risk Breakdown
                  {showRiskBreakdown ? (
                    <ChevronUp className="h-4 w-4 ml-2" />
                  ) : (
                    <ChevronDown className="h-4 w-4 ml-2" />
                  )}
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Risk Breakdown (Collapsible) */}
      {showRiskBreakdown && riskCategories.length > 0 && (
        <Card className="border-0 shadow-md">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              Detailed Risk Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {riskCategories.map((category, index) => (
                <div
                  key={index}
                  className={cn(
                    'p-4 rounded-lg border-l-4',
                    category.score >= 7
                      ? 'bg-red-50 border-l-red-500 border border-red-100'
                      : category.score >= 4
                      ? 'bg-yellow-50 border-l-yellow-500 border border-yellow-100'
                      : 'bg-green-50 border-l-green-500 border border-green-100'
                  )}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900 text-sm">{category.category}</h4>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold">
                        {category.score.toFixed(1)}
                      </span>
                      <Badge
                        variant="outline"
                        className={cn(
                          'text-xs',
                          category.score >= 7
                            ? 'border-red-300 text-red-700 bg-red-50'
                            : category.score >= 4
                            ? 'border-yellow-300 text-yellow-700 bg-yellow-50'
                            : 'border-green-300 text-green-700 bg-green-50'
                        )}
                      >
                        {category.risk_level.toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {category.description}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Clauses (Only if showDetails is true) */}
      {showDetails && keyClauses.length > 0 && (
        <Card className="border-0 shadow-md">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Key Clauses Requiring Attention
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {keyClauses.slice(0, 3).map((clause, index) => (
                <div
                  key={index}
                  className={cn(
                    'p-4 rounded-lg border-l-4',
                    clause.risk_score >= 7
                      ? 'bg-red-50 border-l-red-500 border border-red-100'
                      : clause.risk_score >= 4
                      ? 'bg-yellow-50 border-l-yellow-500 border border-yellow-100'
                      : 'bg-green-50 border-l-green-500 border border-green-100'
                  )}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className={cn(
                          'w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold text-white',
                          clause.risk_score >= 7
                            ? 'bg-red-500'
                            : clause.risk_score >= 4
                            ? 'bg-yellow-500'
                            : 'bg-green-500'
                        )}>
                          {index + 1}
                        </div>
                        <h4 className="font-medium text-gray-900 text-sm">
                          {clause.type || `Clause ${index + 1}`}
                        </h4>
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-3 leading-relaxed">
                        {clause.explanation}
                      </p>
                      
                      {clause.recommendations && clause.recommendations.length > 0 && (
                        <div className="text-xs text-gray-500">
                          <strong>Recommendation:</strong> {clause.recommendations[0]}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex-shrink-0">
                      <RiskGauge
                        score={clause.risk_score}
                        size="sm"
                        label=""
                      />
                    </div>
                  </div>
                </div>
              ))}
              
              {keyClauses.length > 3 && (
                <div className="text-center pt-2">
                  <span className="text-sm text-gray-500">
                    and {keyClauses.length - 3} more clauses...
                  </span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
