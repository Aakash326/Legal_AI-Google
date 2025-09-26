# Load environment variables first
import os
from pathlib import Path

def load_env_file():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    os.environ[key] = value

load_env_file()

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from agents.orchestrator import OrchestratorAgent
from models.document import UploadedDocument, ProcessingStatus
from models.analysis import DocumentAnalysis, QueryResult

# CrewAI Integration
from crew.enhanced_orchestrator import EnhancedOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LegalClarity AI Backend",
    description="AI-powered legal document analysis system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator with CrewAI enhancement
base_orchestrator = OrchestratorAgent()
enable_crewai = os.getenv("ENABLE_CREWAI", "true").lower() == "true"
orchestrator = EnhancedOrchestrator(base_orchestrator, enable_crewai=enable_crewai)

processing_status: Dict[str, ProcessingStatus] = {}
analysis_results: Dict[str, DocumentAnalysis] = {}

class QueryRequest(BaseModel):
    document_id: str
    query: str

class EnhancedUploadRequest(BaseModel):
    use_crew_enhancement: bool = True
    enable_detailed_analysis: bool = True

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload a legal document for analysis"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        allowed_extensions = {".pdf", ".docx", ".txt"}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        document_id = str(uuid.uuid4())
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{document_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        uploaded_doc = UploadedDocument(
            document_id=document_id,
            filename=file.filename,
            file_type=file_extension,
            upload_time=datetime.utcnow(),
            file_size=len(content)
        )
        
        processing_status[document_id] = ProcessingStatus(
            document_id=document_id,
            status="uploaded",
            progress=0,
            current_step="File uploaded successfully",
            start_time=datetime.utcnow()
        )
        
        background_tasks.add_task(process_document_async, document_id, file_path)
        
        logger.info(f"Document uploaded: {document_id} - {file.filename}")
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Document uploaded successfully and processing started"
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/status/{document_id}")
async def get_processing_status(document_id: str):
    """Get the processing status of a document"""
    if document_id not in processing_status:
        raise HTTPException(status_code=404, detail="Document not found")
    
    status = processing_status[document_id]
    return status.dict()

@app.get("/analysis/{document_id}")
async def get_analysis_results(document_id: str):
    """Get analysis results for a processed document"""
    if document_id not in analysis_results:
        if document_id not in processing_status:
            raise HTTPException(status_code=404, detail="Document not found")
        
        status = processing_status[document_id]
        if status.status in ["processing", "uploaded"]:
            raise HTTPException(
                status_code=202, 
                detail="Document is still being processed"
            )
        elif status.status == "failed":
            raise HTTPException(
                status_code=500, 
                detail=f"Processing failed: {status.error_message}"
            )
    
    return analysis_results[document_id].dict()

@app.post("/query")
async def query_document(query_request: QueryRequest):
    """Ask a question about a processed document"""
    document_id = query_request.document_id
    query = query_request.query
    
    if document_id not in analysis_results:
        raise HTTPException(
            status_code=404, 
            detail="Document not found or not yet processed"
        )
    
    try:
        result = await orchestrator.handle_user_query(document_id, query)
        return result.dict()
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

async def process_document_async(document_id: str, file_path: str):
    """Background task to process the uploaded document"""
    try:
        processing_status[document_id].status = "processing"
        processing_status[document_id].progress = 10
        processing_status[document_id].current_step = "Starting document analysis"
        
        logger.info(f"Starting processing for document: {document_id}")
        
        result = await orchestrator.process_document(file_path, document_id, processing_status)
        
        analysis_results[document_id] = result
        processing_status[document_id].status = "completed"
        processing_status[document_id].progress = 100
        processing_status[document_id].current_step = "Analysis completed"
        processing_status[document_id].end_time = datetime.utcnow()
        

        logger.info(f"Processing completed for document: {document_id}")
    except Exception as e:

        
        logger.error(f"Processing error for {document_id}: {str(e)}")
        processing_status[document_id].status = "failed"
        processing_status[document_id].error_message = str(e)
        processing_status[document_id].end_time = datetime.utcnow()

@app.post("/upload/enhanced")
async def upload_document_enhanced(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_crew_enhancement: bool = True
):
    """Upload document with optional CrewAI enhancement"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        allowed_extensions = {".pdf", ".docx", ".txt"}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        document_id = str(uuid.uuid4())
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{document_id}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        processing_status[document_id] = ProcessingStatus(
            document_id=document_id,
            status="uploaded",
            progress=0,
            current_step="File uploaded successfully - Enhanced analysis enabled",
            start_time=datetime.utcnow()
        )
        
        # Use enhanced processing with CrewAI
        background_tasks.add_task(
            process_document_enhanced_async, 
            document_id, 
            file_path, 
            use_crew_enhancement
        )
        
        logger.info(f"Document uploaded for enhanced analysis: {document_id} - {file.filename}")
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "uploaded",
            "enhancement_enabled": use_crew_enhancement,
            "message": "Document uploaded successfully and enhanced processing started"
        }
        
    except Exception as e:
        logger.error(f"Enhanced upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced upload failed: {str(e)}")

@app.get("/system/status")
async def get_system_status():
    """Get comprehensive system status including CrewAI"""
    try:
        status = orchestrator.get_system_status()
        status.update({
            "timestamp": datetime.utcnow().isoformat(),
            "active_documents": len(processing_status),
            "completed_analyses": len(analysis_results)
        })
        return status
    except Exception as e:
        logger.error(f"System status error: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/analysis/{document_id}/enhanced")
async def get_enhanced_analysis_results(document_id: str):
    """Get enhanced analysis results including CrewAI insights"""
    if document_id not in analysis_results:
        if document_id not in processing_status:
            raise HTTPException(status_code=404, detail="Document not found")
        
        status = processing_status[document_id]
        if status.status in ["processing", "uploaded"]:
            raise HTTPException(
                status_code=202, 
                detail="Document is still being processed"
            )
        elif status.status == "failed":
            raise HTTPException(
                status_code=500, 
                detail=f"Processing failed: {status.error_message}"
            )
    
    result = analysis_results[document_id]
    
    enhanced_fields = [
        'legal_precedent_research',
        'consumer_rights_analysis', 
        'compliance_assessment',
        'negotiation_guidance',
        'alternatives_research'
    ]
    
    result_dict = result.dict() if hasattr(result, 'dict') else result.__dict__
    
    has_crew_enhancement = any(field in result_dict for field in enhanced_fields)
    
    return {
        **result_dict,
        "has_crew_enhancement": has_crew_enhancement,
        "enhanced_fields_available": [field for field in enhanced_fields if field in result_dict]
    }

async def process_document_enhanced_async(document_id: str, file_path: str, use_crew_enhancement: bool = True):
    """Enhanced background task with CrewAI processing"""
    try:
        processing_status[document_id].status = "processing"
        processing_status[document_id].progress = 10
        processing_status[document_id].current_step = "Starting enhanced document analysis"
        
        logger.info(f"Starting enhanced processing for document: {document_id} (CrewAI: {use_crew_enhancement})")
        
        # Use enhanced orchestrator
        result = await orchestrator.process_document(
            file_path, document_id, processing_status, use_crew_enhancement
        )
        
        analysis_results[document_id] = result
        processing_status[document_id].status = "completed"
        processing_status[document_id].progress = 100
        processing_status[document_id].current_step = "Enhanced analysis completed"
        processing_status[document_id].end_time = datetime.utcnow()
        
        logger.info(f"Enhanced processing completed for document: {document_id}")
        
    except Exception as e:
        logger.error(f"Enhanced processing error for {document_id}: {str(e)}")
        
        user_message = f"Document processing encountered an error: {str(e)}"
        
        processing_status[document_id].status = "failed"
        processing_status[document_id].error_message = user_message
        processing_status[document_id].end_time = datetime.utcnow()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LegalClarity AI Backend with CrewAI Enhancement",
        "version": "2.0.0",
        "features": [
            "Document Analysis",
            "Risk Assessment", 
            "CrewAI Expert Agents",
            "Legal Research",
            "Negotiation Strategies",
            "Alternative Solutions"
        ],
        "endpoints": {
            "upload": "/upload (basic analysis)",
            "enhanced_upload": "/upload/enhanced (with CrewAI)",
            "status": "/status/{document_id}",
            "analysis": "/analysis/{document_id}",
            "enhanced_analysis": "/analysis/{document_id}/enhanced",
            "query": "/query",
            "system_status": "/system/status"
        },
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)