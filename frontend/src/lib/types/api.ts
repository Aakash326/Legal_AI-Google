// API Response Types for LegalClarity AI

export interface UploadResponse {
  document_id: string;
  filename: string;
  status: string;
  message: string;
  enhancement_enabled?: boolean;
}

export interface DocumentStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  current_step: string;
  start_time?: string;
  end_time?: string;
  error_message?: string;
}

export interface RiskCategory {
  category: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  score: number;
  description: string;
}

export interface LegalClause {
  id: string;
  type: string;
  text: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risk_score: number;
  page_number?: number;
  section?: string;
  explanation: string;
  recommendations: string[];
  key_terms: string[];
}

export interface DocumentSummary {
  parties: string[];
  document_type: string;
  key_dates: { label: string; date: string }[];
  key_amounts: { label: string; amount: string }[];
  jurisdiction?: string;
}

export interface CrewAIEnhancement {
  legal_precedent_research?: string;
  consumer_rights_analysis?: string;
  compliance_assessment?: string;
  negotiation_guidance?: string;
  alternatives_research?: string;
  crew_ai_enhanced: boolean;
  crew_enhancement_time?: number;
  crew_agents_used?: string[];
  enhancement_timestamp?: string;
}

export interface DocumentAnalysis extends CrewAIEnhancement {
  document_id: string;
  overall_risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  document_summary: DocumentSummary;
  risk_categories: RiskCategory[];
  key_clauses: LegalClause[];
  red_flags: string[];
  recommendations: string[];
  processing_stats: {
    processing_time: number;
    total_pages: number;
    total_words: number;
  };
}

export interface QueryRequest {
  document_id: string;
  query: string;
}

export interface QueryResponse {
  query: string;
  answer: string;
  confidence: number;
  relevant_clauses: LegalClause[];
  sources: string[];
}

export interface SystemStatus {
  core_system: string;
  crewai_enabled: boolean;
  crewai_available: boolean;
  crewai_status?: {
    crew_initialized: boolean;
    agents_count: number;
    agent_roles: string[];
    llm_model: string;
    memory_enabled: boolean;
  };
  timestamp: string;
  active_documents: number;
  completed_analyses: number;
}

// UI Component Types
export interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
}

export interface AnalysisState {
  isLoading: boolean;
  data: DocumentAnalysis | null;
  error: string | null;
}