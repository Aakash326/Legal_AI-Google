# backend/agents/crew_agents.py
"""
CrewAI agents that complement the existing LegalClarity AI architecture.
These agents work alongside your current document_processor, legal_analyzer, etc.
"""

from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
import json
from datetime import datetime

# Initialize Gemini LLM for CrewAI
def get_gemini_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.1,
        max_tokens=2048
    )

class LegalExpertiseTools:
    """Custom tools for CrewAI agents to interact with your existing services"""
    
    @staticmethod
    def create_document_research_tool(gemini_service):
        """Tool for researching legal precedents and case law"""
        def research_legal_precedent(clause_text: str) -> str:
            prompt = f"""
            Research legal precedents and case law related to this clause:
            {clause_text}
            
            Provide:
            1. Similar cases or legal precedents
            2. Common interpretations in courts
            3. Consumer protection aspects
            4. Industry standard practices
            """
            return gemini_service.generate_content(prompt)
        
        return Tool(
            name="legal_precedent_research",
            description="Research legal precedents and case law for specific clauses",
            func=research_legal_precedent
        )
    
    @staticmethod
    def create_compliance_check_tool(gemini_service):
        """Tool for checking regulatory compliance"""
        def check_compliance(document_text: str, jurisdiction: str = "US") -> str:
            prompt = f"""
            Check this document for compliance with consumer protection laws in {jurisdiction}:
            {document_text[:1000]}...
            
            Focus on:
            1. Fair Credit Reporting Act violations
            2. Truth in Lending Act compliance
            3. Fair Housing Act compliance
            4. State-specific consumer protection laws
            """
            return gemini_service.generate_content(prompt)
        
        return Tool(
            name="compliance_checker",
            description="Check document compliance with consumer protection laws",
            func=check_compliance
        )

