"""
Modern Gemini Service using the official Google GenAI SDK (2025)
Replaces the legacy google-generativeai implementation with proper structured output and error handling
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

try:
    from google import genai
    from google.genai import types
except ImportError:
    # Fallback if new SDK not installed yet
    import google.generativeai as genai_legacy
    genai = None
    types = None

from models.document import ClauseType, DocumentType
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class LegalAnalysisResponse(BaseModel):
    clause_type: str = Field(..., description="Type of legal clause")
    obligations: List[str] = Field(default_factory=list, description="Key obligations")
    risk_score: int = Field(..., ge=1, le=10, description="Risk score 1-10")
    risk_explanation: str = Field(..., description="Explanation of risk assessment")
    simplified_text: str = Field(..., description="Plain language explanation")
    concerns: List[str] = Field(default_factory=list, description="Potential concerns")
    key_terms: List[str] = Field(default_factory=list, description="Key terms extracted")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")

class DocumentClassificationResponse(BaseModel):
    document_type: str = Field(..., description="Type of document")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(..., description="Classification reasoning")

class DocumentSummaryResponse(BaseModel):
    parties: List[str] = Field(default_factory=list, description="Parties involved")
    key_dates: List[str] = Field(default_factory=list, description="Important dates")
    key_amounts: List[str] = Field(default_factory=list, description="Financial amounts")
    duration: Optional[str] = Field(None, description="Contract duration")
    main_purpose: str = Field(..., description="Main purpose of document")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Answer to the query")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in answer")
    sources_used: List[str] = Field(default_factory=list, description="Sources referenced")

class DocumentExplanationResponse(BaseModel):
    document_explanation: str = Field(..., description="Comprehensive explanation of the document")
    key_provisions: List[str] = Field(default_factory=list, description="Key provisions explained")
    legal_implications: List[str] = Field(default_factory=list, description="Legal implications")
    practical_impact: str = Field(..., description="Practical impact explanation")
    clause_summaries: List[str] = Field(default_factory=list, description="Clause-by-clause summaries")

class ModernGeminiService:
    """Modern Gemini service using the official Google GenAI SDK"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Initialize the modern client
        if genai:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = "gemini-1.5-flash"  # More stable model with higher rate limits
            self.use_modern_sdk = True
            logger.info("Using modern Google GenAI SDK")
        else:
            # Fallback to legacy SDK if modern one not available
            genai_legacy.configure(api_key=self.api_key)
            self.model = genai_legacy.GenerativeModel('gemini-1.5-flash')
            self.use_modern_sdk = False
            logger.warning("Using legacy google-generativeai SDK - consider upgrading")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    async def _make_modern_request(self, prompt: str, response_schema=None) -> str:
        """Make request using modern Google GenAI SDK"""
        try:
            config = {
                "response_mime_type": "application/json",
                "temperature": 0.1,
                "max_output_tokens": 2048,
            }
            
            if response_schema:
                config["response_schema"] = response_schema
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            # Handle response properly
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            elif hasattr(response, 'parsed') and response.parsed:
                return json.dumps(response.parsed) if not isinstance(response.parsed, str) else response.parsed
            else:
                logger.warning("Empty response from Gemini API")
                return "{}"
            
        except Exception as e:
            logger.error(f"Modern Gemini API error: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _make_legacy_request(self, prompt: str) -> str:
        """Fallback request using legacy SDK"""
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                logger.warning("Empty response from legacy Gemini API")
                return "{}"
        except Exception as e:
            logger.error(f"Legacy Gemini API error: {str(e)}")
            raise
    
    async def _safe_json_parse(self, text: str) -> Dict[str, Any]:
        """Safely parse JSON response"""
        try:
            # Clean up common markdown formatting
            text = text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            if not text or text == "{}":
                raise ValueError("Empty JSON response from API")
            
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}, text: {text[:100]}...")
            raise ValueError(f"Invalid JSON response from API: {e}")
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}")
            raise
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is due to rate limiting"""
        error_str = str(error).lower()
        return any(term in error_str for term in [
            'rate limit', 'quota exceeded', '429', 'resource_exhausted',
            'too many requests', 'rate_limit_exceeded'
        ])
    
    async def analyze_legal_text(self, clause_text: str) -> Dict[str, Any]:
        """Analyze a legal clause using modern Gemini API"""
        prompt = f"""
