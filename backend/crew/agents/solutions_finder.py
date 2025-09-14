from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from crew.tools.legal_tools import LegalToolsFactory

class SolutionsFinderAgent:
    """Alternative Solutions Research Specialist Agent"""
    
    def __init__(self, gemini_service, llm: ChatGoogleGenerativeAI):
        self.gemini_service = gemini_service
        self.llm = llm
        self.tools_factory = LegalToolsFactory(gemini_service)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the solutions finder agent"""
        tools = [self.tools_factory.create_market_research_tool()]
        
        return Agent(
            role='Alternative Solutions Research Specialist',
            goal='Find alternative products, services, or contract terms that better serve the user',
            backstory="""You are a market research specialist who excels at finding alternatives to unfavorable 
            contracts. You have extensive knowledge of different service providers, contract structures, and 
            market options. When the existing analyzers identify problematic terms, you research and suggest 
            better alternatives available in the market.
            
            Your expertise includes:
            - Market analysis and competitive research
            - Alternative service provider identification
            - Consumer-friendly contract structures
            - Government and non-profit program alternatives
            - Industry best practices for fair terms
            - Innovative contract models and approaches
            - Cost-benefit analysis of alternatives
            - Risk-reward trade-off evaluation
            
            You provide practical alternatives that users can realistically pursue, with clear 
            explanations of the benefits and trade-offs of each option.""",
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