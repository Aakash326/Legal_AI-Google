from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from crew.tools.legal_tools import LegalToolsFactory

class ComplianceExpertAgent:
    """Regulatory Compliance Expert Agent"""
    
    def __init__(self, gemini_service, llm: ChatGoogleGenerativeAI):
        self.gemini_service = gemini_service
        self.llm = llm
        self.tools_factory = LegalToolsFactory(gemini_service)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the compliance expert agent"""
        tools = [self.tools_factory.create_compliance_tool()]
        
        return Agent(
            role='Regulatory Compliance Expert',
            goal='Ensure documents comply with federal and state regulations',
            backstory="""You are a regulatory compliance expert with deep knowledge of consumer protection laws, 
            fair lending practices, housing regulations, and employment law. You have 18 years of experience 
            helping organizations navigate complex regulatory environments. You work with existing analyzers to 
            identify potential compliance issues.
            
            Your expertise includes:
            - Federal consumer protection regulations (CFPB, FTC, etc.)
            - Fair Credit Reporting Act (FCRA) compliance
            - Truth in Lending Act (TILA) requirements
            - Fair Housing Act (FHA) compliance
            - Equal Credit Opportunity Act (ECOA) adherence
            - State-specific consumer protection laws
            - Industry-specific regulatory requirements
            - Required disclosure analysis
            
            You provide detailed compliance assessments with specific regulatory citations and 
            actionable recommendations for addressing violations.""",
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