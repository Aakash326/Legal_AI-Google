# LegalClarity AI Backend

## 🎯 Overview

LegalClarity AI is an innovative backend system that uses **Google Cloud's Gemini API** and an **Agentic RAG (Retrieval-Augmented Generation)** architecture to analyze legal documents and make them understandable for ordinary people.

### Key Features

- **Document Analysis**: Extract and analyze legal clauses from PDF, DOCX, and TXT files
- **Risk Assessment**: Assign risk scores (1-10) to legal clauses and overall documents
- **Plain Language Translation**: Convert complex legal jargon into understandable language
- **Q&A System**: Answer natural language questions about document terms
- **Agentic Architecture**: Specialized AI agents handle different aspects of analysis
- **Real-time Processing**: Background processing with status updates

## 🏗️ Architecture

The system uses an **Agentic RAG** approach with specialized agents:

```
Document Upload → Orchestrator Agent → Specialized Agents → Results Dashboard
                       ↓
    ┌─ Document Processor Agent (text extraction, chunking)
    ├─ Legal Analyzer Agent (clause identification, classification)  
    ├─ Risk Assessor Agent (risk scoring, red flag detection)
    ├─ Query Handler Agent (Q&A about document terms)
    └─ Results Compilation → User Interface
```

## 📁 Project Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── README.md                 # This file
├── agents/                   # Specialized AI agents
│   ├── __init__.py
│   ├── orchestrator.py       # Central coordinator agent
│   ├── document_processor.py # Document parsing & chunking agent
│   ├── legal_analyzer.py     # Legal clause analysis agent
│   ├── risk_assessor.py      # Risk scoring agent
│   └── query_handler.py      # Q&A agent
├── services/                 # Google Cloud service integrations
│   ├── __init__.py
│   ├── gemini_service.py     # Google Gemini API wrapper
│   ├── vertex_ai_service.py  # Vertex AI embeddings
│   └── storage_service.py    # Cloud Storage integration
├── models/                   # Data models and schemas
│   ├── __init__.py
│   ├── document.py           # Document data models
│   └── analysis.py           # Analysis result models
└── utils/                    # Utility functions
    ├── __init__.py
    ├── pdf_parser.py          # PDF text extraction
    └── text_processor.py     # Text processing utilities
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Project with Gemini API enabled
- Google Cloud API key

### Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Google Cloud credentials
   ```

4. **Configure Google Cloud credentials**
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key"
   export GOOGLE_CLOUD_PROJECT="your_project_id"
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   Or with uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud Project ID | Yes |
| `GOOGLE_CLOUD_STORAGE_BUCKET` | Storage bucket name | Optional |

### Google Cloud Setup

1. **Enable APIs** in your Google Cloud Project:
   - Generative AI API (for Gemini)
   - Vertex AI API (for embeddings)
   - Cloud Storage API (for file storage)

2. **Get API Key**:
   - Go to Google AI Studio (https://makersuite.google.com/)
   - Create an API key for Gemini

3. **Optional: Service Account** (for production):
   ```bash
   gcloud iam service-accounts create legalclarity-ai
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:legalclarity-ai@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/aiplatform.user"
   ```

## 📚 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload document for analysis |
| GET | `/status/{document_id}` | Get processing status |
| GET | `/analysis/{document_id}` | Get analysis results |
| POST | `/query` | Ask questions about document |
| GET | `/health` | Health check |

### Example Usage

#### Upload Document
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@contract.pdf"
```

#### Check Status
```bash
curl "http://localhost:8000/status/{document_id}"
```

#### Get Analysis
```bash
curl "http://localhost:8000/analysis/{document_id}"
```

#### Ask Question
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "document_id": "your-doc-id",
       "query": "What happens if I break this lease early?"
     }'
