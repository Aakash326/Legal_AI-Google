from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from .document import LegalClause, DocumentSummary, DocumentType

class RiskCategory(BaseModel):
    category: str = Field(..., description="Risk category name")
    score: int = Field(..., ge=1, le=10, description="Risk score for this category")
    description: str = Field(..., description="Description of risks in this category")
    clauses_count: int = Field(0, ge=0, description="Number of clauses in this category")

class DocumentAnalysis(BaseModel):
    document_id: str = Field(..., description="Unique document identifier")
    document_type: DocumentType = Field(..., description="Classified document type")
    overall_risk_score: float = Field(..., ge=1.0, le=10.0, description="Overall document risk score")
    document_summary: DocumentSummary = Field(..., description="Key information extracted from document")
    key_clauses: List[LegalClause] = Field(default_factory=list, description="Identified legal clauses")
    risk_categories: List[RiskCategory] = Field(default_factory=list, description="Risk breakdown by category")
    recommendations: List[str] = Field(default_factory=list, description="General recommendations for the document")
    red_flags: List[str] = Field(default_factory=list, description="Critical issues identified")
    
    # Enhanced comprehensive explanation fields
    document_explanation: str = Field(default="", description="Comprehensive plain-language explanation of the entire document")
    key_provisions_explained: List[str] = Field(default_factory=list, description="Detailed explanations of major provisions")
    legal_implications: List[str] = Field(default_factory=list, description="Important legal implications and consequences")
    practical_impact: str = Field(default="", description="What this document means in practical terms")
    clause_by_clause_summary: List[str] = Field(default_factory=list, description="Summary of each major clause in plain language")
    
    processing_time: float = Field(..., ge=0, description="Total processing time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class QueryResult(BaseModel):
    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Generated answer to the query")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the answer")
    relevant_clauses: List[str] = Field(default_factory=list, description="Clause IDs relevant to the query")
    sources: List[str] = Field(default_factory=list, description="Source text snippets used for the answer")
    document_id: str = Field(..., description="Document this query was asked about")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ClauseAnalysisResult(BaseModel):
    clause_id: str = Field(..., description="Unique clause identifier")
    analysis_success: bool = Field(..., description="Whether analysis completed successfully")
    error_message: Optional[str] = Field(None, description="Error message if analysis failed")
    processing_time: float = Field(..., ge=0, description="Time taken to analyze this clause")

class RiskAssessmentResult(BaseModel):
    document_id: str = Field(..., description="Document identifier")
    overall_risk: float = Field(..., ge=1.0, le=10.0, description="Overall risk score")
    high_risk_clauses: List[str] = Field(default_factory=list, description="Clause IDs with risk score >= 7")
    medium_risk_clauses: List[str] = Field(default_factory=list, description="Clause IDs with risk score 4-6")
    low_risk_clauses: List[str] = Field(default_factory=list, description="Clause IDs with risk score 1-3")
    risk_distribution: Dict[str, int] = Field(default_factory=dict, description="Risk score distribution")
    recommendations: List[str] = Field(default_factory=list, description="Risk-based recommendations")

class ProcessingStats(BaseModel):
    total_processing_time: float = Field(..., ge=0, description="Total processing time in seconds")
    text_extraction_time: float = Field(..., ge=0, description="Time for text extraction")
    clause_analysis_time: float = Field(..., ge=0, description="Time for clause analysis")
    risk_assessment_time: float = Field(..., ge=0, description="Time for risk assessment")
    total_clauses_found: int = Field(0, ge=0, description="Total number of clauses identified")
    successful_analyses: int = Field(0, ge=0, description="Number of successfully analyzed clauses")
    failed_analyses: int = Field(0, ge=0, description="Number of failed clause analyses")