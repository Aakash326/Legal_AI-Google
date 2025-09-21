import asyncio
import time
import uuid
from typing import Dict, Any, List
import logging
from pathlib import Path

from models.document import ProcessingStatus, ProcessedDocument, DocumentType, LegalClause, DocumentSummary
from models.analysis import DocumentAnalysis, QueryResult, RiskCategory, ProcessingStats
from agents.document_processor import DocumentProcessorAgent
from agents.legal_analyzer import LegalAnalyzerAgent
from agents.risk_assessor import RiskAssessorAgent
from agents.query_handler import QueryHandlerAgent
from services.modern_gemini_service import get_modern_gemini_service

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    def __init__(self):
        self.document_processor = DocumentProcessorAgent()
        self.legal_analyzer = LegalAnalyzerAgent()
        self.risk_assessor = RiskAssessorAgent()
        self.query_handler = QueryHandlerAgent()
        self.gemini_service = get_modern_gemini_service()
        
        # Store processed documents and analysis results
        self.processed_documents: Dict[str, ProcessedDocument] = {}
        self.analysis_cache: Dict[str, DocumentAnalysis] = {}
    
    async def process_document(self, file_path: str, document_id: str, status_tracker: Dict[str, ProcessingStatus]) -> DocumentAnalysis:
        """Main document processing workflow"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting document processing for {document_id}")
            
            # Step 1: Document Processing (Text Extraction)
            status_tracker[document_id].current_step = "Extracting text from document"
            status_tracker[document_id].progress = 20
            
            processed_doc = await self.document_processor.process_document(file_path, document_id)
            self.processed_documents[document_id] = processed_doc
            
            logger.info(f"Text extraction completed for {document_id}. Word count: {processed_doc.word_count}")
            
            # Step 2: Legal Analysis (Clause Identification)
            status_tracker[document_id].current_step = "Analyzing legal clauses"
            status_tracker[document_id].progress = 40
            
            legal_clauses = await self.legal_analyzer.analyze_document(processed_doc)
            
            logger.info(f"Legal analysis completed for {document_id}. Found {len(legal_clauses)} clauses")
            
            # Step 3: Risk Assessment
            status_tracker[document_id].current_step = "Assessing risk levels"
            status_tracker[document_id].progress = 60
            
            risk_assessment = await self.risk_assessor.assess_document_risk(legal_clauses)
            
            logger.info(f"Risk assessment completed for {document_id}. Overall risk: {risk_assessment.overall_risk}")
            
            # Step 4: Generate Document Summary
            status_tracker[document_id].current_step = "Generating document summary"
            status_tracker[document_id].progress = 80
            
            document_summary = await self._generate_document_summary(processed_doc)
            
            # Step 5: Generate Comprehensive Explanation
            status_tracker[document_id].current_step = "Creating comprehensive explanation"
            status_tracker[document_id].progress = 85
            
            explanation_data = await self._generate_comprehensive_explanation(processed_doc, legal_clauses)
            
            # Step 6: Compile Results
            status_tracker[document_id].current_step = "Compiling analysis results"
            status_tracker[document_id].progress = 90
            
            processing_time = time.time() - start_time
            
            # Step 7: Generate AI-powered recommendations
            status_tracker[document_id].current_step = "Generating personalized recommendations"
            status_tracker[document_id].progress = 95
            
            ai_recommendations = await self._generate_ai_recommendations(
                legal_clauses, risk_assessment, processed_doc.document_type.value
            )
            
            # Create final analysis result
            analysis_result = DocumentAnalysis(
                document_id=document_id,
                document_type=processed_doc.document_type,
                overall_risk_score=risk_assessment.overall_risk,
                document_summary=document_summary,
                key_clauses=legal_clauses,
                risk_categories=await self._create_enhanced_risk_categories(legal_clauses, processed_doc.document_type.value),
                recommendations=ai_recommendations,
                red_flags=await self._identify_ai_red_flags(legal_clauses),
                document_explanation=explanation_data.get("document_explanation", ""),
                key_provisions_explained=explanation_data.get("key_provisions", []),
                legal_implications=explanation_data.get("legal_implications", []),
                practical_impact=explanation_data.get("practical_impact", ""),
                clause_by_clause_summary=explanation_data.get("clause_summaries", []),
                overall_risk_explanation=explanation_data.get("overall_risk_explanation", ""),
                processing_time=processing_time
            )
            
            # Cache the result
            self.analysis_cache[document_id] = analysis_result
            
            logger.info(f"Document processing completed for {document_id} in {processing_time:.2f} seconds")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Document processing failed for {document_id}: {str(e)}")
            raise
    
    async def handle_user_query(self, document_id: str, query: str) -> QueryResult:
        """Handle user queries about processed documents"""
        try:
            if document_id not in self.analysis_cache:
                raise ValueError(f"Document {document_id} not found or not processed")
            
            analysis = self.analysis_cache[document_id]
            processed_doc = self.processed_documents.get(document_id)
            
            if not processed_doc:
                raise ValueError(f"Processed document {document_id} not found")
            
            # Use query handler agent
            return await self.query_handler.handle_query(
                query=query,
                document_id=document_id,
                document_text=processed_doc.extracted_text,
                legal_clauses=analysis.key_clauses
            )
            
        except Exception as e:
            logger.error(f"Query handling failed for {document_id}: {str(e)}")
            raise
    
    async def get_processing_status(self, document_id: str) -> ProcessingStatus:
        """Get current processing status"""
        # This would be implemented with a proper status tracking system
        # For now, return a basic status
        return ProcessingStatus(
            document_id=document_id,
            status="unknown",
            progress=0,
            current_step="Status not available"
        )
    
    async def _generate_document_summary(self, processed_doc: ProcessedDocument) -> DocumentSummary:
        """Generate a summary of the document using Gemini"""
        try:
            summary_data = await self.gemini_service.extract_document_summary(processed_doc.extracted_text)
            
            return DocumentSummary(
                parties=summary_data.get("parties", []),
                key_dates=summary_data.get("key_dates", []),
                key_amounts=summary_data.get("key_amounts", []),
                duration=summary_data.get("duration"),
                main_purpose=summary_data.get("main_purpose", ""),
                jurisdiction=summary_data.get("jurisdiction")
            )
        except Exception as e:
            logger.error(f"Failed to generate document summary: {str(e)}")
            raise
    
    def _create_risk_categories(self, clauses: List[LegalClause]) -> List[RiskCategory]:
        """Create risk categories based on analyzed clauses"""
        category_data = {}
        
        for clause in clauses:
            category = clause.clause_type.value if clause.clause_type else "other"
            if category not in category_data:
                category_data[category] = {
                    "scores": [],
                    "count": 0,
                    "high_risk_count": 0
                }
            
            category_data[category]["scores"].append(clause.risk_score)
            category_data[category]["count"] += 1
            if clause.risk_score >= 7:
                category_data[category]["high_risk_count"] += 1
        
        risk_categories = []
        for category, data in category_data.items():
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 5
            
            description = self._get_category_description(category, data["high_risk_count"], data["count"])
            
            risk_categories.append(RiskCategory(
                category=category.replace("_", " ").title(),
                score=int(round(avg_score)),
                description=description,
                clauses_count=data["count"]
            ))
        
        return risk_categories
    
    def _get_category_description(self, category: str, high_risk_count: int, total_count: int) -> str:
        """Get description for risk category"""
        risk_descriptions = {
            "payment_terms": "Financial obligations and payment requirements",
            "termination": "Conditions and procedures for ending the agreement",
            "liability": "Responsibility and damage provisions",
            "confidentiality": "Information protection and non-disclosure requirements",
            "intellectual_property": "Rights and ownership of intellectual assets",
            "dispute_resolution": "Methods for resolving conflicts and disagreements",
            "governing_law": "Legal jurisdiction and applicable laws",
            "amendment": "Procedures for modifying the agreement",
            "other": "Other legal provisions and general terms"
        }
        
        base_description = risk_descriptions.get(category, "Legal provisions")
        
        if high_risk_count > 0:
            return f"{base_description}. Contains {high_risk_count} high-risk provision(s)."
        elif total_count > 0:
            return f"{base_description}. Generally standard terms."
        else:
            return base_description
    
    async def _generate_ai_recommendations(self, clauses: List[LegalClause], risk_assessment, document_type: str) -> List[str]:
        """Generate AI-powered contextual recommendations"""
        try:
            # Prepare clause summary for AI analysis
            high_risk_clauses = [c for c in clauses if c.risk_score >= 7]
            medium_risk_clauses = [c for c in clauses if 4 <= c.risk_score < 7]
            
            clause_summary = {
                "total_clauses": len(clauses),
                "high_risk_count": len(high_risk_clauses),
                "medium_risk_count": len(medium_risk_clauses),
                "overall_risk": risk_assessment.overall_risk,
                "document_type": document_type,
                "high_risk_types": [c.clause_type.value if c.clause_type else "other" for c in high_risk_clauses],
                "key_concerns": []
            }
            
            # Collect key concerns from high-risk clauses
            for clause in high_risk_clauses[:5]:  # Top 5 high-risk clauses
                concerns = getattr(clause, 'concerns', [])
                if concerns:
                    clause_summary["key_concerns"].extend(concerns[:2])  # Top 2 concerns per clause
            
            # Generate AI recommendations
            recommendations_data = await self.gemini_service.generate_risk_recommendations(
                document_type, clause_summary
            )
            
            if recommendations_data and isinstance(recommendations_data, dict):
                ai_recommendations = recommendations_data.get("recommendations", [])
                if isinstance(ai_recommendations, list):
                    return ai_recommendations[:8]  # Limit to 8 AI recommendations
            
            logger.warning("AI recommendation generation failed, falling back to template-based")
            return self._generate_fallback_recommendations(clauses, risk_assessment)
            
        except Exception as e:
            logger.error(f"Failed to generate AI recommendations: {str(e)}")
            return self._generate_fallback_recommendations(clauses, risk_assessment)
    
    def _generate_fallback_recommendations(self, clauses: List[LegalClause], risk_assessment) -> List[str]:
        """Generate fallback template-based recommendations"""
        recommendations = []
        
        # High-risk clauses recommendations
        high_risk_clauses = [c for c in clauses if c.risk_score >= 7]
        if high_risk_clauses:
            recommendations.append(
                f"Review {len(high_risk_clauses)} high-risk clause(s) carefully before signing"
            )
        
        # Category-specific recommendations
        clause_types = set(c.clause_type.value if c.clause_type else "other" for c in clauses)
        
        if "payment_terms" in clause_types:
            payment_clauses = [c for c in clauses if (c.clause_type.value if c.clause_type else "other") == "payment_terms"]
            high_risk_payment = [c for c in payment_clauses if c.risk_score >= 7]
            if high_risk_payment:
                recommendations.append("Carefully review payment terms for potential hidden fees or penalties")
        
        if "termination" in clause_types:
            termination_clauses = [c for c in clauses if (c.clause_type.value if c.clause_type else "other") == "termination"]
            high_risk_termination = [c for c in termination_clauses if c.risk_score >= 7]
            if high_risk_termination:
                recommendations.append("Pay special attention to termination conditions and penalties")
        
        if "liability" in clause_types:
            liability_clauses = [c for c in clauses if (c.clause_type.value if c.clause_type else "other") == "liability"]
            high_risk_liability = [c for c in liability_clauses if c.risk_score >= 7]
            if high_risk_liability:
                recommendations.append("Consider the extent of liability and potential financial exposure")
        
        # Overall risk recommendations
        if risk_assessment.overall_risk >= 7:
            recommendations.append("Overall high risk - strongly recommend legal review before signing")
        elif risk_assessment.overall_risk >= 4:
            recommendations.append("Moderate risk - consider professional review of key terms")
        
        # Add clause-specific recommendations
        for clause in clauses:
            clause_recommendations = getattr(clause, 'recommendations', [])
            if clause_recommendations:
                recommendations.extend(clause_recommendations[:2])  # Limit to top 2 per clause
        
        # Remove duplicates and limit total
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:10]  # Limit to 10 recommendations
    
    def _generate_recommendations(self, clauses: List[LegalClause], risk_assessment) -> List[str]:
        """Legacy method - kept for backward compatibility"""
        return self._generate_fallback_recommendations(clauses, risk_assessment)
    
    async def _create_enhanced_risk_categories(self, clauses: List[LegalClause], document_type: str) -> List[RiskCategory]:
        """Create enhanced risk categories with AI-generated descriptions"""
        try:
            # Get basic risk categories first
            basic_categories = self._create_risk_categories(clauses)
            
            # Enhance each category with AI-generated descriptions
            enhanced_categories = []
            for category in basic_categories:
                try:
                    # Get clauses for this category
                    category_clauses = [c for c in clauses if (c.clause_type.value if c.clause_type else "other").replace("_", " ").title() == category.category]
                    
                    # Generate AI description for this category
                    ai_description = await self._generate_category_description(
                        category.category, category_clauses, document_type
                    )
                    
                    enhanced_category = RiskCategory(
                        category=category.category,
                        score=category.score,
                        description=ai_description if ai_description else category.description,
                        clauses_count=category.clauses_count
                    )
                    enhanced_categories.append(enhanced_category)
                    
                except Exception as e:
                    logger.warning(f"Failed to enhance category {category.category}: {e}")
                    enhanced_categories.append(category)  # Fallback to basic category
            
            return enhanced_categories
            
        except Exception as e:
            logger.error(f"Failed to create enhanced risk categories: {e}")
            return self._create_risk_categories(clauses)  # Fallback to basic categories
    
    async def _generate_category_description(self, category_name: str, category_clauses: List[LegalClause], document_type: str) -> str:
        """Generate AI-powered description for a risk category"""
        try:
            if not category_clauses:
                return self._get_category_description(category_name.lower().replace(" ", "_"), 0, 0)
            
            # Prepare data for AI generation
            high_risk_count = len([c for c in category_clauses if c.risk_score >= 7])
            category_data = {
                "category_name": category_name,
                "total_count": len(category_clauses),
                "high_risk_count": high_risk_count,
                "average_risk": sum(c.risk_score for c in category_clauses) / len(category_clauses),
                "document_type": document_type,
                "sample_concerns": []
            }
            
            # Get sample concerns from high-risk clauses
            for clause in category_clauses[:3]:  # Top 3 clauses
                concerns = getattr(clause, 'concerns', [])
                if concerns:
                    category_data["sample_concerns"].extend(concerns[:2])
            
            # Generate AI description
            description_data = await self.gemini_service.generate_category_description(category_data)
            
            if description_data and isinstance(description_data, dict):
                ai_description = description_data.get("description", "")
                if ai_description and len(ai_description.strip()) > 10:
                    return ai_description.strip()
            
            # Fallback to template-based description
            return self._get_category_description(category_name.lower().replace(" ", "_"), high_risk_count, len(category_clauses))
            
        except Exception as e:
            logger.warning(f"Failed to generate AI description for {category_name}: {e}")
            high_risk_count = len([c for c in category_clauses if c.risk_score >= 7])
            return self._get_category_description(category_name.lower().replace(" ", "_"), high_risk_count, len(category_clauses))
    
    async def _identify_ai_red_flags(self, clauses: List[LegalClause]) -> List[str]:
        """Identify red flags using AI analysis"""
        try:
            # Get critical clauses (high risk)
            critical_clauses = [c for c in clauses if c.risk_score >= 8]
            
            if not critical_clauses:
                return self._identify_red_flags(clauses)  # Fallback to template-based
            
            # Prepare data for AI analysis
            red_flag_data = {
                "total_clauses": len(clauses),
                "critical_clause_count": len(critical_clauses),
                "critical_clauses": []
            }
            
            # Add critical clause details for AI analysis
            for clause in critical_clauses[:5]:  # Top 5 critical clauses
                clause_data = {
                    "type": clause.clause_type.value if clause.clause_type else "other",
                    "risk_score": clause.risk_score,
                    "risk_explanation": clause.risk_explanation[:200],  # Truncate for token efficiency
                    "concerns": getattr(clause, 'concerns', [])[:3]  # Top 3 concerns
                }
                red_flag_data["critical_clauses"].append(clause_data)
            
            # Generate AI red flags
            flags_data = await self.gemini_service.generate_red_flags(red_flag_data)
            
            if flags_data and isinstance(flags_data, dict):
                ai_red_flags = flags_data.get("red_flags", [])
                if isinstance(ai_red_flags, list) and ai_red_flags:
                    return ai_red_flags[:6]  # Limit to 6 AI red flags
            
            # Fallback to template-based red flags
            return self._identify_red_flags(clauses)
            
        except Exception as e:
            logger.error(f"Failed to generate AI red flags: {e}")
            return self._identify_red_flags(clauses)
    
    def _identify_red_flags(self, clauses: List[LegalClause]) -> List[str]:
        """Identify critical red flags in the document (template-based fallback)"""
        red_flags = []
        
        # Very high risk clauses (9-10)
        critical_clauses = [c for c in clauses if c.risk_score >= 9]
        for clause in critical_clauses:
            clause_type_display = (clause.clause_type.value if clause.clause_type else "other").replace('_', ' ')
            red_flags.append(f"Critical risk in {clause_type_display}: {clause.risk_explanation[:100]}...")
        
        # Specific red flag patterns
        for clause in clauses:
            text_lower = clause.original_text.lower()
            
            # Financial red flags
            if any(term in text_lower for term in ['unlimited liability', 'unlimited damages', 'no cap on liability']):
                red_flags.append("Unlimited liability exposure detected")
            
            # Termination red flags
            if any(term in text_lower for term in ['terminate at will', 'terminate without cause', 'immediate termination']):
                red_flags.append("One-sided termination rights detected")
            
            # Payment red flags
            if any(term in text_lower for term in ['non-refundable', 'forfeiture', 'penalty fee']):
                red_flags.append("Non-refundable fees or penalties detected")
        
        # Remove duplicates
        return list(dict.fromkeys(red_flags))[:5]  # Limit to 5 red flags
    
    def get_analysis_result(self, document_id: str) -> DocumentAnalysis:
        """Get cached analysis result"""
        return self.analysis_cache.get(document_id)
    
    def get_processed_document(self, document_id: str) -> ProcessedDocument:
        """Get processed document"""
        return self.processed_documents.get(document_id)
    
    async def _generate_comprehensive_explanation(self, processed_doc: ProcessedDocument, clauses: List[LegalClause]) -> Dict[str, Any]:
        """Generate comprehensive explanation of the document"""
        try:
            # Convert clauses to simple dict format for the explanation service
            clause_data = []
            for i, clause in enumerate(clauses):
                try:
                    # Safely get clause type
                    clause_type = getattr(clause, 'clause_type', None)
                    clause_type_value = clause_type.value if clause_type else "other"
                    
                    clause_dict = {
                        "clause_type": clause_type_value,
                        "simplified_text": getattr(clause, 'simplified_text', ''),
                        "risk_score": getattr(clause, 'risk_score', 5),
                        "concerns": getattr(clause, 'concerns', []),
                        "obligations": getattr(clause, 'obligations', [])
                    }
                    clause_data.append(clause_dict)
                except Exception as clause_error:
                    logger.error(f"Error processing clause {i}: {clause_error}")
                    # Skip problematic clause and continue
                    continue
            
            # Safely get document type
            doc_type = processed_doc.document_type.value if processed_doc.document_type else "other"
            
            explanation = await self.gemini_service.generate_comprehensive_explanation(
                processed_doc.extracted_text,
                doc_type,
                clause_data
            )
            
            logger.info(f"Comprehensive explanation generated for {processed_doc.document_id}")
            return explanation
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive explanation: {str(e)}")
            # Return a basic explanation instead of failing completely
            return {
                "document_explanation": "Unable to generate detailed explanation due to processing error",
                "key_provisions": ["Please review the document manually"],
                "legal_implications": ["Consult with a legal professional"],
                "practical_impact": "Impact assessment unavailable",
                "clause_summaries": ["Clause analysis unavailable"],
                "overall_risk_explanation": "Risk assessment unavailable due to processing error"
            }
