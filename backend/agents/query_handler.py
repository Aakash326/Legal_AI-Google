import time
from typing import List, Dict, Any
import logging
import re

from models.document import LegalClause, ClauseType
from models.analysis import QueryResult
from services.gemini_service import get_gemini_service
from utils.text_processor import text_processor

logger = logging.getLogger(__name__)

class QueryHandlerAgent:
    def __init__(self):
        self.gemini_service = get_gemini_service()
        
        # Common question patterns and their associated clause types
        self.question_patterns = {
            r'(payment|pay|fee|cost|money|charge|bill)': [ClauseType.PAYMENT_TERMS],
            r'(terminat|end|cancel|break|exit|quit)': [ClauseType.TERMINATION],
            r'(liability|liable|responsible|damage|fault)': [ClauseType.LIABILITY],
            r'(confidential|secret|private|disclosure)': [ClauseType.CONFIDENTIALITY],
            r'(intellectual property|copyright|trademark|patent)': [ClauseType.INTELLECTUAL_PROPERTY],
            r'(dispute|conflict|disagree|arbitrat|court|legal)': [ClauseType.DISPUTE_RESOLUTION],
            r'(law|jurisdiction|govern|legal)': [ClauseType.GOVERNING_LAW],
            r'(change|modify|amend|alter)': [ClauseType.AMENDMENT],
            r'(indemnif|hold harmless|protect)': [ClauseType.INDEMNIFICATION]
        }
    
    async def handle_query(self, query: str, document_id: str, document_text: str, legal_clauses: List[LegalClause]) -> QueryResult:
        """Handle a user query about the document"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing query for document {document_id}: {query[:100]}...")
            
            # Step 1: Find relevant clauses based on query
            relevant_clauses = self._find_relevant_clauses(query, legal_clauses)
            
            # Step 2: Extract relevant context from document
            relevant_context = self._extract_relevant_context(query, document_text, relevant_clauses)
            
            # Step 3: Generate answer using Gemini
            answer_data = await self._generate_answer(query, relevant_context, relevant_clauses)
            
            # Step 4: Calculate confidence score
            confidence = self._calculate_confidence(query, relevant_clauses, answer_data)
            
            # Step 5: Prepare sources
            sources = self._prepare_sources(relevant_clauses)
            
            processing_time = time.time() - start_time
            
            result = QueryResult(
                query=query,
                answer=answer_data.get("answer", "I couldn't find a clear answer to your question."),
                confidence=confidence,
                relevant_clauses=[clause.clause_id for clause in relevant_clauses],
                sources=sources,
                document_id=document_id
            )
            
            logger.info(
                f"Query processed in {processing_time:.2f}s. "
                f"Found {len(relevant_clauses)} relevant clauses, "
                f"confidence: {confidence:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Query handling failed: {str(e)}")
            raise
    
    def _find_relevant_clauses(self, query: str, legal_clauses: List[LegalClause]) -> List[LegalClause]:
        """Find clauses relevant to the user's query"""
        query_lower = query.lower()
        
        # Score clauses based on relevance
        clause_scores = []
        
        for clause in legal_clauses:
            score = 0.0
            
            # Score based on clause type matching query patterns
            for pattern, clause_types in self.question_patterns.items():
                if re.search(pattern, query_lower):
                    if clause.clause_type in clause_types:
                        score += 3.0
                    elif any(keyword in clause.original_text.lower() for keyword in re.findall(r'\w+', pattern)):
                        score += 1.0
            
            # Score based on keyword overlap
            query_keywords = set(re.findall(r'\b\w+\b', query_lower))
            clause_keywords = set(re.findall(r'\b\w+\b', clause.original_text.lower()))
            
            # Remove common words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall'}
            query_keywords -= common_words
            clause_keywords -= common_words
            
            if query_keywords and clause_keywords:
                overlap = len(query_keywords.intersection(clause_keywords))
                score += overlap / len(query_keywords) * 2.0
            
            # Boost score for high-risk clauses (they're often important)
            if clause.risk_score >= 7:
                score += 0.5
            
            # Score based on simplified text match (often clearer)
            if clause.simplified_text:
                simplified_keywords = set(re.findall(r'\b\w+\b', clause.simplified_text.lower())) - common_words
                if query_keywords and simplified_keywords:
                    overlap = len(query_keywords.intersection(simplified_keywords))
                    score += overlap / len(query_keywords) * 1.5
            
            clause_scores.append((clause, score))
        
        # Sort by score and return top relevant clauses
        clause_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return clauses with score > 0.5, up to 5 clauses
        relevant_clauses = [clause for clause, score in clause_scores if score > 0.5][:5]
        
        # If no relevant clauses found, return top 2 highest scoring
        if not relevant_clauses and clause_scores:
            relevant_clauses = [clause_scores[0][0]]
            if len(clause_scores) > 1:
                relevant_clauses.append(clause_scores[1][0])
        
        logger.debug(f"Found {len(relevant_clauses)} relevant clauses for query")
        return relevant_clauses
    
    def _extract_relevant_context(self, query: str, document_text: str, relevant_clauses: List[LegalClause]) -> str:
        """Extract relevant context from the document"""
        # Use the text from relevant clauses as primary context
        context_parts = []
        
        # Add clause text
        for clause in relevant_clauses:
            context_parts.append(f"[{clause.clause_type.value.replace('_', ' ').title()}] {clause.original_text}")
        
        # Add some surrounding context from the document if needed
        query_keywords = set(re.findall(r'\b\w+\b', query.lower()))
        
        # Find additional relevant sentences from the document
        sentences = re.split(r'[.!?]+', document_text)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
                
            sentence_keywords = set(re.findall(r'\b\w+\b', sentence.lower()))
            
            # Check for keyword overlap
            if query_keywords and sentence_keywords:
                overlap = len(query_keywords.intersection(sentence_keywords))
                if overlap >= 2:  # At least 2 keywords match
                    # Check if this sentence is not already in clause text
                    is_duplicate = any(sentence.lower() in clause.original_text.lower() for clause in relevant_clauses)
                    if not is_duplicate:
                        relevant_sentences.append(sentence)
        
        # Add top relevant sentences (limit to avoid too much context)
        if relevant_sentences:
            context_parts.extend(relevant_sentences[:3])
        
        # Combine all context
        full_context = '\n\n'.join(context_parts)
        
        # Limit context size for API
        if len(full_context) > 3000:
            full_context = full_context[:3000] + "..."
        
        return full_context
    
    async def _generate_answer(self, query: str, context: str, relevant_clauses: List[LegalClause]) -> Dict[str, Any]:
        """Generate answer using Gemini"""
        try:
            # Prepare clause summaries for context
            clause_summaries = []
            for clause in relevant_clauses:
                summary = f"- {clause.clause_type.value.replace('_', ' ').title()}: {clause.simplified_text[:200]}"
                if clause.risk_score >= 7:
                    summary += " [HIGH RISK]"
                clause_summaries.append(summary)
            
            # Use Gemini to answer the query
            answer_data = await self.gemini_service.answer_query(
                document_context=context,
                relevant_clauses=clause_summaries,
                query=query
            )
            
            return answer_data
            
        except Exception as e:
            logger.error(f"Answer generation failed: {str(e)}")
            return {
                "answer": "I'm having trouble generating an answer right now. Please try rephrasing your question.",
                "confidence": 0.1,
                "sources_used": []
            }
    
    def _calculate_confidence(self, query: str, relevant_clauses: List[LegalClause], answer_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the answer"""
        confidence = answer_data.get("confidence", 0.5)
        
        # Adjust based on number of relevant clauses
        if len(relevant_clauses) >= 3:
            confidence += 0.1
        elif len(relevant_clauses) == 0:
            confidence -= 0.3
        
        # Adjust based on query specificity
        query_words = len(query.split())
        if query_words >= 8:  # Specific question
            confidence += 0.1
        elif query_words <= 3:  # Very general question
            confidence -= 0.1
        
        # Adjust based on clause types (some are more definitive)
        definitive_types = {ClauseType.PAYMENT_TERMS, ClauseType.TERMINATION, ClauseType.GOVERNING_LAW}
        has_definitive = any(clause.clause_type in definitive_types for clause in relevant_clauses)
        if has_definitive:
            confidence += 0.1
        
        # Ensure confidence is in valid range
        return max(0.0, min(1.0, confidence))
    
    def _prepare_sources(self, relevant_clauses: List[LegalClause]) -> List[str]:
        """Prepare source citations for the answer"""
        sources = []
        
        for clause in relevant_clauses:
            source = f"{clause.clause_type.value.replace('_', ' ').title()}"
            
            if clause.section_number:
                source += f" (Section {clause.section_number})"
            
            # Add snippet of original text
            snippet = clause.original_text[:150]
            if len(clause.original_text) > 150:
                snippet += "..."
            
            source += f": {snippet}"
            sources.append(source)
        
        return sources
    
    def suggest_related_questions(self, document_text: str, legal_clauses: List[LegalClause]) -> List[str]:
        """Suggest related questions based on document content"""
        suggestions = []
        
        # Get clause types present in document
        clause_types = set(clause.clause_type for clause in legal_clauses)
        
        # Standard questions based on clause types
        if ClauseType.PAYMENT_TERMS in clause_types:
            suggestions.extend([
                "What are the payment terms and due dates?",
                "Are there any late fees or penalties?",
                "What payment methods are accepted?"
            ])
        
        if ClauseType.TERMINATION in clause_types:
            suggestions.extend([
                "How can this agreement be terminated?",
                "What happens if I need to end this early?",
                "Are there any termination penalties?"
            ])
        
        if ClauseType.LIABILITY in clause_types:
            suggestions.extend([
                "What am I liable for under this agreement?",
                "What are the limits on liability?",
                "What damages could I be responsible for?"
            ])
        
        if ClauseType.CONFIDENTIALITY in clause_types:
            suggestions.extend([
                "What information must be kept confidential?",
                "How long do confidentiality obligations last?"
            ])
        
        if ClauseType.DISPUTE_RESOLUTION in clause_types:
            suggestions.extend([
                "How are disputes resolved?",
                "Is arbitration required for disagreements?"
            ])
        
        # High-risk clause questions
        high_risk_clauses = [c for c in legal_clauses if c.risk_score >= 7]
        if high_risk_clauses:
            suggestions.append("What are the highest risk terms in this document?")
        
        # Remove duplicates and limit
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:8]
    
    def get_query_statistics(self, queries: List[QueryResult]) -> Dict[str, Any]:
        """Get statistics about processed queries"""
        if not queries:
            return {
                "total_queries": 0,
                "average_confidence": 0.0,
                "common_topics": []
            }
        
        # Calculate average confidence
        avg_confidence = sum(q.confidence for q in queries) / len(queries)
        
        # Identify common topics/keywords
        all_queries_text = ' '.join(q.query for q in queries).lower()
        words = re.findall(r'\b\w+\b', all_queries_text)
        
        # Count word frequency (excluding common words)
        common_words = {'what', 'how', 'when', 'where', 'why', 'who', 'can', 'will', 'would', 'could', 'should', 'do', 'does', 'did', 'is', 'are', 'was', 'were', 'the', 'a', 'an', 'and', 'or', 'but'}
        filtered_words = [word for word in words if word not in common_words and len(word) > 3]
        
        word_counts = {}
        for word in filtered_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top topics
        common_topics = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_queries": len(queries),
            "average_confidence": round(avg_confidence, 2),
            "high_confidence_queries": len([q for q in queries if q.confidence >= 0.8]),
            "low_confidence_queries": len([q for q in queries if q.confidence < 0.5]),
            "common_topics": [f"{word} ({count})" for word, count in common_topics]
        }