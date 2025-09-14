from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Any
from crew.tools.legal_tools import LegalToolsFactory

class LegalResearcherAgent:
    """Legal Research Specialist Agent"""
    
    def __init__(self, gemini_service, llm: ChatGoogleGenerativeAI):
        self.gemini_service = gemini_service
        self.llm = llm
        self.tools_factory = LegalToolsFactory(gemini_service)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the legal researcher agent"""
        tools = [self.tools_factory.create_legal_research_tool()]
        
        return Agent(
            role='Senior Legal Research Specialist',
            goal='Research legal precedents, case law, and regulatory context for document clauses',
            backstory="""You are a senior legal researcher with 20 years of experience in case law analysis. 
            You specialize in finding relevant legal precedents, understanding how courts have interpreted 
            similar clauses, and identifying potential legal challenges. You work closely with the existing 
            legal analyzer to provide deeper context and historical perspective.
            
            Your expertise includes:
            - Federal and state case law research
            - Regulatory interpretation analysis
            - Consumer protection precedents
            - Contract enforceability studies
            - Legal trend analysis
            
            You provide thorough, well-cited research that helps users understand the legal landscape 
            around their document clauses.""",
            llm=self.llm,
            tools=tools,
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            memory=True
        )
    
    def get_agent(self) -> Agent:
        """Get the configured agent"""
        return self.agent