from typing import Dict, Any
from crewai.tools import BaseTool
from langchain.tools import Tool
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class LegalResearchInput(BaseModel):
    """Input schema for legal research tool"""
    clause_text: str = Field(..., description="Legal clause text to research")
    jurisdiction: str = Field(default="US", description="Legal jurisdiction")

class ComplianceCheckInput(BaseModel):
    """Input schema for compliance check tool"""
    document_text: str = Field(..., description="Document text to check")
    jurisdiction: str = Field(default="US", description="Legal jurisdiction")
    document_type: str = Field(default="general", description="Type of document")

class LegalResearchTool(BaseTool):
    name: str = "legal_precedent_research"
    description: str = "Research legal precedents and case law for specific clauses"
    args_schema: type[BaseModel] = LegalResearchInput
    gemini_service: Any = None
    
    def __init__(self, gemini_service=None, **kwargs):
        super().__init__(**kwargs)
        self.gemini_service = gemini_service
    
    def _run(self, clause_text: str, jurisdiction: str = "US") -> str:
        """Research legal precedents for a clause"""
        try:
            prompt = f"""
            Research legal precedents and case law related to this clause in {jurisdiction}:
            
            CLAUSE: {clause_text}
            
            Provide:
            1. Similar cases or legal precedents
            2. Common interpretations in courts
            3. Consumer protection aspects
            4. Industry standard practices
            5. Potential legal challenges
            
            Format as structured analysis with citations where possible.
            """
            
            # Use the synchronous method
            response = self.gemini_service.generate_content_sync(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Legal research failed: {str(e)}")
            return f"Legal research unavailable: {str(e)}"

class ComplianceCheckTool(BaseTool):
    name: str = "compliance_checker"
    description: str = "Check document compliance with consumer protection laws"
    args_schema: type[BaseModel] = ComplianceCheckInput
    gemini_service: Any = None
    
    def __init__(self, gemini_service=None, **kwargs):
        super().__init__(**kwargs)
        self.gemini_service = gemini_service
    
    def _run(self, document_text: str, jurisdiction: str = "US", document_type: str = "general") -> str:
        """Check compliance with regulations"""
        try:
            # Limit document text for API efficiency
            text_excerpt = document_text[:1500] + "..." if len(document_text) > 1500 else document_text
            
            prompt = f"""
            Check this {document_type} document for compliance with consumer protection laws in {jurisdiction}:
            
            DOCUMENT EXCERPT: {text_excerpt}
            
            Focus on:
            1. Fair Credit Reporting Act violations
            2. Truth in Lending Act compliance
            3. Fair Housing Act compliance (if applicable)
            4. State-specific consumer protection laws
            5. Unfair or deceptive practices
            6. Required disclosures
            7. Fee transparency requirements
            
            Provide specific law citations and violation risks.
            """
            
            response = self.gemini_service.generate_content_sync(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Compliance check failed: {str(e)}")
            return f"Compliance check unavailable: {str(e)}"

class MarketResearchTool(BaseTool):
    name: str = "market_research"
    description: str = "Research market alternatives and better options"
    gemini_service: Any = None
    
    def __init__(self, gemini_service=None, **kwargs):
        super().__init__(**kwargs)
        self.gemini_service = gemini_service
    
    def _run(self, document_type: str, problematic_terms: str) -> str:
        """Research market alternatives"""
        try:
            prompt = f"""
            Research market alternatives for this type of agreement:
            
            DOCUMENT TYPE: {document_type}
            PROBLEMATIC TERMS: {problematic_terms}
            
            Find:
            1. Better service providers with fairer terms
            2. Alternative contract structures
            3. Consumer-friendly options in the market
            4. Government or non-profit alternatives
            5. Industry best practices for fair terms
            
            Provide specific recommendations with reasons.
            """
            
            response = self.gemini_service.generate_content_sync(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Market research failed: {str(e)}")
            return f"Market research unavailable: {str(e)}"

class NegotiationStrategyTool(BaseTool):
    name: str = "negotiation_strategy"
    description: str = "Generate negotiation strategies for contract terms"
    gemini_service: Any = None
    
    def __init__(self, gemini_service=None, **kwargs):
        super().__init__(**kwargs)
        self.gemini_service = gemini_service
    
    def _run(self, high_risk_clauses: str, document_type: str) -> str:
        """Generate negotiation strategies"""
        try:
            prompt = f"""
            Develop negotiation strategies for these problematic clauses in a {document_type}:
            
            HIGH-RISK CLAUSES: {high_risk_clauses}
            
            Provide:
            1. Which terms are typically negotiable vs. non-negotiable
            2. Leverage points for the consumer
            3. Alternative language suggestions
            4. Walking-away triggers
            5. Timing strategies for negotiation
            6. Common compromises that work
            
            Focus on practical, actionable advice.
            """
            
            response = self.gemini_service.generate_content_sync(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Negotiation strategy generation failed: {str(e)}")
            return f"Negotiation strategy unavailable: {str(e)}"

class LegalToolsFactory:
    """Factory class to create legal tools for CrewAI agents"""
    
    def __init__(self, gemini_service):
        self.gemini_service = gemini_service
    
    def create_legal_research_tool(self) -> LegalResearchTool:
        """Create legal research tool"""
        return LegalResearchTool(self.gemini_service)
    
    def create_compliance_tool(self) -> ComplianceCheckTool:
        """Create compliance check tool"""
        return ComplianceCheckTool(self.gemini_service)
    
    def create_market_research_tool(self) -> MarketResearchTool:
        """Create market research tool"""
        return MarketResearchTool(self.gemini_service)
    
    def create_negotiation_tool(self) -> NegotiationStrategyTool:
        """Create negotiation strategy tool"""
        return NegotiationStrategyTool(self.gemini_service)
    
    def create_all_tools(self) -> Dict[str, BaseTool]:
        """Create all legal tools"""
        return {
            'legal_research': self.create_legal_research_tool(),
            'compliance_check': self.create_compliance_tool(),
            'market_research': self.create_market_research_tool(),
            'negotiation_strategy': self.create_negotiation_tool()
        }