# LegalClarity AI

> AI-powered legal document analysis system with comprehensive risk assessment and expert guidance

## 🎯 Overview

LegalClarity AI is a sophisticated legal document analysis platform that leverages advanced AI technologies to provide comprehensive insights into legal documents. The system combines modern web technologies with powerful AI agents to deliver expert-level legal analysis, risk assessment, and actionable recommendations.

## ✨ Features

### Core Capabilities
- **Document Analysis**: Comprehensive analysis of PDF, DOCX, and TXT legal documents
- **Risk Assessment**: Intelligent risk scoring with detailed visualizations
- **AI-Powered Chat**: Interactive Q&A with your analyzed documents
- **Multi-Agent System**: CrewAI-powered expert agents for specialized analysis
- **Real-time Processing**: Live progress tracking with background processing

### Advanced Features
- **Legal Precedent Research**: Automated research of relevant case law
- **Consumer Rights Analysis**: Detailed analysis of consumer protection aspects
- **Compliance Assessment**: Regulatory compliance evaluation
- **Negotiation Guidance**: Strategic advice for contract negotiations
- **Alternative Solutions**: Creative alternatives and risk mitigation strategies

## 🏗️ Architecture

### Frontend Stack
- **Framework**: Next.js 15.5.3 with React 19.1.0
- **Styling**: Tailwind CSS 4.0 with custom animations
- **UI Components**: Radix UI primitives with shadcn/ui
- **State Management**: Zustand for global state
- **Data Fetching**: TanStack Query (React Query) with Axios
- **Form Handling**: React Hook Form with Zod validation
- **Animations**: Framer Motion
- **Charts**: Recharts for data visualization
- **Theme**: next-themes for dark/light mode

### Backend Stack
- **Framework**: FastAPI with async/await support
- **AI Models**: Google Gemini AI integration
- **Document Processing**: PyPDF2, python-docx, pdfplumber
- **Agent Framework**: CrewAI for multi-agent orchestration
- **Vector Database**: ChromaDB for document embeddings
- **Language Models**: LangChain with Google Generative AI
- **Data Validation**: Pydantic for request/response models
- **Background Tasks**: FastAPI BackgroundTasks

### AI & ML Stack
- **Primary LLM**: Google Gemini Pro
- **Agent Framework**: CrewAI for specialized legal agents
- **Vector Embeddings**: ChromaDB for semantic search
- **Text Processing**: NLTK, spaCy for advanced NLP
- **Document Analysis**: Custom legal analysis pipeline

## 📁 Project Structure

```
Legal-Ai/
├── frontend/                 # Next.js React application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── lib/            # Utilities and configurations
│   │   └── types/          # TypeScript type definitions
│   ├── package.json
│   └── tailwind.config.ts
├── backend/                 # FastAPI Python application
│   ├── agents/             # AI agent implementations
│   ├── crew/              # CrewAI orchestration
│   ├── models/            # Pydantic data models
│   ├── services/          # Core business logic
│   ├── utils/             # Helper utilities
│   ├── main.py            # FastAPI application entry
│   └── requirements.txt
├── uploads/               # Document storage
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.8+ with pip
- **Node.js**: 18+ with npm
- **Google AI API Key**: For Gemini integration

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Legal-Ai
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Create .env file
   cp .env.example .env
   # Add your Google AI API key to .env
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Environment is pre-configured in .env.local
   ```

### Running the Application

#### Option 1: Separate Terminals
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

#### Option 2: Background Process
```bash
# Start both services in background
cd backend && python main.py &
cd frontend && npm run dev &
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
GOOGLE_API_KEY=your_google_ai_api_key
ENABLE_CREWAI=true
LOG_LEVEL=INFO
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="LegalClarity AI"
NEXT_PUBLIC_SUPPORT_EMAIL=support@legalclarity.ai
```

## 📚 API Endpoints

### Document Management
- `POST /upload` - Basic document upload and analysis
- `POST /upload/enhanced` - Enhanced analysis with CrewAI agents
- `GET /status/{document_id}` - Processing status
- `GET /analysis/{document_id}` - Analysis results
- `GET /analysis/{document_id}/enhanced` - Enhanced results with agent insights

### Interactive Features
- `POST /query` - Ask questions about analyzed documents
- `GET /system/status` - System health and statistics

### System
- `GET /health` - Health check
- `GET /` - API information and available endpoints

## 🎨 Key Components

### Frontend Components
- **DocumentUpload**: Drag-and-drop file upload with progress
- **AnalysisResults**: Comprehensive analysis display
- **RiskVisualization**: Interactive risk score charts
- **ChatInterface**: Document Q&A interface
- **ProgressTracker**: Real-time processing updates

### Backend Agents
- **Legal Analyzer**: Core document analysis
- **Risk Assessor**: Risk evaluation and scoring
- **Legal Researcher**: Precedent and case law research
- **Consumer Rights Specialist**: Consumer protection analysis
- **Compliance Expert**: Regulatory compliance assessment

## 🛡️ Security Features

- **Input Validation**: Comprehensive request validation with Pydantic
- **File Type Restrictions**: Limited to PDF, DOCX, TXT files
- **CORS Configuration**: Controlled cross-origin access
- **Error Handling**: Secure error messages without sensitive data exposure
- **Background Processing**: Isolated document processing

## 🔄 Development Workflow

### Adding New Features
1. **Backend**: Create new endpoints in `main.py` and agents in `agents/`
2. **Frontend**: Add components in `components/` and pages in `app/`
3. **Types**: Update TypeScript definitions in `lib/types/`

### Testing
```bash
# Backend testing
cd backend
python -m pytest  # (when tests are added)

# Frontend testing
cd frontend
npm run lint
npm run build
```

## 📦 Dependencies

### Frontend Key Dependencies
- `next`: 15.5.3 - React framework
- `@tanstack/react-query`: 5.87.4 - Data fetching
- `axios`: 1.12.1 - HTTP client
- `@radix-ui/*`: UI primitives
- `tailwindcss`: 4.0 - CSS framework
- `framer-motion`: 12.23.12 - Animations
- `recharts`: 3.2.0 - Charts
- `zustand`: 5.0.8 - State management

### Backend Key Dependencies
- `fastapi`: 0.104.0+ - Web framework
- `google-generativeai`: 0.3.0+ - Gemini AI
- `crewai`: 0.28.0+ - Multi-agent framework
- `langchain`: 0.1.0+ - LLM framework
- `pydantic`: 2.5.0+ - Data validation
- `pypdf2`: 3.0.1+ - PDF processing

## 🔮 Future Enhancements

- **Advanced Analytics**: Usage analytics and insights dashboard
- **Multi-language Support**: Support for documents in multiple languages
- **Batch Processing**: Multiple document analysis
- **Integration APIs**: Third-party legal database integrations
- **Advanced Security**: User authentication and role-based access
- **Mobile App**: React Native mobile application

## 📄 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

This is a private project. For questions or suggestions, contact the development team.

## 📞 Support

For technical support or questions:
- Email: support@legalclarity.ai
- Documentation: Available in `/docs` endpoint when running

---

Built with ❤️ using cutting-edge AI and modern web technologies.