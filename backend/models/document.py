from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    RENTAL_AGREEMENT = "rental_agreement"
    EMPLOYMENT_CONTRACT = "employment_contract"
    LOAN_AGREEMENT = "loan_agreement"
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    PURCHASE_AGREEMENT = "purchase_agreement"
    OTHER = "other"

class ProcessingStatus(BaseModel):
    document_id: str
    status: str = Field(..., description="Current processing status")
    progress: int = Field(0, ge=0, le=100, description="Progress percentage (0-100)")
    current_step: str = Field("", description="Description of current processing step")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

class UploadedDocument(BaseModel):
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File extension (.pdf, .docx, .txt)")
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    file_size: int = Field(..., ge=0, description="File size in bytes")
    
class ProcessedDocument(BaseModel):
    document_id: str = Field(..., description="Unique document identifier")
    document_type: DocumentType = Field(..., description="Classified document type")
    extracted_text: str = Field(..., description="Full extracted text from document")
    chunks: List[str] = Field(default_factory=list, description="Text chunks for processing")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    word_count: int = Field(0, ge=0, description="Total word count")
    page_count: int = Field(0, ge=0, description="Total page count")

class ClauseType(str, Enum):
    PAYMENT_TERMS = "payment_terms"
    TERMINATION = "termination"
    LIABILITY = "liability"
    PRIVACY = "privacy"
    INDEMNIFICATION = "indemnification"
    DISPUTE_RESOLUTION = "dispute_resolution"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CONFIDENTIALITY = "confidentiality"
    FORCE_MAJEURE = "force_majeure"
    GOVERNING_LAW = "governing_law"
    AMENDMENT = "amendment"
    SEVERABILITY = "severability"
    OTHER = "other"

class LegalClause(BaseModel):
    clause_id: str = Field(..., description="Unique clause identifier")
    clause_type: ClauseType = Field(..., description="Type of legal clause")
    original_text: str = Field(..., description="Original clause text from document")
    simplified_text: str = Field(..., description="Plain language explanation")
    risk_score: int = Field(..., ge=1, le=10, description="Risk level (1-10 scale)")
    risk_explanation: str = Field(..., description="Explanation of the risk assessment")
    section_number: Optional[str] = Field(None, description="Section number if available")
    page_number: Optional[int] = Field(None, description="Page number where clause appears")
    key_terms: List[str] = Field(default_factory=list, description="Key terms extracted from clause")
    recommendations: List[str] = Field(default_factory=list, description="Specific recommendations for this clause")
    concerns: List[str] = Field(default_factory=list, description="Potential concerns or red flags")
    obligations: List[str] = Field(default_factory=list, description="Key obligations for each party")

class DocumentSummary(BaseModel):
    parties: List[str] = Field(default_factory=list, description="Parties involved in the document")
    key_dates: List[str] = Field(default_factory=list, description="Important dates mentioned")
    key_amounts: List[str] = Field(default_factory=list, description="Financial amounts mentioned")
    duration: Optional[str] = Field(None, description="Contract duration if applicable")
    main_purpose: str = Field("", description="Main purpose of the document")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction")