"""CrewAI Integration for LegalClarity AI

This module provides CrewAI integration with 5 specialized legal expert agents:
1. Legal Research Specialist - Research precedents and case law
2. Consumer Protection Advocate - Identify unfair practices
3. Regulatory Compliance Expert - Check legal compliance
4. Contract Negotiation Advisor - Provide negotiation strategies
5. Alternative Solutions Finder - Research better alternatives

Usage:
    from crew.enhanced_orchestrator import EnhancedOrchestrator
    
    orchestrator = EnhancedOrchestrator(base_orchestrator)
    result = await orchestrator.process_document(file_path, doc_id, status)
"""

__version__ = "1.0.0"
__author__ = "LegalClarity AI Team"

from .enhanced_orchestrator import EnhancedOrchestrator, CrewAILegalTeam

__all__ = [
    "EnhancedOrchestrator",
    "CrewAILegalTeam"
]