"""
OpenAI Service as fallback for when Gemini API limits are reached
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

from models.document import ClauseType, DocumentType

logger = logging.getLogger(__name__)

class OpenAIService:
    """OpenAI service as fallback for Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Using GPT-4o-mini for better performance
        logger.info("OpenAI fallback service initialized with GPT-4o-mini")
    
    @retry(
        stop=stop_after_attempt(1),  # No retries - fail fast
        wait=wait_exponential(multiplier=1, min=1, max=2),  # Very short waits
        retry=retry_if_exception_type((Exception,))
    )
    async def _make_request(self, prompt: str, temperature: float = 0.1) -> str:
        """Make request to OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a legal analysis AI. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=2048
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            else:
                logger.warning("Empty response from OpenAI API")
                return "{}"
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def _safe_json_parse(self, text: str) -> Dict[str, Any]:
        """Safely parse JSON response"""
        try:
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
    
    async def analyze_legal_text(self, clause_text: str) -> Dict[str, Any]:
        """Analyze a legal clause using OpenAI"""
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
        
        response_text = await self._make_request(prompt)
        result = await self._safe_json_parse(response_text)
        return self._validate_legal_analysis(result)
    
    async def classify_document(self, document_text: str) -> DocumentType:
        """Classify the type of legal document"""
        excerpt = document_text[:2000]
        
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
        
        response_text = await self._make_request(prompt)
        result = await self._safe_json_parse(response_text)
        
        document_type_str = result.get("document_type", "other")
        
        try:
            return DocumentType(document_type_str)
        except ValueError:
            logger.warning(f"Unknown document type: {document_type_str}")
            return DocumentType.OTHER
    
    async def extract_document_summary(self, document_text: str) -> Dict[str, Any]:
        """Extract key information from document for summary"""
        content = document_text[:3000]
        
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
        
        response_text = await self._make_request(prompt)
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
        
        response_text = await self._make_request(prompt)
        result = await self._safe_json_parse(response_text)
        return self._validate_query_response(result)
    
    async def generate_comprehensive_explanation(self, document_text: str, document_type: str, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive explanation of the entire document"""
        content = document_text[:4000]
        
        clause_summary = "\n".join([
            f"- {clause.get('clause_type', 'Unknown')}: {clause.get('simplified_text', 'No description')[:100]}..."
            for clause in clauses[:10]
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
        
        response_text = await self._make_request(prompt)
        result = await self._safe_json_parse(response_text)
        return self._validate_explanation_response(result)
    
    async def generate_risk_recommendations(self, document_type: str, clause_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered risk recommendations using OpenAI"""
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
        
        response_text = await self._make_request(prompt)
        result = await self._safe_json_parse(response_text)
        return self._validate_recommendations_response(result)
    
    async def generate_category_description(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered category description using OpenAI"""
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
        
        response_text = await self._make_request(prompt)
        result = await self._safe_json_parse(response_text)
        return self._validate_category_description_response(result)
    
    async def generate_red_flags(self, red_flag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered red flags using OpenAI"""
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
        
        response_text = await self._make_request(prompt)
        result = await self._safe_json_parse(response_text)
        return self._validate_red_flags_response(result)
    
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
        """Synchronous method for CrewAI tools to generate content"""
        import concurrent.futures
        
        try:
            # Use thread executor to run async method
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(self._make_request(prompt, temperature=0.3))
                )
                result = future.result(timeout=30)  # 30 second timeout
                return result
        except Exception as e:
            logger.error(f"OpenAI sync content generation failed: {str(e)}")
            return f"OpenAI content generation failed: {str(e)}"

# Global instance
openai_service = None

def get_openai_service() -> Optional[OpenAIService]:
    """Get global OpenAI service instance if available"""
    global openai_service
    if openai_service is None:
        try:
            openai_service = OpenAIService()
        except (ImportError, ValueError) as e:
            logger.warning(f"OpenAI service not available: {e}")
            return None
    return openai_service