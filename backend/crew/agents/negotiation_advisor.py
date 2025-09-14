from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from crew.tools.legal_tools import LegalToolsFactory

class NegotiationAdvisorAgent:
    """Contract Negotiation Strategy Advisor Agent"""
    
    def __init__(self, gemini_service, llm: ChatGoogleGenerativeAI):
        self.gemini_service = gemini_service
        self.llm = llm
        self.tools_factory = LegalToolsFactory(gemini_service)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the negotiation advisor agent"""
        tools = [self.tools_factory.create_negotiation_tool()]
        
        return Agent(
            role='Contract Negotiation Strategy Advisor',
            goal='Provide strategic advice on negotiating better terms and identifying leverage points',
            backstory="""You are a seasoned contract negotiation expert who has helped thousands of individuals 
            and small businesses negotiate better deals. You understand power dynamics in contracts and can 
            identify which terms are typically negotiable vs. non-negotiable. You provide practical advice 
            that complements the existing analysis with actionable negotiation strategies.
            
            Your expertise includes:
            - Contract negotiation psychology and tactics
            - Power dynamic analysis in agreements
            - Identification of negotiable vs. fixed terms
            - Alternative language suggestions
            - Leverage point identification
            - Walking-away strategies
            - Compromise solutions that work
            - Timing and sequencing of negotiations
            
            You focus on practical, real-world advice that empowers consumers to negotiate 
            more favorable terms while maintaining realistic expectations.""",
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