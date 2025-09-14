from crewai import Task
from typing import Dict, List, Any
from datetime import datetime

class LegalTaskFactory:
    """Factory class to create tasks for CrewAI agents"""
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
    
    def create_research_task(self, high_risk_clauses: List[Dict]) -> Task:
        """Create legal research task"""
        high_risk_text = "\n".join([f"- {clause.get('clause_type', 'Unknown')}: {clause.get('original_text', '')[:200]}..." 
                                   for clause in high_risk_clauses[:3]])
        
        return Task(
            description=f"""
            Research legal precedents for the highest-risk clauses identified in this document:
            
            HIGH-RISK CLAUSES:
            {high_risk_text}
            
            Your research should include:
            1. Relevant case law and precedents for similar clauses
            2. How courts typically interpret these types of clauses
            3. Consumer success stories in challenging similar terms
            4. Legal theories that could be used to contest unfair clauses
            5. Recent regulatory guidance on these clause types
            6. State vs. federal law differences that might apply
            
            Provide specific case citations and legal authorities where possible.
            Focus on precedents that would benefit the consumer's position.
            """,
            agent=self.agents['researcher'],
            expected_output="""Detailed legal research report containing:
            - Specific case law citations relevant to each clause type
            - Court interpretation patterns and trends
            - Consumer protection precedents
            - Actionable legal theories for challenging unfair terms
            - Regulatory guidance and recent developments
            - Jurisdiction-specific considerations"""
        )
    
    def create_consumer_protection_task(self, document_summary: str, risk_assessment: Dict) -> Task:
        """Create consumer protection analysis task"""
        return Task(
            description=f"""
            Analyze this document for consumer rights violations and unfair practices:
            
            DOCUMENT SUMMARY: {document_summary}
            OVERALL RISK SCORE: {risk_assessment.get('overall_risk', 'Unknown')}
            HIGH-RISK AREAS: {risk_assessment.get('high_risk_clauses', [])}
            
            Focus your analysis on:
            1. Unfair or deceptive practices under FTC Act
            2. Violations of specific consumer protection laws
            3. Unconscionable contract terms
            4. Hidden fees, costs, or penalties
            5. Misleading language or buried terms
            6. Power imbalances that disadvantage consumers
            7. Lack of required disclosures
            8. Terms that waive important consumer rights
            
            Evaluate each violation for:
            - Severity level (minor, moderate, serious)
            - Legal remedy options available to consumers
            - Regulatory enforcement potential
            - Class action lawsuit potential
            """,
            agent=self.agents['advocate'],
            expected_output="""Consumer protection violation assessment including:
            - Specific law violations with citations
            - Unfair practice identification and analysis
            - Severity rankings for each violation
            - Available consumer remedies and rights
            - Enforcement mechanism recommendations
            - Red flags requiring immediate attention"""
        )
    
    def create_compliance_task(self, document_type: str, key_clauses: List[Dict]) -> Task:
        """Create regulatory compliance check task"""
        clause_summary = "\n".join([f"- {clause.get('clause_type', 'Unknown')}: Risk Score {clause.get('risk_score', 'N/A')}" 
                                   for clause in key_clauses[:5]])
        
        return Task(
            description=f"""
            Perform comprehensive regulatory compliance check for this {document_type} document:
            
            KEY CLAUSES IDENTIFIED:
            {clause_summary}
            
            Verify compliance with applicable regulations:
            
            FEDERAL LAWS:
            1. Fair Credit Reporting Act (FCRA) - if credit-related
            2. Truth in Lending Act (TILA) - if lending/credit terms
            3. Fair Debt Collection Practices Act (FDCPA) - if debt collection
            4. Fair Housing Act (FHA) - if housing/rental related
            5. Equal Credit Opportunity Act (ECOA) - if credit decisions
            6. Electronic Signatures in Global Commerce Act (ESIGN)
            7. Consumer Financial Protection Bureau (CFPB) regulations
            
            STATE LAWS:
            1. State consumer protection acts
            2. State disclosure requirements
            3. State usury laws and interest rate caps
            4. State landlord-tenant laws (if applicable)
            5. State employment laws (if applicable)
            
            INDUSTRY-SPECIFIC:
            1. Industry-specific regulatory requirements
            2. Professional licensing board requirements
            3. Trade association best practices
            
            For each potential violation, identify:
            - Specific regulatory citation
            - Risk level (low, moderate, high, critical)
            - Potential penalties or enforcement actions
            - Required corrective actions
            """,
            agent=self.agents['compliance'],
            expected_output="""Comprehensive regulatory compliance assessment with:
            - Federal law compliance analysis with specific citations
            - State law compliance review
            - Industry-specific requirement verification
            - Violation risk ratings (low/moderate/high/critical)
            - Specific corrective action recommendations
            - Regulatory enforcement risk assessment"""
        )
    
    def create_negotiation_task(self, high_risk_clauses: List[Dict], document_type: str) -> Task:
        """Create negotiation strategy task"""
        problematic_terms = "\n".join([f"- {clause.get('clause_type', 'Unknown')} (Risk: {clause.get('risk_score', 'N/A')}): {clause.get('risk_explanation', '')[:150]}..." 
                                      for clause in high_risk_clauses[:4]])
        
        return Task(
            description=f"""
            Develop comprehensive negotiation strategies for this {document_type} with problematic clauses:
            
            PROBLEMATIC TERMS TO ADDRESS:
            {problematic_terms}
            
            Create negotiation guidance covering:
            
            NEGOTIABILITY ANALYSIS:
            1. Which terms are typically negotiable vs. non-negotiable
            2. Industry standards for each clause type
            3. Common variations and alternatives
            4. Precedent for successful negotiations
            
            LEVERAGE IDENTIFICATION:
            1. Consumer leverage points (market competition, alternatives, etc.)
            2. Timing advantages (contract renewal, market conditions)
            3. Regulatory compliance leverage
            4. Reputational considerations for the other party
            
            STRATEGY DEVELOPMENT:
            1. Specific alternative language proposals
            2. Compromise positions that reduce risk
            3. Deal-breaker identification (when to walk away)
            4. Negotiation sequence and timing
            5. Supporting documentation needed
            
            TACTICAL APPROACHES:
            1. How to initiate the negotiation conversation
            2. Framing strategies that emphasize mutual benefit
            3. Handling pushback and resistance
            4. When to escalate to supervisors or legal counsel
            5. Documentation and follow-up protocols
            
            Focus on practical, actionable advice that an average consumer can implement.
            """,
            agent=self.agents['negotiator'],
            expected_output="""Practical negotiation strategy guide containing:
            - Negotiability assessment for each problematic clause
            - Specific alternative language proposals
            - Consumer leverage points and timing strategies
            - Step-by-step negotiation playbook
            - Deal-breaker criteria and walking-away triggers
            - Scripts and conversation starters
            - Success metrics and follow-up actions"""
        )
    
    def create_alternatives_task(self, document_type: str, problematic_terms: List[str], overall_risk: float) -> Task:
        """Create alternative solutions research task"""
        problems_text = "\n".join([f"- {term}" for term in problematic_terms[:5]])
        
        return Task(
            description=f"""
            Research comprehensive alternatives to this {document_type} with overall risk score of {overall_risk:.1f}:
            
            MAIN PROBLEMS IDENTIFIED:
            {problems_text}
            
            Research and recommend alternatives across these categories:
            
            ALTERNATIVE SERVICE PROVIDERS:
            1. Competitors with better terms and fairer contracts
            2. Consumer-friendly companies with transparent practices
            3. Credit unions, non-profits, or cooperative alternatives
            4. Government programs or public alternatives
            5. Peer-to-peer or sharing economy options
            
            ALTERNATIVE CONTRACT STRUCTURES:
            1. Different contract types that achieve similar goals
            2. Shorter-term or more flexible arrangements
            3. Performance-based or outcome-focused agreements
            4. Subscription vs. ownership models
            5. Cooperative or community-based approaches
            
            ALTERNATIVE SOLUTIONS:
            1. DIY or self-service options
            2. Professional service alternatives
            3. Technology-based solutions
            4. Community resources and support networks
            5. Regulatory or legal remedies
            
            For each alternative, provide:
            1. Specific company/option names where possible
            2. How it addresses the identified problems
            3. Trade-offs and limitations
            4. Cost comparisons
            5. Ease of transition or implementation
            6. Long-term benefits and risks
            
            Prioritize realistic, accessible alternatives that typical consumers can pursue.
            """,
            agent=self.agents['solutions'],
            expected_output="""Comprehensive alternatives research report with:
            - Specific alternative service providers and contact information
            - Alternative contract structures and approaches
            - Creative solutions and workarounds
            - Cost-benefit analysis for each option
            - Implementation difficulty and timeline assessments
            - Ranked recommendations based on consumer benefit
            - Transition strategies and next steps"""
        )
    
    def create_all_tasks(self, analysis_result: Dict[str, Any]) -> List[Task]:
        """Create all tasks based on analysis result"""
        # Extract data from analysis result
        high_risk_clauses = [clause for clause in analysis_result.get('key_clauses', []) 
                           if clause.get('risk_score', 0) >= 7]
        
        document_summary = analysis_result.get('document_summary', {})
        document_type = analysis_result.get('document_type', 'unknown')
        risk_assessment = {
            'overall_risk': analysis_result.get('overall_risk_score', 5.0),
            'high_risk_clauses': [clause.get('clause_id') for clause in high_risk_clauses]
        }
        
        problematic_terms = [clause.get('risk_explanation', '')[:100] for clause in high_risk_clauses]
        
        # Create all tasks
        tasks = [
            self.create_research_task(high_risk_clauses),
            self.create_consumer_protection_task(str(document_summary), risk_assessment),
            self.create_compliance_task(document_type, analysis_result.get('key_clauses', [])),
            self.create_negotiation_task(high_risk_clauses, document_type),
            self.create_alternatives_task(document_type, problematic_terms, risk_assessment['overall_risk'])
        ]
        
        return tasks