Analyze this legal clause and provide a detailed assessment:

CLAUSE TEXT:
{clause_text}

INSTRUCTIONS:
1. Classify clause type from: payment_terms, termination, liability, privacy, indemnification, dispute_resolution, intellectual_property, confidentiality, force_majeure, governing_law, amendment, severability, other
2. List key obligations for each party
3. Assess risk level (1-10 scale) with detailed explanation
4. Provide plain language explanation
5. Identify potential concerns or red flags
6. Extract key terms and definitions
7. Provide specific recommendations

IMPORTANT: Respond ONLY with valid JSON using this exact structure:
{{
    "clause_type": "string",
    "obligations": ["string"],
    "risk_score": integer,
    "risk_explanation": "string", 
    "simplified_text": "string",
    "concerns": ["string"],
    "key_terms": ["string"],
    "recommendations": ["string"]
}}
"""
        
        if self.use_modern_sdk:
            response_text = await self._make_modern_request(prompt, LegalAnalysisResponse)
        else:
            response_text = await self._make_legacy_request(prompt)
        
        result = await self._safe_json_parse(response_text)
        return self._validate_legal_analysis(result)
    
    async def classify_document(self, document_text: str) -> DocumentType:
        """Classify the type of legal document"""
        excerpt = document_text[:2000]  # Limit for better performance
        
        prompt = f"""
Classify this legal document into one of these types:
- rental_agreement
- employment_contract  
- loan_agreement
- terms_of_service
- privacy_policy
- purchase_agreement
- other

DOCUMENT EXCERPT:
{excerpt}

INSTRUCTIONS:
Analyze the document content and provide classification with confidence and reasoning.

IMPORTANT: Respond ONLY with valid JSON:
{{
    "document_type": "string",
    "confidence": 0.95,
    "reasoning": "string explaining classification"
}}
"""
        
        if self.use_modern_sdk:
            response_text = await self._make_modern_request(prompt, DocumentClassificationResponse)
        else:
            response_text = await self._make_legacy_request(prompt)
        
        result = await self._safe_json_parse(response_text)
        
        document_type_str = result.get("document_type", "other")
        
        try:
            return DocumentType(document_type_str)
        except ValueError:
            logger.warning(f"Unknown document type: {document_type_str}")
            return DocumentType.OTHER
    
    async def extract_document_summary(self, document_text: str) -> Dict[str, Any]:
        """Extract key information from document for summary"""
        content = document_text[:3000]  # Limit content size
        
        prompt = f"""
Extract key information from this legal document:

DOCUMENT CONTENT:
{content}

EXTRACT:
1. All parties involved (person/company names)
2. Important dates mentioned (deadlines, effective dates, etc.)
3. Financial amounts and monetary terms
4. Contract duration or term length
5. Main purpose/subject of the document
6. Legal jurisdiction or governing law location

IMPORTANT: Respond ONLY with valid JSON:
{{
    "parties": ["string"],
    "key_dates": ["string"],
    "key_amounts": ["string"],
    "duration": "string or null",
    "main_purpose": "string",
    "jurisdiction": "string or null"
}}
"""
        
        if self.use_modern_sdk:
            response_text = await self._make_modern_request(prompt, DocumentSummaryResponse)
        else:
            response_text = await self._make_legacy_request(prompt)
        
        result = await self._safe_json_parse(response_text)
        return {
            "parties": result.get("parties", []) if isinstance(result.get("parties"), list) else [],
            "key_dates": result.get("key_dates", []) if isinstance(result.get("key_dates"), list) else [],
            "key_amounts": result.get("key_amounts", []) if isinstance(result.get("key_amounts"), list) else [],
            "duration": result.get("duration"),
            "main_purpose": str(result.get("main_purpose", "Unable to determine")),
            "jurisdiction": result.get("jurisdiction")
        }
    
    async def answer_query(self, document_context: str, relevant_clauses: List[str], query: str) -> Dict[str, Any]:
        """Answer user query about document"""
        context = document_context[:2000]
        clauses_text = "\\n\\n".join(relevant_clauses[:3])
        
        prompt = f"""
