import asyncio
import uuid
import time
from typing import List, Dict, Any
import logging

from models.document import ProcessedDocument, LegalClause, ClauseType
from services.modern_gemini_service import get_modern_gemini_service
from utils.text_processor import text_processor

logger = logging.getLogger(__name__)

class LegalAnalyzerAgent:
    def __init__(self):
        self.gemini_service = get_modern_gemini_service()
        
    async def analyze_document(self, processed_doc: ProcessedDocument) -> List[LegalClause]:
        """Analyze document and extract legal clauses"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting legal analysis for document {processed_doc.document_id}")
            
            # Step 1: Identify potential clauses using text processing
            potential_clauses = text_processor.identify_potential_clauses(processed_doc.extracted_text)
            
            logger.info(f"Found {len(potential_clauses)} potential clauses")
            
            # Step 2: Analyze each potential clause with Gemini
            legal_clauses = []
            
            # Process clauses in batches to avoid rate limits
            batch_size = 5
            for i in range(0, len(potential_clauses), batch_size):
                batch = potential_clauses[i:i + batch_size]
                
                # Process batch concurrently
                tasks = [
                    self._analyze_single_clause(clause, processed_doc.document_id, idx + i)
                    for idx, clause in enumerate(batch)
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter successful results
                for result in batch_results:
                    if isinstance(result, LegalClause):
                        legal_clauses.append(result)
                    elif isinstance(result, Exception):
                        logger.warning(f"Clause analysis failed: {str(result)}")
                
                # Small delay between batches to be respectful to API
                if i + batch_size < len(potential_clauses):
                    await asyncio.sleep(1)
            
            # Step 3: Post-process and validate clauses
            validated_clauses = self._validate_and_filter_clauses(legal_clauses)
            
            processing_time = time.time() - start_time
            
            logger.info(
                f"Legal analysis completed for {processed_doc.document_id}. "
                f"Analyzed {len(potential_clauses)} potential clauses, "
                f"extracted {len(validated_clauses)} valid legal clauses "
                f"in {processing_time:.2f} seconds"
            )
            
            return validated_clauses
            
        except Exception as e:
            logger.error(f"Legal analysis failed for {processed_doc.document_id}: {str(e)}")
            raise
    
    async def _analyze_single_clause(self, clause_info: Dict[str, Any], document_id: str, clause_index: int) -> LegalClause:
        """Analyze a single clause using Gemini"""
        try:
            clause_text = clause_info["text"]
            
            # Use Gemini to analyze the clause
            analysis_result = await self.gemini_service.analyze_legal_text(clause_text)
            
            # Create LegalClause object
            clause_id = f"{document_id}_{clause_index}_{str(uuid.uuid4())[:8]}"
            
            # Parse clause type
            try:
                clause_type = ClauseType(analysis_result["clause_type"])
            except ValueError:
                clause_type = ClauseType.OTHER
            
            legal_clause = LegalClause(
                clause_id=clause_id,
                clause_type=clause_type,
                original_text=clause_text,
                simplified_text=analysis_result.get("simplified_text", ""),
                risk_score=analysis_result.get("risk_score", 5),
                risk_explanation=analysis_result.get("risk_explanation", ""),
                section_number=self._extract_section_number(clause_text),
                page_number=None,  # Would need page mapping for this
                key_terms=analysis_result.get("key_terms", []),
                recommendations=analysis_result.get("recommendations", [])
            )
            
            return legal_clause
            
        except Exception as e:
            logger.error(f"Single clause analysis failed: {str(e)}")
            raise
    
    def _extract_section_number(self, clause_text: str) -> str:
        """Extract section number from clause text if present"""
        import re
        
        # Common section number patterns
        patterns = [
            r'^(\d+\.\d*)',  # 1.1, 1.2.3
            r'^(\d+)',  # 1, 2, 3
            r'^\((\d+)\)',  # (1), (2)
            r'^([A-Z])\.?\s',  # A., B.
            r'^\(([a-z])\)',  # (a), (b)
            r'Section\s+(\d+)',  # Section 1
            r'Article\s+(\d+)',  # Article 1
        ]
        
        first_line = clause_text.split('\n')[0].strip()
        
        for pattern in patterns:
            match = re.search(pattern, first_line, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _validate_and_filter_clauses(self, clauses: List[LegalClause]) -> List[LegalClause]:
        """Validate and filter clauses based on quality criteria"""
        validated_clauses = []
        
        for clause in clauses:
            # Quality checks
            if self._is_valid_clause(clause):
                validated_clauses.append(clause)
            else:
                logger.debug(f"Filtered out invalid clause: {clause.clause_id}")
        
        # Remove duplicates
        validated_clauses = self._remove_duplicate_clauses(validated_clauses)
        
        # Sort by importance (risk score and clause type)
        validated_clauses.sort(key=lambda x: (x.risk_score, self._get_clause_importance(x.clause_type)), reverse=True)
        
        return validated_clauses
    
    def _is_valid_clause(self, clause: LegalClause) -> bool:
        """Check if a clause meets quality criteria"""
        # Minimum text length
        if len(clause.original_text.strip()) < 50:
            return False
        
        # Must have some simplified text
        if not clause.simplified_text.strip():
            return False
        
        # Risk score must be valid
        if not (1 <= clause.risk_score <= 10):
            return False
        
        # Must have some meaningful content (not just headers or numbers)
        text_words = clause.original_text.lower().split()
        meaningful_words = [word for word in text_words if len(word) > 3 and word.isalpha()]
        if len(meaningful_words) < 5:
            return False
        
        return True
    
    def _remove_duplicate_clauses(self, clauses: List[LegalClause]) -> List[LegalClause]:
        """Remove duplicate or very similar clauses"""
        unique_clauses = []
        seen_texts = set()
        
        for clause in clauses:
            # Create a normalized version of the text for comparison
            normalized_text = ' '.join(clause.original_text.lower().split())
            
            # Check for exact duplicates
            if normalized_text in seen_texts:
                continue
            
            # Check for very similar clauses (>90% overlap)
            is_duplicate = False
            for seen_text in seen_texts:
                similarity = self._calculate_text_similarity(normalized_text, seen_text)
                if similarity > 0.9:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_clauses.append(clause)
                seen_texts.add(normalized_text)
        
        return unique_clauses
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity based on word overlap"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _get_clause_importance(self, clause_type: ClauseType) -> int:
        """Get importance score for clause type (higher = more important)"""
        importance_scores = {
            ClauseType.LIABILITY: 10,
            ClauseType.PAYMENT_TERMS: 9,
            ClauseType.TERMINATION: 8,
            ClauseType.INDEMNIFICATION: 7,
            ClauseType.INTELLECTUAL_PROPERTY: 6,
            ClauseType.CONFIDENTIALITY: 5,
            ClauseType.DISPUTE_RESOLUTION: 4,
            ClauseType.GOVERNING_LAW: 3,
            ClauseType.AMENDMENT: 2,
            ClauseType.SEVERABILITY: 1,
            ClauseType.OTHER: 0
        }
        
        return importance_scores.get(clause_type, 0)
    
    async def analyze_clause_relationships(self, clauses: List[LegalClause]) -> Dict[str, Any]:
        """Analyze relationships between clauses"""
        relationships = {
            "related_clauses": [],
            "conflicting_clauses": [],
            "clause_dependencies": []
        }
        
        # This would be a more sophisticated analysis
        # For now, just group by type
        clause_groups = {}
        for clause in clauses:
            clause_type = clause.clause_type.value
            if clause_type not in clause_groups:
                clause_groups[clause_type] = []
            clause_groups[clause_type].append(clause)
        
        # Identify groups with multiple clauses (potentially related)
        for clause_type, group_clauses in clause_groups.items():
            if len(group_clauses) > 1:
                relationships["related_clauses"].append({
                    "type": clause_type,
                    "clauses": [c.clause_id for c in group_clauses],
                    "description": f"Multiple {clause_type.replace('_', ' ')} clauses found"
                })
        
        return relationships
    
    def get_clause_statistics(self, clauses: List[LegalClause]) -> Dict[str, Any]:
        """Get statistics about analyzed clauses"""
        if not clauses:
            return {
                "total_clauses": 0,
                "clause_types": {},
                "risk_distribution": {},
                "average_risk_score": 0.0
            }
        
        # Clause type distribution
        clause_types = {}
        for clause in clauses:
            clause_type = clause.clause_type.value
            clause_types[clause_type] = clause_types.get(clause_type, 0) + 1
        
        # Risk distribution
        risk_distribution = {
            "low_risk": len([c for c in clauses if c.risk_score <= 3]),
            "medium_risk": len([c for c in clauses if 4 <= c.risk_score <= 6]),
            "high_risk": len([c for c in clauses if c.risk_score >= 7])
        }
        
        # Average risk score
        avg_risk = sum(c.risk_score for c in clauses) / len(clauses)
        
        return {
            "total_clauses": len(clauses),
            "clause_types": clause_types,
            "risk_distribution": risk_distribution,
            "average_risk_score": round(avg_risk, 2),
            "highest_risk_clause": max(clauses, key=lambda x: x.risk_score).clause_id,
            "most_common_type": max(clause_types, key=clause_types.get) if clause_types else None
        }