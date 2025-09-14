# CrewAI Enhanced Legal Analysis 🤖⚖️

## Overview

This CrewAI integration adds **5 specialized AI agents** to the LegalClarity AI system, providing expert-level analysis and insights beyond the base document processing.

## 🎭 The Expert Agent Team

### 1. **Legal Research Specialist** 📚
- **Role**: Senior Legal Research Specialist  
- **Expertise**: Case law, precedents, regulatory context
- **Tools**: Legal precedent research, case law database access
- **Output**: Detailed research reports with citations

### 2. **Consumer Protection Advocate** 🛡️
- **Role**: Consumer Protection Advocate
- **Expertise**: Unfair practices, consumer rights violations
- **Tools**: Compliance checking, consumer law analysis
- **Output**: Consumer rights violation reports

### 3. **Regulatory Compliance Expert** 📋
- **Role**: Regulatory Compliance Expert
- **Expertise**: Federal/state regulations, industry compliance
- **Tools**: Multi-jurisdiction compliance checking
- **Output**: Comprehensive compliance assessments

### 4. **Contract Negotiation Advisor** 🤝
- **Role**: Contract Negotiation Strategy Advisor
- **Expertise**: Negotiation tactics, leverage identification
- **Tools**: Negotiation strategy generation
- **Output**: Practical negotiation playbooks

### 5. **Alternative Solutions Finder** 🔍
- **Role**: Alternative Solutions Research Specialist
- **Expertise**: Market alternatives, better options research
- **Tools**: Market research, alternative analysis
- **Output**: Comprehensive alternatives with comparisons

## 🏗️ Architecture

```
Document Upload
     ↓
Base Analysis (Existing Pipeline)
     ↓
CrewAI Enhancement (If Enabled)
     ↓
┌─ Legal Research Agent
├─ Consumer Advocate Agent  
├─ Compliance Expert Agent
├─ Negotiation Advisor Agent
└─ Solutions Finder Agent
     ↓
Enhanced Results
```

## 📁 File Structure

```
crew/
├── README.md                 # This file
├── __init__.py              # Main CrewAI exports
├── enhanced_orchestrator.py # Integration orchestrator
├── agents/                  # Individual agent implementations
│   ├── __init__.py
│   ├── legal_researcher.py
│   ├── consumer_advocate.py
│   ├── compliance_expert.py
│   ├── negotiation_advisor.py
│   └── solutions_finder.py
├── tasks/                   # CrewAI task definitions
│   ├── __init__.py
│   └── legal_tasks.py
└── tools/                   # Custom CrewAI tools
    ├── __init__.py
    └── legal_tools.py
```

## 🚀 Usage

### Basic Integration

```python
from crew.enhanced_orchestrator import EnhancedOrchestrator
from agents.orchestrator import OrchestratorAgent

# Create enhanced orchestrator
base_orchestrator = OrchestratorAgent()
enhanced_orchestrator = EnhancedOrchestrator(
    base_orchestrator, 
    enable_crewai=True
)

# Process document with CrewAI enhancement
result = await enhanced_orchestrator.process_document(
    file_path="contract.pdf",
    document_id="doc123",
    status_tracker=status_dict,
    use_crew_enhancement=True
)
```

### API Endpoints

#### Enhanced Upload
```bash
# Upload with CrewAI enhancement
curl -X POST "http://localhost:8000/upload/enhanced" \
     -F "file=@contract.pdf" \
     -F "use_crew_enhancement=true"
```

#### Enhanced Analysis Results
```bash
# Get enhanced results
curl "http://localhost:8000/analysis/{doc_id}/enhanced"
```

#### System Status
```bash
# Check CrewAI system status
curl "http://localhost:8000/system/status"
```

## 🔧 Configuration

### Environment Variables

```bash
# Enable/Disable CrewAI
ENABLE_CREWAI=true
ENABLE_CREWAI_ENHANCEMENT=true

# Model Configuration
CREWAI_MODEL=gemini-1.5-pro
CREWAI_TEMPERATURE=0.1
CREWAI_MAX_TOKENS=2048

# Individual Agent Control
ENABLE_LEGAL_RESEARCH_AGENT=true
ENABLE_CONSUMER_ADVOCATE_AGENT=true
ENABLE_COMPLIANCE_EXPERT_AGENT=true
ENABLE_NEGOTIATION_ADVISOR_AGENT=true
ENABLE_SOLUTIONS_FINDER_AGENT=true

# Performance Tuning
MAX_CONCURRENT_CREW_TASKS=3
CREWAI_TASK_TIMEOUT=180
```

## 📊 Enhanced Output Format

CrewAI adds these fields to the analysis results:

```json
{
  "document_id": "abc-123",
  "overall_risk_score": 7.2,
  "key_clauses": [...],
  
  // CrewAI Enhanced Fields
  "legal_precedent_research": "Detailed case law analysis...",
  "consumer_rights_analysis": "Consumer protection violations...",
  "compliance_assessment": "Regulatory compliance review...",
  "negotiation_guidance": "Strategic negotiation advice...",
  "alternatives_research": "Better options and alternatives...",
  
  // Metadata
  "crew_ai_enhanced": true,
  "crew_enhancement_time": 45.2,
  "crew_agents_used": ["researcher", "advocate", "compliance", "negotiator", "solutions"],
  "enhancement_timestamp": "2024-01-15T10:30:00Z"
}
```