Answer this question about the legal document based on the provided context.

DOCUMENT CONTEXT:
{context}

RELEVANT CLAUSES:
{clauses_text}

USER QUESTION:
{query}

INSTRUCTIONS:
- Provide a clear, accurate answer based only on the document content
- If information isn't available in the document, clearly state this
- Include confidence level in your answer
- Reference specific clauses/sections used

IMPORTANT: Respond ONLY with valid JSON:
{{
    "answer": "string",
    "confidence": 0.95,
    "sources_used": ["string"]
}}
"""
        
        if self.use_modern_sdk:
            response_text = await self._make_modern_request(prompt, QueryResponse)
        else:
            response_text = await self._make_legacy_request(prompt)
        
        result = await self._safe_json_parse(response_text)
        return self._validate_query_response(result)
    
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
    
    def _validate_query_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean query response"""
        return {
            "answer": str(result.get("answer", "No answer provided")),
            "confidence": max(0.0, min(1.0, float(result.get("confidence", 0.5)))),
            "sources_used": result.get("sources_used", []) if isinstance(result.get("sources_used"), list) else []
        }
    
    async def generate_comprehensive_explanation(self, document_text: str, document_type: str, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive explanation of the entire document"""
        # Limit document text for better processing
        content = document_text[:4000]
        
        # Create a summary of key clauses
        clause_summary = "\n".join([
            f"- {clause.get('clause_type', 'Unknown')}: {clause.get('simplified_text', 'No description')[:100]}..."
            for clause in clauses[:10]  # Limit to top 10 clauses
        ])
        
        prompt = f"""
Provide a comprehensive, easy-to-understand explanation of this legal document.

DOCUMENT TYPE: {document_type}

DOCUMENT CONTENT:
{content}

KEY CLAUSES IDENTIFIED:
{clause_summary}

INSTRUCTIONS:
Provide a detailed explanation that includes:
1. Overall purpose and nature of this document
2. Key provisions and what they mean in plain language
3. Important legal implications for all parties
4. Practical impact and real-world consequences
5. Clause-by-clause summary of major sections

Write in clear, non-legal language that anyone can understand. Focus on practical implications rather than legal jargon.

IMPORTANT: Respond ONLY with valid JSON using this exact structure:
{{
    "document_explanation": "comprehensive explanation of the entire document",
    "key_provisions": ["provision 1 explained", "provision 2 explained"],
    "legal_implications": ["implication 1", "implication 2"],
    "practical_impact": "what this means in practical terms",
    "clause_summaries": ["clause 1 summary", "clause 2 summary"]
}}
"""
        
        if self.use_modern_sdk:
            response_text = await self._make_modern_request(prompt, DocumentExplanationResponse)
        else:
            response_text = await self._make_legacy_request(prompt)
        
        result = await self._safe_json_parse(response_text)
        return self._validate_explanation_response(result)
    
    def _validate_explanation_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean explanation response"""
        return {
            "document_explanation": str(result.get("document_explanation", "Unable to generate explanation")),
            "key_provisions": result.get("key_provisions", []) if isinstance(result.get("key_provisions"), list) else [],
            "legal_implications": result.get("legal_implications", []) if isinstance(result.get("legal_implications"), list) else [],
            "practical_impact": str(result.get("practical_impact", "Unable to determine practical impact")),
            "clause_summaries": result.get("clause_summaries", []) if isinstance(result.get("clause_summaries"), list) else []
        }


# Global instance
modern_gemini_service = None

def get_modern_gemini_service() -> ModernGeminiService:
    """Get global modern Gemini service instance"""
    global modern_gemini_service
    if modern_gemini_service is None:
        modern_gemini_service = ModernGeminiService()
    return modern_gemini_service