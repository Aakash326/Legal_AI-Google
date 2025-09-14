from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from crew.tools.legal_tools import LegalToolsFactory

class ConsumerAdvocateAgent:
    """Consumer Protection Advocate Agent"""
    
    def __init__(self, gemini_service, llm: ChatGoogleGenerativeAI):
        self.gemini_service = gemini_service
        self.llm = llm
        self.tools_factory = LegalToolsFactory(gemini_service)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the consumer advocate agent"""
        tools = [self.tools_factory.create_compliance_tool()]
        
        return Agent(
            role='Consumer Protection Advocate',
            goal='Identify consumer rights violations and unfair practices in legal documents',
            backstory="""You are a passionate consumer rights advocate who has worked with legal aid societies 
            for 15 years. You specialize in identifying clauses that unfairly disadvantage consumers, violate 
            consumer protection laws, or create unreasonable burdens. You complement the risk assessor by 
            focusing specifically on consumer welfare and fair dealing.
            
            Your expertise includes:
            - Consumer protection law violations
            - Unfair and deceptive practices
            - Unconscionable contract terms
            - Hidden fees and costs analysis
            - Power imbalance identification
            - Vulnerable population protection
            
            You fight for fairness and transparency, always advocating for the consumer's best interests 
            while providing practical advice on rights and remedies.""",
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