import asyncio
import time
from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime

from crewai import Crew
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.orchestrator import OrchestratorAgent
from models.analysis import DocumentAnalysis
from services.modern_gemini_service import get_modern_gemini_service
from services.vertex_ai_service import get_vertex_ai_service

# Import CrewAI components
from crew.agents.legal_researcher import LegalResearcherAgent
from crew.agents.consumer_advocate import ConsumerAdvocateAgent
from crew.agents.compliance_expert import ComplianceExpertAgent
from crew.agents.negotiation_advisor import NegotiationAdvisorAgent
from crew.agents.solutions_finder import SolutionsFinderAgent
from crew.tasks.legal_tasks import LegalTaskFactory

logger = logging.getLogger(__name__)

class CrewAILegalTeam:
    """CrewAI team with 5 specialized legal agents"""
    
    def __init__(self, gemini_service, vertex_ai_service=None):
        self.gemini_service = gemini_service
        self.vertex_ai_service = vertex_ai_service
        
        # Initialize LLM for CrewAI
        self.llm = self._initialize_llm()
        
        # Create agents
        self.agents = self._create_agents()
        
        # Task factory
        self.task_factory = LegalTaskFactory(self.agents)
        
        logger.info("CrewAI Legal Team initialized with 5 specialized agents")
    
    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize Gemini LLM for CrewAI"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment")
            
            return ChatGoogleGenerativeAI(
                model=os.getenv("CREWAI_MODEL", "gemini-1.5-pro"),
                temperature=float(os.getenv("CREWAI_TEMPERATURE", "0.1")),
                max_tokens=int(os.getenv("CREWAI_MAX_TOKENS", "2048")),
                google_api_key=api_key
            )
        except Exception as e:
            logger.error(f"Failed to initialize CrewAI LLM: {str(e)}")
            raise
    
    def _create_agents(self) -> Dict[str, Any]:
        """Create all CrewAI agents"""
        try:
            agents = {
                'researcher': LegalResearcherAgent(self.gemini_service, self.llm).get_agent(),
                'advocate': ConsumerAdvocateAgent(self.gemini_service, self.llm).get_agent(),
                'compliance': ComplianceExpertAgent(self.gemini_service, self.llm).get_agent(),
                'negotiator': NegotiationAdvisorAgent(self.gemini_service, self.llm).get_agent(),
                'solutions': SolutionsFinderAgent(self.gemini_service, self.llm).get_agent()
            }
            
            logger.info(f"Created {len(agents)} CrewAI agents: {list(agents.keys())}")
            return agents
            
        except Exception as e:
            logger.error(f"Failed to create CrewAI agents: {str(e)}")
            raise
    
    async def enhance_legal_analysis(self, analysis_result: Dict[str, Any], 
                                   enable_crew_analysis: bool = True) -> Dict[str, Any]:
        """Enhance existing analysis with CrewAI insights"""
        if not enable_crew_analysis:
            logger.info("CrewAI enhancement disabled, returning original analysis")
            return analysis_result
        
        start_time = time.time()
        
        try:
            logger.info("Starting CrewAI enhancement of legal analysis")
            
            # Convert analysis result format if needed
            formatted_analysis = self._format_analysis_for_crew(analysis_result)
            
            # Create tasks based on analysis
            tasks = self.task_factory.create_all_tasks(formatted_analysis)
            
            # Execute CrewAI workflow
            crew_results = await self._execute_crew_tasks(tasks)
            
            # Enhance original analysis with CrewAI insights
            enhanced_analysis = self._merge_crew_results(analysis_result, crew_results)
            
            processing_time = time.time() - start_time
            
            enhanced_analysis.update({
                'crew_ai_enhanced': True,
                'crew_enhancement_time': processing_time,
                'enhancement_timestamp': datetime.utcnow().isoformat(),
                'crew_agents_used': list(self.agents.keys())
            })
            
            logger.info(f"CrewAI enhancement completed in {processing_time:.2f} seconds")
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"CrewAI enhancement failed: {str(e)}")
            # Return original analysis with error info
            analysis_result.update({
                'crew_ai_enhanced': False,
                'crew_enhancement_error': str(e),
                'enhancement_timestamp': datetime.utcnow().isoformat()
            })
            return analysis_result
    
    def _format_analysis_for_crew(self, analysis_result: Any) -> Dict[str, Any]:
        """Format analysis result for CrewAI processing"""
        # Handle DocumentAnalysis object or dict
        if hasattr(analysis_result, '__dict__'):
            # Convert Pydantic model to dict
            formatted = analysis_result.dict() if hasattr(analysis_result, 'dict') else analysis_result.__dict__
        else:
            formatted = analysis_result
        
        # Ensure key_clauses is properly formatted
        if 'key_clauses' in formatted:
            clauses = formatted['key_clauses']
            if clauses and hasattr(clauses[0], '__dict__'):
                # Convert clause objects to dicts
                formatted['key_clauses'] = [
                    clause.dict() if hasattr(clause, 'dict') else clause.__dict__ 
                    for clause in clauses
                ]
        
        return formatted
    
    async def _execute_crew_tasks(self, tasks: List) -> Dict[str, Any]:
        """Execute CrewAI tasks and return results"""
        results = {}
        
        # Execute tasks individually to handle errors better
        for i, task in enumerate(tasks):
            try:
                logger.info(f"Executing task {i+1}/{len(tasks)}: {task.agent.role}")
                
                # Create crew for this specific task
                crew = Crew(
                    agents=[task.agent],
                    tasks=[task],
                    verbose=int(os.getenv("CREWAI_VERBOSE", "1")),
                    memory=True
                )
                
                # Execute task
                result = crew.kickoff()
                
                # Store result based on agent role
                agent_role = task.agent.role
                if 'Research' in agent_role:
                    results['legal_research'] = str(result)
                elif 'Consumer Protection' in agent_role:
                    results['consumer_protection_analysis'] = str(result)
                elif 'Compliance' in agent_role:
                    results['regulatory_compliance'] = str(result)
                elif 'Negotiation' in agent_role:
                    results['negotiation_strategies'] = str(result)
                elif 'Alternative' in agent_role:
                    results['alternative_solutions'] = str(result)
                
                logger.info(f"Task {i+1} completed successfully")
                
            except Exception as e:
                logger.error(f"Task {i+1} failed ({task.agent.role}): {str(e)}")
                # Continue with other tasks even if one fails
                continue
        
        logger.info(f"CrewAI execution completed. Generated {len(results)} results.")
        return results
    
    def _merge_crew_results(self, original_analysis: Dict[str, Any], 
                           crew_results: Dict[str, Any]) -> Dict[str, Any]:
        """Merge CrewAI results with original analysis"""
        enhanced_analysis = original_analysis.copy()
        
        # Add CrewAI insights as new sections
        if crew_results.get('legal_research'):
            enhanced_analysis['legal_precedent_research'] = crew_results['legal_research']
        
        if crew_results.get('consumer_protection_analysis'):
            enhanced_analysis['consumer_rights_analysis'] = crew_results['consumer_protection_analysis']
        
        if crew_results.get('regulatory_compliance'):
            enhanced_analysis['compliance_assessment'] = crew_results['regulatory_compliance']
        
        if crew_results.get('negotiation_strategies'):
            enhanced_analysis['negotiation_guidance'] = crew_results['negotiation_strategies']
        
        if crew_results.get('alternative_solutions'):
            enhanced_analysis['alternatives_research'] = crew_results['alternative_solutions']
        
        # Enhance recommendations with CrewAI insights
        original_recommendations = enhanced_analysis.get('recommendations', [])
        crew_recommendations = self._extract_crew_recommendations(crew_results)
        
        if crew_recommendations:
            enhanced_analysis['recommendations'] = original_recommendations + crew_recommendations
        
        return enhanced_analysis
    
    def _extract_crew_recommendations(self, crew_results: Dict[str, Any]) -> List[str]:
        """Extract actionable recommendations from CrewAI results"""
        recommendations = []
        
        # Extract key recommendations from each crew result
        for result_type, result_content in crew_results.items():
            if not result_content:
                continue
                
            content_str = str(result_content)
            
            # Look for recommendation-like content
            if 'recommend' in content_str.lower():
                # Extract sentences with recommendations
                sentences = content_str.split('.')
                for sentence in sentences:
                    if 'recommend' in sentence.lower() and len(sentence.strip()) > 20:
                        recommendations.append(sentence.strip() + '.')
                        if len(recommendations) >= 2:  # Limit per result type
                            break
        
        return recommendations[:8]  # Limit total recommendations
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get status of CrewAI team"""
        return {
            'crew_initialized': True,
            'agents_count': len(self.agents),
            'agent_roles': [agent.role for agent in self.agents.values()],
            'llm_model': getattr(self.llm, 'model_name', 'unknown'),
            'memory_enabled': True
        }

class EnhancedOrchestrator:
    """Enhanced orchestrator integrating existing pipeline with CrewAI"""
    
    def __init__(self, existing_orchestrator: OrchestratorAgent, 
                 enable_crewai: bool = True):
        self.existing_orchestrator = existing_orchestrator
        self.enable_crewai = enable_crewai
        
        if self.enable_crewai:
            try:
                # Initialize CrewAI team
                gemini_service = get_modern_gemini_service()
                vertex_ai_service = get_vertex_ai_service()
                self.crew_team = CrewAILegalTeam(gemini_service, vertex_ai_service)
                logger.info("Enhanced Orchestrator initialized with CrewAI support")
            except Exception as e:
                logger.error(f"CrewAI initialization failed: {str(e)}")
                self.enable_crewai = False
                self.crew_team = None
        else:
            self.crew_team = None
            logger.info("Enhanced Orchestrator initialized without CrewAI")
    
    async def process_document(self, file_path: str, document_id: str, 
                             status_tracker: Dict, use_crew_enhancement: bool = True) -> DocumentAnalysis:
        """Process document with optional CrewAI enhancement"""
        try:
            # Step 1: Use existing orchestrator for core analysis
            logger.info(f"Starting core document processing for {document_id}")
            base_analysis = await self.existing_orchestrator.process_document(
                file_path, document_id, status_tracker
            )
            
            # Step 2: Apply CrewAI enhancement if enabled and requested
            if (self.enable_crewai and use_crew_enhancement and self.crew_team and 
                os.getenv("ENABLE_CREWAI_ENHANCEMENT", "true").lower() == "true"):
                
                logger.info(f"Starting CrewAI enhancement for {document_id}")
                status_tracker[document_id].current_step = "Enhancing analysis with expert agents"
                status_tracker[document_id].progress = 95
                
                # Convert DocumentAnalysis to dict for CrewAI
                analysis_dict = base_analysis.dict() if hasattr(base_analysis, 'dict') else base_analysis.__dict__
                
                enhanced_dict = await self.crew_team.enhance_legal_analysis(
                    analysis_dict, enable_crew_analysis=True
                )
                
                # Convert back to DocumentAnalysis if needed
                if hasattr(base_analysis, '__class__'):
                    # Update only allowed fields in the DocumentAnalysis model
                    allowed_fields = base_analysis.__fields__.keys() if hasattr(base_analysis, '__fields__') else []
                    for key, value in enhanced_dict.items():
                        if key in allowed_fields:
                            setattr(base_analysis, key, value)
                        else:
                            # Store additional data in recommendations or other existing fields
                            if key not in ['crew_ai_enhanced', 'legal_precedent_research', 
                                         'consumer_rights_analysis', 'compliance_assessment',
                                         'negotiation_guidance', 'alternatives_research']:
                                continue
                            # Add enhanced insights to recommendations
                            if hasattr(base_analysis, 'recommendations') and isinstance(value, str):
                                base_analysis.recommendations.append(f"Enhanced Analysis - {key}: {value[:200]}...")
                
                logger.info(f"CrewAI enhancement completed for {document_id}")
            else:
                logger.info(f"CrewAI enhancement skipped for {document_id}")
            
            return base_analysis
            
        except Exception as e:
            logger.error(f"Enhanced document processing failed for {document_id}: {str(e)}")
            raise
    
    async def handle_user_query(self, document_id: str, query: str):
        """Handle user query using existing query handler"""
        return await self.existing_orchestrator.handle_user_query(document_id, query)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of entire system"""
        status = {
            'core_system': 'operational',
            'crewai_enabled': self.enable_crewai,
            'crewai_available': self.crew_team is not None
        }
        
        if self.crew_team:
            status['crewai_status'] = self.crew_team.get_crew_status()
        
        return status