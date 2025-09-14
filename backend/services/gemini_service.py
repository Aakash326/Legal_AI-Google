import google.generativeai as genai
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from models.document import ClauseType, DocumentType
from models.analysis import RiskAssessmentResult

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Legal analysis prompts
        self.legal_analysis_prompt = """
Analyze this legal clause and provide:
1. Clause type from: payment_terms, termination, liability, privacy, indemnification, dispute_resolution, intellectual_property, confidentiality, force_majeure, governing_law, amendment, severability, other
2. Key obligations for each party
3. Risk level (1-10 scale) with explanation
4. Plain language explanation
5. Potential concerns or red flags
6. Key terms extracted
7. Specific recommendations

Clause: {clause_text}

Response format: JSON with keys: clause_type, obligations, risk_score, risk_explanation, simplified_text, concerns, key_terms, recommendations
"""
        
        self.risk_assessment_prompt = """
Assess the risk level of this legal clause on a scale of 1-10:
1-3: Low risk (standard, fair terms)
4-6: Medium risk (some concerns, review recommended)  
7-10: High risk (unfavorable, potentially problematic)

Consider: favorability, clarity, potential costs, enforceability, one-sidedness

Clause: {clause_text}

Response format: JSON with keys: risk_score, risk_explanation, red_flags, recommendations
"""
        
        self.document_classification_prompt = """
Classify this document type from: rental_agreement, employment_contract, loan_agreement, terms_of_service, privacy_policy, purchase_agreement, other

Document excerpt: {document_text}

Response format: JSON with keys: document_type, confidence, reasoning
"""
        
        self.query_prompt = """
Answer the user's question about this legal document based on the provided context.

Document Context: {document_context}

Relevant Clauses: {relevant_clauses}

User Question: {query}

Provide a clear, accurate answer in plain language. If the information isn't in the document, say so.

Response format: JSON with keys: answer, confidence, sources_used
"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _make_request(self, prompt: str) -> str:
        """Make a request to Gemini API with retry logic"""
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    async def analyze_legal_text(self, clause_text: str) -> Dict[str, Any]:
        """Analyze a legal clause using Gemini"""
        prompt = self.legal_analysis_prompt.format(clause_text=clause_text)
        
        try:
            response_text = await self._make_request(prompt)
            
            # Try to parse JSON response
            try:
                result = json.loads(response_text)
                # Validate and clean the response
                return self._validate_legal_analysis(result)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a basic response
                return {
                    "clause_type": "other",
                    "obligations": [],
                    "risk_score": 5,
                    "risk_explanation": "Unable to parse detailed analysis",
                    "simplified_text": response_text[:500],
                    "concerns": [],
                    "key_terms": [],
                    "recommendations": ["Review this clause with a legal professional"]
                }
        except Exception as e:
            logger.error(f"Legal analysis error: {str(e)}")
            return {
                "clause_type": "other",
                "obligations": [],
                "risk_score": 5,
                "risk_explanation": f"Analysis failed: {str(e)}",
                "simplified_text": "Analysis unavailable",
                "concerns": ["Unable to analyze this clause"],
                "key_terms": [],
                "recommendations": ["Review this clause with a legal professional"]
            }
    
    async def classify_clause(self, clause_text: str) -> ClauseType:
        """Classify the type of legal clause"""
        analysis = await self.analyze_legal_text(clause_text)
        clause_type_str = analysis.get("clause_type", "other")
        
        try:
            return ClauseType(clause_type_str)
        except ValueError:
            return ClauseType.OTHER
    
    async def assess_risk(self, clause_text: str) -> Dict[str, Any]:
        """Assess risk level of a clause"""
        prompt = self.risk_assessment_prompt.format(clause_text=clause_text)
        
        try:
            response_text = await self._make_request(prompt)
            result = json.loads(response_text)
            return self._validate_risk_assessment(result)
        except Exception as e:
            logger.error(f"Risk assessment error: {str(e)}")
            return {
                "risk_score": 5,
                "risk_explanation": f"Risk assessment failed: {str(e)}",
                "red_flags": [],
                "recommendations": ["Review with legal professional"]
            }
    
    async def classify_document(self, document_text: str) -> DocumentType:
        """Classify the type of legal document"""
        # Use first 2000 characters for classification
        excerpt = document_text[:2000]
        prompt = self.document_classification_prompt.format(document_text=excerpt)
        
        try:
            response_text = await self._make_request(prompt)
            result = json.loads(response_text)
            document_type_str = result.get("document_type", "other")
            
            try:
                return DocumentType(document_type_str)
            except ValueError:
                return DocumentType.OTHER
        except Exception as e:
            logger.error(f"Document classification error: {str(e)}")
            return DocumentType.OTHER
    
    async def answer_query(self, document_context: str, relevant_clauses: List[str], query: str) -> Dict[str, Any]:
        """Answer user query about document"""
        # Limit context size
        context = document_context[:3000]
        clauses_text = "\n\n".join(relevant_clauses[:5])  # Limit to 5 most relevant clauses
        
        prompt = self.query_prompt.format(
            document_context=context,
            relevant_clauses=clauses_text,
            query=query
        )
        
        try:
            response_text = await self._make_request(prompt)
            result = json.loads(response_text)
            return self._validate_query_response(result)
        except Exception as e:
            logger.error(f"Query answering error: {str(e)}")
            return {
                "answer": f"I couldn't process your query due to an error: {str(e)}",
                "confidence": 0.0,
                "sources_used": []
            }
    
    def _validate_legal_analysis(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean legal analysis response"""
        return {
            "clause_type": result.get("clause_type", "other"),
            "obligations": result.get("obligations", []) if isinstance(result.get("obligations"), list) else [],
            "risk_score": max(1, min(10, int(result.get("risk_score", 5)))),
            "risk_explanation": str(result.get("risk_explanation", "No explanation provided")),
            "simplified_text": str(result.get("simplified_text", "")),
            "concerns": result.get("concerns", []) if isinstance(result.get("concerns"), list) else [],
            "key_terms": result.get("key_terms", []) if isinstance(result.get("key_terms"), list) else [],
            "recommendations": result.get("recommendations", []) if isinstance(result.get("recommendations"), list) else []
        }
    
    def _validate_risk_assessment(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean risk assessment response"""
        return {
            "risk_score": max(1, min(10, int(result.get("risk_score", 5)))),
            "risk_explanation": str(result.get("risk_explanation", "No explanation provided")),
            "red_flags": result.get("red_flags", []) if isinstance(result.get("red_flags"), list) else [],
            "recommendations": result.get("recommendations", []) if isinstance(result.get("recommendations"), list) else []
        }
    
    def _validate_query_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean query response"""
        return {
            "answer": str(result.get("answer", "No answer provided")),
            "confidence": max(0.0, min(1.0, float(result.get("confidence", 0.5)))),
            "sources_used": result.get("sources_used", []) if isinstance(result.get("sources_used"), list) else []
        }
    
    async def extract_document_summary(self, document_text: str) -> Dict[str, Any]:
        """Extract key information from document for summary"""
        summary_prompt = f"""
Extract key information from this legal document:

1. Parties involved (names/entities)
2. Key dates mentioned
3. Financial amounts mentioned
4. Contract duration if applicable
5. Main purpose of the document
6. Legal jurisdiction if mentioned

Document: {document_text[:3000]}

Response format: JSON with keys: parties, key_dates, key_amounts, duration, main_purpose, jurisdiction
"""
        
        try:
            response_text = await self._make_request(summary_prompt)
            result = json.loads(response_text)
            return {
                "parties": result.get("parties", []) if isinstance(result.get("parties"), list) else [],
                "key_dates": result.get("key_dates", []) if isinstance(result.get("key_dates"), list) else [],
                "key_amounts": result.get("key_amounts", []) if isinstance(result.get("key_amounts"), list) else [],
                "duration": result.get("duration"),
                "main_purpose": str(result.get("main_purpose", "")),
                "jurisdiction": result.get("jurisdiction")
            }
        except Exception as e:
            logger.error(f"Document summary error: {str(e)}")
            return {
                "parties": [],
                "key_dates": [],
                "key_amounts": [],
                "duration": None,
                "main_purpose": "Unable to determine",
                "jurisdiction": None
            }

# Global instance
gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get global Gemini service instance"""
    global gemini_service
    if gemini_service is None:
        gemini_service = GeminiService()
    return gemini_service