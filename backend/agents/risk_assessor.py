import asyncio
import time
from typing import List, Dict, Any
import logging

from models.document import LegalClause, ClauseType
from models.analysis import RiskAssessmentResult
from services.gemini_service import get_gemini_service

logger = logging.getLogger(__name__)

class RiskAssessorAgent:
    def __init__(self):
        self.gemini_service = get_gemini_service()
        
        # Risk weights for different clause types
        self.clause_weights = {
            ClauseType.LIABILITY: 1.5,
            ClauseType.INDEMNIFICATION: 1.4,
            ClauseType.PAYMENT_TERMS: 1.3,
            ClauseType.TERMINATION: 1.2,
            ClauseType.INTELLECTUAL_PROPERTY: 1.1,
            ClauseType.CONFIDENTIALITY: 1.0,
            ClauseType.DISPUTE_RESOLUTION: 0.9,
            ClauseType.GOVERNING_LAW: 0.8,
            ClauseType.AMENDMENT: 0.7,
            ClauseType.SEVERABILITY: 0.6,
            ClauseType.PRIVACY: 1.0,
            ClauseType.FORCE_MAJEURE: 0.8,
            ClauseType.OTHER: 0.5
        }
    
    async def assess_document_risk(self, clauses: List[LegalClause]) -> RiskAssessmentResult:
        """Assess overall risk level of the document"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting risk assessment for {len(clauses)} clauses")
            
            if not clauses:
                return RiskAssessmentResult(
                    document_id="unknown",
                    overall_risk=5.0,
                    high_risk_clauses=[],
                    medium_risk_clauses=[],
                    low_risk_clauses=[],
                    risk_distribution={},
                    recommendations=["No clauses found for risk assessment"]
                )
            
            # Step 1: Enhance individual clause risk assessments
            enhanced_clauses = await self._enhance_clause_risk_assessments(clauses)
            
            # Step 2: Calculate overall document risk
            overall_risk = self._calculate_overall_risk(enhanced_clauses)
            
            # Step 3: Categorize clauses by risk level
            risk_categories = self._categorize_clauses_by_risk(enhanced_clauses)
            
            # Step 4: Analyze risk distribution
            risk_distribution = self._analyze_risk_distribution(enhanced_clauses)
            
            # Step 5: Generate risk-based recommendations
            recommendations = self._generate_risk_recommendations(enhanced_clauses, overall_risk)
            
            processing_time = time.time() - start_time
            
            # Get document ID from first clause
            document_id = enhanced_clauses[0].clause_id.split('_')[0] if enhanced_clauses else "unknown"
            
            result = RiskAssessmentResult(
                document_id=document_id,
                overall_risk=overall_risk,
                high_risk_clauses=risk_categories["high"],
                medium_risk_clauses=risk_categories["medium"],
                low_risk_clauses=risk_categories["low"],
                risk_distribution=risk_distribution,
                recommendations=recommendations
            )
            
            logger.info(
                f"Risk assessment completed. "
                f"Overall risk: {overall_risk:.2f}, "
                f"High risk clauses: {len(risk_categories['high'])}, "
                f"Time: {processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            raise
    
    async def _enhance_clause_risk_assessments(self, clauses: List[LegalClause]) -> List[LegalClause]:
        """Enhance risk assessments for clauses that need more detailed analysis"""
        enhanced_clauses = []
        
        # Process high-priority clauses for enhanced assessment
        high_priority_types = {
            ClauseType.LIABILITY,
            ClauseType.INDEMNIFICATION,
            ClauseType.PAYMENT_TERMS,
            ClauseType.TERMINATION
        }
        
        for clause in clauses:
            enhanced_clause = clause.copy()
            
            # Enhanced assessment for high-priority clause types
            if clause.clause_type in high_priority_types and clause.risk_score >= 6:
                try:
                    enhanced_assessment = await self.gemini_service.assess_risk(clause.original_text)
                    
                    # Update risk score if enhancement provides better assessment
                    enhanced_risk = enhanced_assessment.get("risk_score", clause.risk_score)
                    if abs(enhanced_risk - clause.risk_score) <= 2:  # Reasonable range
                        enhanced_clause.risk_score = enhanced_risk
                        
                        # Update risk explanation with enhanced analysis
                        enhanced_explanation = enhanced_assessment.get("risk_explanation", "")
                        if enhanced_explanation:
                            enhanced_clause.risk_explanation = enhanced_explanation
                        
                        # Add any additional recommendations
                        enhanced_recommendations = enhanced_assessment.get("recommendations", [])
                        if enhanced_recommendations:
                            enhanced_clause.recommendations.extend(enhanced_recommendations[:2])
                    
                except Exception as e:
                    logger.warning(f"Enhanced risk assessment failed for clause {clause.clause_id}: {str(e)}")
            
            enhanced_clauses.append(enhanced_clause)
        
        return enhanced_clauses
    
    def _calculate_overall_risk(self, clauses: List[LegalClause]) -> float:
        """Calculate weighted overall risk score for the document"""
        if not clauses:
            return 5.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for clause in clauses:
            weight = self.clause_weights.get(clause.clause_type, 1.0)
            
            # Additional weight for high-risk clauses
            if clause.risk_score >= 8:
                weight *= 1.3
            elif clause.risk_score >= 6:
                weight *= 1.1
            
            total_weighted_score += clause.risk_score * weight
            total_weight += weight
        
        weighted_average = total_weighted_score / total_weight
        
        # Apply document-level risk factors
        risk_adjustments = self._calculate_document_risk_adjustments(clauses)
        
        final_risk = weighted_average + risk_adjustments
        
        # Ensure risk score is within valid range
        return max(1.0, min(10.0, final_risk))
    
    def _calculate_document_risk_adjustments(self, clauses: List[LegalClause]) -> float:
        """Calculate risk adjustments based on document-level factors"""
        adjustment = 0.0
        
        # High number of high-risk clauses
        high_risk_count = len([c for c in clauses if c.risk_score >= 7])
        high_risk_ratio = high_risk_count / len(clauses)
        
        if high_risk_ratio > 0.3:  # More than 30% high-risk clauses
            adjustment += 0.5
        elif high_risk_ratio > 0.15:  # More than 15% high-risk clauses
            adjustment += 0.2
        
        # Critical clause types present
        critical_types = {ClauseType.LIABILITY, ClauseType.INDEMNIFICATION}
        critical_clauses = [c for c in clauses if c.clause_type in critical_types]
        
        for clause in critical_clauses:
            if clause.risk_score >= 8:
                adjustment += 0.3  # Very high-risk critical clause
            elif clause.risk_score >= 6:
                adjustment += 0.1  # Medium-risk critical clause
        
        # Lack of protective clauses
        protective_types = {ClauseType.SEVERABILITY, ClauseType.FORCE_MAJEURE}
        has_protective = any(c.clause_type in protective_types for c in clauses)
        
        if not has_protective and len(clauses) > 5:
            adjustment += 0.2  # Missing protective clauses in substantial document
        
        return adjustment
    
    def _categorize_clauses_by_risk(self, clauses: List[LegalClause]) -> Dict[str, List[str]]:
        """Categorize clauses by risk level"""
        categories = {
            "high": [],    # Risk score 7-10
            "medium": [],  # Risk score 4-6
            "low": []      # Risk score 1-3
        }
        
        for clause in clauses:
            if clause.risk_score >= 7:
                categories["high"].append(clause.clause_id)
            elif clause.risk_score >= 4:
                categories["medium"].append(clause.clause_id)
            else:
                categories["low"].append(clause.clause_id)
        
        return categories
    
    def _analyze_risk_distribution(self, clauses: List[LegalClause]) -> Dict[str, int]:
        """Analyze the distribution of risk scores"""
        distribution = {}
        
        for clause in clauses:
            score = clause.risk_score
            distribution[str(score)] = distribution.get(str(score), 0) + 1
        
        # Add summary categories
        distribution["total_clauses"] = len(clauses)
        distribution["high_risk_count"] = len([c for c in clauses if c.risk_score >= 7])
        distribution["medium_risk_count"] = len([c for c in clauses if 4 <= c.risk_score <= 6])
        distribution["low_risk_count"] = len([c for c in clauses if c.risk_score <= 3])
        
        return distribution
    
    def _generate_risk_recommendations(self, clauses: List[LegalClause], overall_risk: float) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        # Overall risk level recommendations
        if overall_risk >= 8:
            recommendations.append("CRITICAL: This document poses significant risks. Professional legal review is strongly recommended before signing.")
        elif overall_risk >= 6:
            recommendations.append("HIGH RISK: Consider having a lawyer review this document, especially the high-risk clauses.")
        elif overall_risk >= 4:
            recommendations.append("MODERATE RISK: Review highlighted clauses carefully and consider seeking advice on unclear terms.")
        else:
            recommendations.append("LOW RISK: Document appears to have reasonable terms, but still review carefully.")
        
        # Clause-specific recommendations
        high_risk_clauses = [c for c in clauses if c.risk_score >= 7]
        
        if high_risk_clauses:
            liability_clauses = [c for c in high_risk_clauses if c.clause_type == ClauseType.LIABILITY]
            if liability_clauses:
                recommendations.append("Review liability clauses carefully - they may expose you to significant financial risk.")
            
            payment_clauses = [c for c in high_risk_clauses if c.clause_type == ClauseType.PAYMENT_TERMS]
            if payment_clauses:
                recommendations.append("Pay attention to payment terms - there may be hidden fees or penalties.")
            
            termination_clauses = [c for c in high_risk_clauses if c.clause_type == ClauseType.TERMINATION]
            if termination_clauses:
                recommendations.append("Termination clauses may be unfavorable - understand exit conditions and penalties.")
        
        # Document type specific recommendations
        clause_types = set(c.clause_type for c in clauses)
        
        if ClauseType.INDEMNIFICATION in clause_types:
            indemnification_clauses = [c for c in clauses if c.clause_type == ClauseType.INDEMNIFICATION]
            high_risk_indemnification = [c for c in indemnification_clauses if c.risk_score >= 7]
            if high_risk_indemnification:
                recommendations.append("Indemnification clauses may require you to cover legal costs - understand your potential exposure.")
        
        # Missing important clauses
        important_types = {ClauseType.TERMINATION, ClauseType.DISPUTE_RESOLUTION}
        missing_important = important_types - clause_types
        
        if missing_important and len(clauses) > 3:
            missing_names = [t.value.replace('_', ' ').title() for t in missing_important]
            recommendations.append(f"Consider adding clauses for: {', '.join(missing_names)}.")
        
        # Limit to most important recommendations
        return recommendations[:8]
    
    def analyze_clause_interactions(self, clauses: List[LegalClause]) -> Dict[str, Any]:
        """Analyze how clauses interact and potentially compound risks"""
        interactions = {
            "risk_amplification": [],
            "conflicting_terms": [],
            "protective_combinations": []
        }
        
        # Look for risk amplification patterns
        liability_clauses = [c for c in clauses if c.clause_type == ClauseType.LIABILITY]
        indemnification_clauses = [c for c in clauses if c.clause_type == ClauseType.INDEMNIFICATION]
        
        if liability_clauses and indemnification_clauses:
            high_risk_liability = [c for c in liability_clauses if c.risk_score >= 7]
            high_risk_indemnification = [c for c in indemnification_clauses if c.risk_score >= 7]
            
            if high_risk_liability and high_risk_indemnification:
                interactions["risk_amplification"].append({
                    "description": "High-risk liability and indemnification clauses may compound financial exposure",
                    "involved_clauses": [c.clause_id for c in high_risk_liability + high_risk_indemnification]
                })
        
        # Look for protective combinations
        severability_clauses = [c for c in clauses if c.clause_type == ClauseType.SEVERABILITY]
        force_majeure_clauses = [c for c in clauses if c.clause_type == ClauseType.FORCE_MAJEURE]
        
        if severability_clauses and force_majeure_clauses:
            interactions["protective_combinations"].append({
                "description": "Document includes protective clauses for unexpected situations",
                "involved_clauses": [c.clause_id for c in severability_clauses + force_majeure_clauses]
            })
        
        return interactions
    
    def get_risk_summary(self, assessment_result: RiskAssessmentResult) -> Dict[str, Any]:
        """Get a summary of the risk assessment"""
        total_clauses = len(assessment_result.high_risk_clauses) + len(assessment_result.medium_risk_clauses) + len(assessment_result.low_risk_clauses)
        
        return {
            "overall_risk_score": assessment_result.overall_risk,
            "risk_level": self._get_risk_level_description(assessment_result.overall_risk),
            "total_clauses_analyzed": total_clauses,
            "high_risk_clause_count": len(assessment_result.high_risk_clauses),
            "medium_risk_clause_count": len(assessment_result.medium_risk_clauses),
            "low_risk_clause_count": len(assessment_result.low_risk_clauses),
            "risk_percentage": {
                "high": round(len(assessment_result.high_risk_clauses) / total_clauses * 100, 1) if total_clauses > 0 else 0,
                "medium": round(len(assessment_result.medium_risk_clauses) / total_clauses * 100, 1) if total_clauses > 0 else 0,
                "low": round(len(assessment_result.low_risk_clauses) / total_clauses * 100, 1) if total_clauses > 0 else 0
            },
            "top_recommendations": assessment_result.recommendations[:3]
        }
    
    def _get_risk_level_description(self, risk_score: float) -> str:
        """Get textual description of risk level"""
        if risk_score >= 8:
            return "Critical Risk"
        elif risk_score >= 6:
            return "High Risk"
        elif risk_score >= 4:
            return "Moderate Risk"
        else:
            return "Low Risk"