## 🎯 Example Enhanced Analysis

### Input: Rental Agreement
**Base Analysis**: Risk score 6.8, 12 clauses identified

### CrewAI Enhancement Output:

**Legal Research**: 
- Found 3 relevant cases: *Smith v. Landlord Corp* (2019)
- Consumer won similar case regarding excessive late fees
- State precedent favors tenant protection

**Consumer Protection**:
- Violation: Hidden fee structure violates Truth in Lending
- Severity: High - potential class action material
- Remedy: File complaint with state attorney general

**Compliance Assessment**:
- CFPB violation: Lack of required disclosures
- State law violation: Exceeds maximum security deposit
- Risk level: Critical - potential regulatory action

**Negotiation Strategy**:
- Negotiable: Late fee amount (industry standard: $25)
- Leverage: Regulatory compliance issues
- Alternative language: "Reasonable late fee not to exceed $25"

**Alternatives Research**:
- ABC Apartments: Similar units, 30% lower fees
- Community Housing Coop: No late fees, tenant-friendly
- Government program: Section 8 voucher eligibility

## 🔍 Agent Deep Dive

### Legal Research Agent Tools
- **Precedent Research**: Searches case law databases
- **Regulatory Analysis**: Reviews federal/state regulations
- **Trend Analysis**: Identifies legal interpretation patterns

### Consumer Advocate Tools
- **Rights Checker**: Validates consumer protection compliance
- **Unfair Practice Detector**: Identifies problematic clauses
- **Remedy Finder**: Suggests available legal remedies

### Compliance Expert Tools
- **Multi-Jurisdiction Checker**: Checks federal and state laws
- **Industry Standards**: Compares against best practices
- **Violation Assessor**: Rates compliance risk levels

### Negotiation Advisor Tools
- **Leverage Analyzer**: Identifies negotiation advantages
- **Alternative Language**: Suggests fairer clause wording
- **Strategy Generator**: Creates step-by-step negotiation plans

### Solutions Finder Tools
- **Market Research**: Finds competitive alternatives
- **Option Evaluator**: Compares costs and benefits
- **Transition Planner**: Provides switching strategies

## ⚡ Performance

### Processing Times
- **Base Analysis**: 10-30 seconds
- **CrewAI Enhancement**: +30-90 seconds
- **Total Enhanced**: 40-120 seconds

### Optimization
- Agents run in parallel where possible
- Configurable timeouts prevent hanging
- Graceful fallback to base analysis if CrewAI fails
- Memory-enabled agents learn from previous analyses

## 🛠️ Development

### Adding New Agents

1. **Create Agent Class**:
```python
# crew/agents/new_agent.py
from crewai import Agent

class NewExpertAgent:
    def __init__(self, gemini_service, llm):
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        return Agent(
            role='New Expert Role',
            goal='Specific expert goal',
            backstory='Expert background...',
            llm=self.llm,
            tools=[...]
        )
```

2. **Add to Enhanced Orchestrator**:
```python
# crew/enhanced_orchestrator.py
def _create_agents(self):
    agents = {
        # ... existing agents
        'new_expert': NewExpertAgent(self.gemini_service, self.llm).get_agent()
    }
```

3. **Create Corresponding Task**:
```python
# crew/tasks/legal_tasks.py
def create_new_expert_task(self, data) -> Task:
    return Task(
        description="Expert task description...",
        agent=self.agents['new_expert'],
        expected_output="Expected output format"
    )
```

### Custom Tools

```python
# crew/tools/legal_tools.py
class NewCustomTool(BaseTool):
    name: str = "tool_name"
    description: str = "Tool description"
    
    def _run(self, input_data: str) -> str:
        # Tool implementation
        return processed_result
```

## 🐛 Troubleshooting

### Common Issues

1. **"CrewAI enhancement failed"**
   - Check Google API key is valid
   - Verify internet connection
   - Check API rate limits

2. **"Agent timeout"**
   - Increase `CREWAI_TASK_TIMEOUT`
   - Reduce document size
   - Check agent configuration

3. **"Memory issues"**
   - Disable memory: `CREWAI_MEMORY=false`
   - Reduce concurrent tasks
   - Check available RAM

### Debug Mode

```bash
# Enable verbose logging
CREWAI_VERBOSE=2
LOG_LEVEL=DEBUG

# Check agent status
curl "http://localhost:8000/system/status"
```

## 📈 Monitoring

### Metrics to Track
- CrewAI success rate
- Average enhancement time
- Agent-specific performance
- API usage and costs
- User satisfaction with enhanced results

### Logging

```python
# Monitor agent performance
logger.info(f"CrewAI enhancement completed in {time:.2f}s")
logger.info(f"Agents used: {agent_list}")
logger.warning(f"Agent {agent_name} timed out")
```

---

**CrewAI Integration**: Elevating legal document analysis with specialized AI expertise! 🚀⚖️