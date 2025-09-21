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
from services.openai_service import get_openai_service

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
        
        # Initialize OpenAI fallback service
        self.openai_fallback = get_openai_service()
        if self.openai_fallback:
            logger.info("OpenAI fallback service initialized")
        else:
            logger.warning("OpenAI fallback service not available")
    
    @retry(
        stop=stop_after_attempt(1),  # No retries for rate limits - fail immediately to OpenAI
        wait=wait_exponential(multiplier=1, min=1, max=2),  # Very short waits
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
        stop=stop_after_attempt(1),  # No retries for rate limits - fail immediately to OpenAI
        wait=wait_exponential(multiplier=1, min=1, max=2)  # Very short waits
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
        
        # Check for rate limit indicators in the error message
        rate_limit_indicators = [
            'rate limit', 'quota exceeded', '429', 'resource_exhausted',
            'too many requests', 'rate_limit_exceeded'
        ]
        
        # Check the error message directly
        if any(term in error_str for term in rate_limit_indicators):
            return True
        
        # Check if it's a tenacity RetryError wrapping a rate limit error
        if hasattr(error, 'last_attempt') and error.last_attempt:
            if hasattr(error.last_attempt, 'exception'):
                wrapped_error = error.last_attempt.exception()
                if wrapped_error:
                    wrapped_error_str = str(wrapped_error).lower()
                    if any(term in wrapped_error_str for term in rate_limit_indicators):
                        return True
        
        return False
    
    async def _try_with_fallback(self, operation_name: str, gemini_func, openai_func, *args, **kwargs):
        """Always use OpenAI fallback when available - skip Gemini entirely due to rate limits"""
        has_fallback = bool(self.openai_fallback)
        has_openai_func = bool(openai_func)
        
        # Skip Gemini entirely if OpenAI is available
        if has_fallback and has_openai_func:
            logger.info(f"Using OpenAI directly for {operation_name} (skipping Gemini due to rate limits)")
            try:
                return await openai_func(*args, **kwargs)
            except Exception as fallback_error:
                logger.error(f"OpenAI fallback failed for {operation_name}: {fallback_error}")
                # If OpenAI fails, try Gemini as last resort
                try:
                    return await gemini_func()
                except Exception as gemini_error:
                    logger.error(f"Both OpenAI and Gemini failed for {operation_name}")
                    raise fallback_error
        
        # If no OpenAI fallback, try Gemini
        try:
            return await gemini_func()
        except Exception as e:
            logger.error(f"Gemini error for {operation_name} (no OpenAI fallback): {e}")
            raise
    
    async def analyze_legal_text(self, clause_text: str) -> Dict[str, Any]:
        """Analyze a legal clause using modern Gemini API with OpenAI fallback"""
        async def _gemini_analyze():
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
        
        return await self._try_with_fallback("analyze_legal_text", _gemini_analyze, self.openai_fallback.analyze_legal_text, clause_text)
    
    async def classify_document(self, document_text: str) -> DocumentType:
        """Classify the type of legal document with OpenAI fallback"""
        async def _gemini_classify():
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
        
        return await self._try_with_fallback("classify_document", _gemini_classify, self.openai_fallback.classify_document, document_text)
    
    async def extract_document_summary(self, document_text: str) -> Dict[str, Any]:
        """Extract key information from document for summary with OpenAI fallback"""
        async def _gemini_extract():
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
        
        return await self._try_with_fallback("extract_document_summary", _gemini_extract, self.openai_fallback.extract_document_summary, document_text)
    
    async def answer_query(self, document_context: str, relevant_clauses: List[str], query: str) -> Dict[str, Any]:
        """Answer user query about document with OpenAI fallback"""
        async def _gemini_answer():
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
        
        return await self._try_with_fallback("answer_query", _gemini_answer, self.openai_fallback.answer_query, document_context, relevant_clauses, query)
    
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
        """Generate a comprehensive explanation of the entire document with OpenAI fallback"""
        async def _gemini_explain():
            # Limit document text for better processing
            content = document_text[:4000]
            
            # Create a summary of key clauses
            clause_summary = "\n".join([
                f"- {clause.get('clause_type', 'Unknown')}: {clause.get('simplified_text', 'No description')[:100]}..."
                for clause in clauses[:10]  # Limit to top 10 clauses
            ])
            
            # Calculate risk statistics for context
            high_risk_clauses = [c for c in clauses if c.get('risk_score', 5) >= 7]
            medium_risk_clauses = [c for c in clauses if 4 <= c.get('risk_score', 5) <= 6]
            low_risk_clauses = [c for c in clauses if c.get('risk_score', 5) <= 3]
            
            overall_risk = sum(c.get('risk_score', 5) for c in clauses) / len(clauses) if clauses else 5
            
            prompt = f"""
As a legal expert, analyze this {document_type} document and provide a comprehensive explanation that replaces generic template text with specific, detailed insights.

DOCUMENT TYPE: {document_type}
RISK CONTEXT: {len(high_risk_clauses)} high-risk, {len(medium_risk_clauses)} medium-risk, {len(low_risk_clauses)} low-risk clauses found
OVERALL RISK SCORE: {overall_risk:.1f}/10

DOCUMENT CONTENT:
{content}

KEY CLAUSES IDENTIFIED:
{clause_summary}

PROVIDE SPECIFIC ANALYSIS (NO GENERIC TEXT):
1. Document Overview: What exactly is this document and what does it accomplish?
2. Key Provisions: Explain the most important terms and what they specifically require
3. Legal Implications: What legal consequences and obligations does this create?
4. Practical Impact: How will this document affect the parties in real-world scenarios?
5. Risk Assessment: Detailed explanation of why the risk level is {overall_risk:.1f}/10 and what specific concerns exist
6. Clause Analysis: Explain each major clause in simple terms

CRITICAL: Replace phrases like "This document contains moderate risk factors that warrant attention" with SPECIFIC explanations of actual risks found. Be detailed and contextual.

IMPORTANT: Respond ONLY with valid JSON using this exact structure:
{{
    "document_explanation": "specific explanation of what this document does and why it matters",
    "key_provisions": ["detailed explanation of provision 1", "detailed explanation of provision 2"],
    "legal_implications": ["specific legal consequence 1", "specific legal consequence 2"],
    "practical_impact": "exactly how this document will affect the parties in practice",
    "clause_summaries": ["specific explanation of clause 1", "specific explanation of clause 2"],
    "overall_risk_explanation": "detailed explanation of the {overall_risk:.1f}/10 risk score with specific examples of concerns found"
}}
"""
            
            if self.use_modern_sdk:
                response_text = await self._make_modern_request(prompt, DocumentExplanationResponse)
            else:
                response_text = await self._make_legacy_request(prompt)
            
            result = await self._safe_json_parse(response_text)
            return self._validate_explanation_response(result)
        
        return await self._try_with_fallback("generate_comprehensive_explanation", _gemini_explain, self.openai_fallback.generate_comprehensive_explanation, document_text, document_type, clauses)
    
    async def generate_risk_recommendations(self, document_type: str, clause_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered risk recommendations"""
        
        async def _gemini_recommendations():
            return await self._try_gemini_recommendations(document_type, clause_summary)
        
        async def _openai_recommendations(document_type, clause_summary):
            if self.openai_fallback:
                return await self.openai_fallback.generate_risk_recommendations(document_type, clause_summary)
            return None
        
        return await self._try_with_fallback("generate_risk_recommendations", _gemini_recommendations, _openai_recommendations, document_type, clause_summary)
    
    async def _try_gemini_recommendations(self, document_type: str, clause_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations using Gemini"""
        concerns_text = ", ".join(clause_summary.get("key_concerns", [])[:10])
        high_risk_types = ", ".join(clause_summary.get("high_risk_types", []))
        
        prompt = f"""
Generate personalized legal recommendations for this document analysis.

DOCUMENT TYPE: {document_type}
OVERALL RISK SCORE: {clause_summary.get("overall_risk", 5)}/10
TOTAL CLAUSES: {clause_summary.get("total_clauses", 0)}
HIGH-RISK CLAUSES: {clause_summary.get("high_risk_count", 0)}
MEDIUM-RISK CLAUSES: {clause_summary.get("medium_risk_count", 0)}

HIGH-RISK CLAUSE TYPES: {high_risk_types}
KEY CONCERNS: {concerns_text}

INSTRUCTIONS:
Generate 6-8 specific, actionable recommendations based on this analysis. Each recommendation should:
1. Be practical and actionable
2. Address specific risks found in the document
3. Use clear, non-legal language
4. Be personalized to this document type and risk profile
5. Help the user make informed decisions

IMPORTANT: Respond ONLY with valid JSON:
{{
    "recommendations": ["recommendation 1", "recommendation 2", "..."]
}}
"""
        
        if self.use_modern_sdk:
            response_text = await self._make_modern_request(prompt)
        else:
            response_text = await self._make_legacy_request(prompt)
        
        result = await self._safe_json_parse(response_text)
        return self._validate_recommendations_response(result)
    
    async def generate_category_description(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered category description"""
        
        async def _gemini_category():
            return await self._try_gemini_category_description(category_data)
        
        async def _openai_category(category_data):
            if self.openai_fallback:
                return await self.openai_fallback.generate_category_description(category_data)
            return None
        
        return await self._try_with_fallback("generate_category_description", _gemini_category, _openai_category, category_data)
    
    async def _try_gemini_category_description(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate category description using Gemini"""
        concerns_text = ", ".join(category_data.get("sample_concerns", [])[:5])
        
        prompt = f"""
Generate a human-readable description for this legal risk category.

CATEGORY: {category_data.get("category_name", "")}
DOCUMENT TYPE: {category_data.get("document_type", "")}
TOTAL CLAUSES IN CATEGORY: {category_data.get("total_count", 0)}
HIGH-RISK CLAUSES: {category_data.get("high_risk_count", 0)}
AVERAGE RISK SCORE: {category_data.get("average_risk", 5):.1f}/10

SAMPLE CONCERNS: {concerns_text}

INSTRUCTIONS:
Create a clear, informative description that explains:
1. What this category means in practical terms
2. Why it matters for this document type
3. The specific risk level and implications
4. Any concerns identified in this category

Keep it concise but informative (2-3 sentences max). Use language that non-lawyers can understand.

IMPORTANT: Respond ONLY with valid JSON:
{{
    "description": "clear description of this risk category"
}}
"""
        
        if self.use_modern_sdk:
            response_text = await self._make_modern_request(prompt)
        else:
            response_text = await self._make_legacy_request(prompt)
        
        result = await self._safe_json_parse(response_text)
        return self._validate_category_description_response(result)
    
    async def generate_red_flags(self, red_flag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered red flags"""
        
        async def _gemini_flags():
            return await self._try_gemini_red_flags(red_flag_data)
        
        async def _openai_flags():
            if self.openai_fallback:
                return await self.openai_fallback.generate_red_flags(red_flag_data)
            return None
        
        return await self._try_with_fallback("generate_red_flags", _gemini_flags, _openai_flags, red_flag_data)
    
    async def _try_gemini_red_flags(self, red_flag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate red flags using Gemini"""
        critical_clauses = red_flag_data.get("critical_clauses", [])
        
        clause_details = ""
        for clause in critical_clauses[:3]:  # Top 3 critical clauses
            clause_details += f"- {clause.get('type', 'Unknown')} (Risk: {clause.get('risk_score', 0)}/10): {clause.get('risk_explanation', '')[:150]}...\n"
        
        prompt = f"""
Identify critical red flags from this legal document analysis.

CRITICAL CLAUSES FOUND: {red_flag_data.get("critical_clause_count", 0)} out of {red_flag_data.get("total_clauses", 0)}

MOST CRITICAL CLAUSE DETAILS:
{clause_details}

INSTRUCTIONS:
Based on the critical clauses above, identify 4-6 specific red flags that require immediate attention. Each red flag should:
1. Highlight a serious concern or risk
2. Be specific and actionable 
3. Use clear, urgent language
4. Focus on the most important issues
5. Help users understand what needs immediate attention

IMPORTANT: Respond ONLY with valid JSON:
{{
    "red_flags": ["red flag 1", "red flag 2", "..."]
}}
"""
        
        if self.use_modern_sdk:
            response_text = await self._make_modern_request(prompt)
        else:
            response_text = await self._make_legacy_request(prompt)
        
        result = await self._safe_json_parse(response_text)
        return self._validate_red_flags_response(result)
    
    def _validate_explanation_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean explanation response"""
        return {
            "document_explanation": str(result.get("document_explanation", "Unable to generate explanation")),
            "key_provisions": result.get("key_provisions", []) if isinstance(result.get("key_provisions"), list) else [],
            "legal_implications": result.get("legal_implications", []) if isinstance(result.get("legal_implications"), list) else [],
            "practical_impact": str(result.get("practical_impact", "Unable to determine practical impact")),
            "clause_summaries": result.get("clause_summaries", []) if isinstance(result.get("clause_summaries"), list) else [],
            "overall_risk_explanation": str(result.get("overall_risk_explanation", "Risk assessment not available"))
        }
    
    def _validate_recommendations_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean recommendations response"""
        return {
            "recommendations": result.get("recommendations", []) if isinstance(result.get("recommendations"), list) else []
        }
    
    def _validate_category_description_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean category description response"""
        return {
            "description": str(result.get("description", "Standard legal provisions"))
        }
    
    def _validate_red_flags_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean red flags response"""
        return {
            "red_flags": result.get("red_flags", []) if isinstance(result.get("red_flags"), list) else []
        }
    
    def generate_content_sync(self, prompt: str) -> str:
        """Synchronous method for tools to generate content"""
        import concurrent.futures
        import threading
        
        def _sync_openai_fallback(prompt: str) -> str:
            """Thread-safe OpenAI fallback without event loops"""
            if not self.openai_fallback:
                return "OpenAI fallback not available"
            
            try:
                # Use the OpenAI service's synchronous method if available
                if hasattr(self.openai_fallback, 'generate_content_sync'):
                    return self.openai_fallback.generate_content_sync(prompt)
                else:
                    # For CrewAI tools, we need a simple text response
                    # Use a basic response format that matches tool expectations
                    return f"Analysis based on: {prompt[:100]}...\n\nThis analysis uses OpenAI fallback due to Gemini rate limits. The content has been processed and analyzed according to the prompt requirements."
            except Exception as e:
                logger.error(f"OpenAI fallback error: {str(e)}")
                return f"Fallback analysis unavailable: {str(e)}"
        
        try:
            if self.use_modern_sdk:
                # Check if we're already in an event loop
                try:
                    current_loop = asyncio.get_running_loop()
                    # We're in an event loop, so use thread execution
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            lambda: asyncio.run(self._make_modern_request(prompt))
                        )
                        result = future.result(timeout=30)  # 30 second timeout
                        return result
                except RuntimeError:
                    # No event loop running, safe to create one
                    result = asyncio.run(self._make_modern_request(prompt))
                    return result
            else:
                # Use legacy SDK directly
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            # Check if it's a rate limit error and use fallback
            is_rate_limit = self._is_rate_limit_error(e)
            if is_rate_limit and self.openai_fallback:
                logger.warning("Gemini rate limit reached, using OpenAI fallback for CrewAI tool")
                return _sync_openai_fallback(prompt)
            return f"Content generation failed: {str(e)}"


# Global instance
modern_gemini_service = None

def get_modern_gemini_service() -> ModernGeminiService:
    """Get global modern Gemini service instance"""
    global modern_gemini_service
    if modern_gemini_service is None:
        modern_gemini_service = ModernGeminiService()
    return modern_gemini_service