class CrewAILegalTeam:
    """
    5 CrewAI agents that complement your existing architecture
    """
    
    def __init__(self, gemini_service, vertex_ai_service):
        self.gemini_service = gemini_service
        self.vertex_ai_service = vertex_ai_service
        self.llm = get_gemini_llm()
        self.tools = self._initialize_tools()
        self.agents = self._create_agents()
        self.crew = self._create_crew()
    
    def _initialize_tools(self):
        """Initialize custom tools for agents"""
        return {
            'legal_research': LegalExpertiseTools.create_document_research_tool(self.gemini_service),
            'compliance_check': LegalExpertiseTools.create_compliance_check_tool(self.gemini_service),
        }
    
    def _create_agents(self):
        """Create 5 specialized CrewAI agents"""
        
        # AGENT 1: Legal Research Specialist
        legal_researcher = Agent(
            role='Senior Legal Research Specialist',
            goal='Research legal precedents, case law, and regulatory context for document clauses',
            backstory="""You are a senior legal researcher with 20 years of experience in case law analysis. 
            You specialize in finding relevant legal precedents, understanding how courts have interpreted 
            similar clauses, and identifying potential legal challenges. You work closely with the existing 
            legal analyzer to provide deeper context and historical perspective.""",
            llm=self.llm,
            tools=[self.tools['legal_research']],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        # AGENT 2: Consumer Protection Advocate  
        consumer_advocate = Agent(
            role='Consumer Protection Advocate',
            goal='Identify consumer rights violations and unfair practices in legal documents',
            backstory="""You are a passionate consumer rights advocate who has worked with legal aid societies 
            for 15 years. You specialize in identifying clauses that unfairly disadvantage consumers, violate 
            consumer protection laws, or create unreasonable burdens. You complement the risk assessor by 
            focusing specifically on consumer welfare and fair dealing.""",
            llm=self.llm,
            tools=[self.tools['compliance_check']],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        # AGENT 3: Regulatory Compliance Expert
        compliance_expert = Agent(
            role='Regulatory Compliance Expert',
            goal='Ensure documents comply with federal and state regulations',
            backstory="""You are a regulatory compliance expert with deep knowledge of consumer protection laws, 
            fair lending practices, housing regulations, and employment law. You have 18 years of experience 
            helping organizations navigate complex regulatory environments. You work with existing analyzers to 
            identify potential compliance issues.""",
            llm=self.llm,
            tools=[self.tools['compliance_check']],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        # AGENT 4: Negotiation Strategy Advisor
        negotiation_advisor = Agent(
            role='Contract Negotiation Strategy Advisor',
            goal='Provide strategic advice on negotiating better terms and identifying leverage points',
            backstory="""You are a seasoned contract negotiation expert who has helped thousands of individuals 
            and small businesses negotiate better deals. You understand power dynamics in contracts and can 
            identify which terms are typically negotiable vs. non-negotiable. You provide practical advice 
            that complements the existing analysis with actionable negotiation strategies.""",
            llm=self.llm,
            tools=[],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        # AGENT 5: Alternative Solutions Finder
        solutions_finder = Agent(
            role='Alternative Solutions Research Specialist',
            goal='Find alternative products, services, or contract terms that better serve the user',
            backstory="""You are a market research specialist who excels at finding alternatives to unfavorable 
            contracts. You have extensive knowledge of different service providers, contract structures, and 
            market options. When the existing analyzers identify problematic terms, you research and suggest 
            better alternatives available in the market.""",
            llm=self.llm,
            tools=[],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        return {
            'researcher': legal_researcher,
            'advocate': consumer_advocate, 
            'compliance': compliance_expert,
            'negotiator': negotiation_advisor,
            'solutions': solutions_finder
        }
    
    def _create_crew(self):
        """Create CrewAI crew with defined workflow"""
        return Crew(
            agents=list(self.agents.values()),
            verbose=2,
            memory=True,
            embedder={
                "provider": "google", 
                "config": {"model": "models/embedding-001"}
            }
        )
    
    async def enhance_legal_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method that enhances existing analysis with CrewAI insights
        This works with your existing orchestrator output
        """
        
        document_text = analysis_result.get('document_text', '')
        key_clauses = analysis_result.get('key_clauses', [])
        risk_assessment = analysis_result.get('risk_assessment', {})
        
        # Task 1: Legal Research on High-Risk Clauses
        research_task = Task(
            description=f"""
            Research legal precedents for the highest-risk clauses identified:
            {[clause for clause in key_clauses if clause.get('risk_score', 0) >= 7]}
            
            Provide:
            1. Relevant case law and precedents
            2. How courts typically interpret these clauses
            3. Consumer success stories in challenging similar terms
            4. Legal theories that could be used to contest unfair clauses
            """,
            agent=self.agents['researcher'],
            expected_output="Detailed legal research report with precedents and case law analysis"
        )
        
        # Task 2: Consumer Protection Analysis
        consumer_task = Task(
            description=f"""
            Analyze document for consumer rights violations:
            Document summary: {analysis_result.get('summary', '')}
            Risk assessment: {risk_assessment}
            
            Focus on:
            1. Unfair or deceptive practices
            2. Violations of consumer protection laws
            3. Unconscionable contract terms
            4. Hidden fees or costs
            """,
            agent=self.agents['advocate'],
            expected_output="Consumer protection violation report with specific law citations"
        )
        
        # Task 3: Regulatory Compliance Check
        compliance_task = Task(
            description=f"""
            Check document for regulatory compliance issues:
            Document type: {analysis_result.get('document_type', '')}
            Key clauses: {key_clauses}
            
            Verify compliance with:
            1. Federal consumer protection laws
            2. State-specific regulations  
            3. Industry-specific requirements
            4. Fair dealing standards
            """,
            agent=self.agents['compliance'],
            expected_output="Regulatory compliance assessment with violation risks"
        )
        
        # Task 4: Negotiation Strategy
        negotiation_task = Task(
            description=f"""
            Develop negotiation strategies for problematic clauses:
            High-risk clauses: {[c for c in key_clauses if c.get('risk_score', 0) >= 6]}
            
            Provide:
            1. Which terms are typically negotiable
            2. Leverage points for the consumer
            3. Alternative language suggestions
            4. Walking-away triggers
            """,
            agent=self.agents['negotiator'],
            expected_output="Practical negotiation strategy guide with specific tactics"
        )
        
        # Task 5: Alternative Solutions
        alternatives_task = Task(
            description=f"""
            Research alternatives to this contract/service:
            Document type: {analysis_result.get('document_type', '')}
            Problematic terms: {[c['simplified_explanation'] for c in key_clauses if c.get('risk_score', 0) >= 7]}
            
            Find:
            1. Better service providers with fairer terms
            2. Alternative contract structures
            3. Consumer-friendly options in the market
            4. Government or non-profit alternatives
            """,
            agent=self.agents['solutions'],
            expected_output="List of alternative solutions with comparative analysis"
        )
        
        # Execute CrewAI workflow
        crew_tasks = [research_task, consumer_task, compliance_task, negotiation_task, alternatives_task]
        
        try:
            crew_results = await self._execute_crew_tasks(crew_tasks)
            
            # Enhance original analysis with CrewAI insights
            enhanced_analysis = analysis_result.copy()
            enhanced_analysis.update({
                'legal_research': crew_results.get('legal_research', ''),
                'consumer_protection_analysis': crew_results.get('consumer_analysis', ''),
                'regulatory_compliance': crew_results.get('compliance_check', ''),
                'negotiation_strategies': crew_results.get('negotiation_advice', ''),
                'alternatives': crew_results.get('alternative_solutions', ''),
                'crew_ai_enhanced': True,
                'enhancement_timestamp': datetime.now().isoformat()
            })
            
            return enhanced_analysis
            
        except Exception as e:
            print(f"CrewAI enhancement failed: {e}")
            # Return original analysis if CrewAI fails
            return analysis_result
    
    async def _execute_crew_tasks(self, tasks: List[Task]) -> Dict[str, Any]:
        """Execute CrewAI tasks and return structured results"""
        
        # For now, execute tasks individually
        # In production, you might want more sophisticated coordination
        results = {}
        
        for task in tasks:
            try:
                # Create temporary crew for each task
                task_crew = Crew(
                    agents=[task.agent],
                    tasks=[task],
                    verbose=1
                )
                
                result = task_crew.kickoff()
                
                # Map results based on agent type
                if task.agent.role == 'Senior Legal Research Specialist':
                    results['legal_research'] = str(result)
                elif task.agent.role == 'Consumer Protection Advocate':
                    results['consumer_analysis'] = str(result)
                elif task.agent.role == 'Regulatory Compliance Expert':
                    results['compliance_check'] = str(result)
                elif task.agent.role == 'Contract Negotiation Strategy Advisor':
                    results['negotiation_advice'] = str(result)
                elif task.agent.role == 'Alternative Solutions Research Specialist':
                    results['alternative_solutions'] = str(result)
                    
            except Exception as e:
                print(f"Task execution failed for {task.agent.role}: {e}")
                continue
        
        return results
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get status of CrewAI agents"""
        return {
            'crew_initialized': True,
            'agents_count': len(self.agents),
            'agents': [agent.role for agent in self.agents.values()],
            'tools_available': list(self.tools.keys()),
            'memory_enabled': True
        }

# Integration with existing orchestrator
class EnhancedOrchestrator:
    """
    Enhanced orchestrator that integrates CrewAI with your existing agents
    """
    
    def __init__(self, existing_orchestrator, gemini_service, vertex_ai_service):
        self.existing_orchestrator = existing_orchestrator
        self.crew_team = CrewAILegalTeam(gemini_service, vertex_ai_service)
    
    async def process_document_with_crew(self, document_path: str, user_id: str, 
                                       use_crew_enhancement: bool = True) -> Dict[str, Any]:
        """
        Process document using existing pipeline + CrewAI enhancement
        """
        
        # Step 1: Use your existing orchestrator for core analysis
        base_analysis = await self.existing_orchestrator.process_document(document_path, user_id)
        
        # Step 2: If CrewAI enhancement requested, add expert insights
        if use_crew_enhancement:
            try:
                enhanced_analysis = await self.crew_team.enhance_legal_analysis(base_analysis)
                enhanced_analysis['enhancement_used'] = 'crew_ai'
                return enhanced_analysis
            except Exception as e:
                print(f"CrewAI enhancement failed, returning base analysis: {e}")
                base_analysis['enhancement_used'] = 'none'
                return base_analysis
        else:
            base_analysis['enhancement_used'] = 'none'
            return base_analysis

# Usage example for your main.py:
"""
# In your main.py, replace the orchestrator initialization:

# OLD:
# orchestrator = OrchestratorAgent(...)

# NEW:
base_orchestrator = OrchestratorAgent(...)
enhanced_orchestrator = EnhancedOrchestrator(
    base_orchestrator, 
    gemini_service, 
    vertex_ai_service
)

# Use enhanced processing:
result = await enhanced_orchestrator.process_document_with_crew(
    document_path="path/to/document.pdf",
    user_id="user123",
    use_crew_enhancement=True
)
"""