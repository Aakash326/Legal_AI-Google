"""CrewAI Agents for Legal Analysis"""

from .legal_researcher import LegalResearcherAgent
from .consumer_advocate import ConsumerAdvocateAgent
from .compliance_expert import ComplianceExpertAgent
from .negotiation_advisor import NegotiationAdvisorAgent
from .solutions_finder import SolutionsFinderAgent

__all__ = [
    "LegalResearcherAgent",
    "ConsumerAdvocateAgent", 
    "ComplianceExpertAgent",
    "NegotiationAdvisorAgent",
    "SolutionsFinderAgent"
]