```

## 🤖 Agent System

### Orchestrator Agent
- Coordinates the entire analysis workflow
- Manages processing status and error handling
- Compiles results from specialized agents

### Document Processor Agent
- Extracts text from PDF, DOCX, and TXT files
- Cleans and normalizes text
- Intelligently chunks text for AI processing
- Classifies document type

### Legal Analyzer Agent
- Identifies and classifies legal clauses
- Extracts key legal entities and terms
- Translates complex legal language to plain English
- Uses specialized prompts for legal analysis

### Risk Assessor Agent
- Assigns risk scores (1-10) to clauses
- Identifies "red flag" terms
- Calculates overall document risk
- Provides actionable recommendations

### Query Handler Agent
- Processes natural language questions
- Finds relevant clauses for each query
- Generates contextual answers
- Provides confidence scores

## 🔍 Analysis Features

### Clause Types Detected
- Payment Terms
- Termination Conditions
- Liability Provisions
- Confidentiality Requirements
- Intellectual Property Rights
- Dispute Resolution
- Governing Law
- Indemnification
- And more...

### Risk Scoring
- **1-3**: Low risk (standard, fair terms)
- **4-6**: Medium risk (some concerns, review recommended)
- **7-10**: High risk (unfavorable, potentially problematic)

### Example Analysis Output
```json
{
  "document_id": "abc-123",
  "document_type": "rental_agreement",
  "overall_risk_score": 6.2,
  "key_clauses": [
    {
      "clause_type": "payment_terms",
      "original_text": "Tenant shall pay...",
      "simplified_text": "You must pay rent by the 1st of each month...",
      "risk_score": 8,
      "risk_explanation": "High late fees and penalties"
    }
  ],
  "recommendations": [
    "Review payment terms for potential hidden fees",
    "Consider negotiating termination conditions"
  ],
  "red_flags": [
    "Unlimited liability exposure detected"
  ]
}
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Test with Sample Document
1. Create a simple text file with legal-like content
2. Upload via the `/upload` endpoint
3. Monitor processing via `/status/{id}`
4. Get results via `/analysis/{id}`
5. Ask questions via `/query`

## 🚨 Error Handling

### Common Issues

1. **"Google API key is required"**
   - Set `GOOGLE_API_KEY` environment variable
   - Verify key is valid in Google AI Studio

2. **"No text could be extracted"**
   - Check file format (PDF, DOCX, TXT only)
   - Ensure file is not corrupted or password-protected

3. **"Processing timeout"**
   - Large files may take longer
   - Check Gemini API rate limits
   - Verify internet connection

4. **"Document not found"**
   - Processing may still be in progress
   - Check document ID is correct
   - Verify upload was successful

## 📈 Performance

### Processing Times
- **Small documents** (1-5 pages): 10-30 seconds
- **Medium documents** (5-15 pages): 30-90 seconds
- **Large documents** (15+ pages): 90+ seconds

### Optimization Tips
- Use smaller document chunks for faster processing
- Enable caching for repeated analyses
- Implement rate limiting for Gemini API
- Use background processing for large files

## 🔒 Security

### Best Practices
- Store API keys securely (use environment variables)
- Implement input validation for file uploads
- Set file size limits
- Use HTTPS in production
- Regularly rotate API keys
- Sanitize user inputs

### File Security
- Files are temporarily stored during processing
- Automatic cleanup of processed files
- No persistent storage of sensitive documents
- Optional Google Cloud Storage integration

## 🚀 Deployment

### Development
```bash
python main.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 🔧 Customization

### Adding New Clause Types
1. Add to `ClauseType` enum in `models/document.py`
2. Update patterns in `text_processor.py`
3. Add specific prompts in `gemini_service.py`
4. Update risk weights in `risk_assessor.py`

### Custom Document Types
1. Add to `DocumentType` enum in `models/document.py`
2. Update classification logic in `document_processor.py`
3. Add type-specific analysis rules

### New Analysis Features
1. Create new agent in `agents/` directory
2. Add agent to orchestrator workflow
3. Update data models as needed
4. Add API endpoints if required

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Include error handling

## 📄 License

This project is licensed under the MIT License.

## 🤝 Support

For questions or issues:
1. Check this README
2. Review API documentation at `/docs`
3. Check logs for error details
4. Open an issue on GitHub

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced document comparison
- [ ] Contract template generation
- [ ] Integration with legal databases
- [ ] Enhanced risk prediction models
- [ ] Real-time collaboration features

---

**LegalClarity AI** - Making legal documents understandable for everyone! 🏛️✨