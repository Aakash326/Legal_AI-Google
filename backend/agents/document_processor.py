import time
import os
from pathlib import Path
from typing import Dict, Any
import logging

from models.document import ProcessedDocument, DocumentType
from utils.pdf_parser import pdf_parser
from utils.text_processor import text_processor
from services.modern_gemini_service import get_modern_gemini_service

logger = logging.getLogger(__name__)

class DocumentProcessorAgent:
    def __init__(self):
        self.gemini_service = get_modern_gemini_service()
        
    async def process_document(self, file_path: str, document_id: str) -> ProcessedDocument:
        """Process uploaded document and extract text"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing document: {file_path}")
            
            # Determine file type
            file_extension = Path(file_path).suffix.lower()
            
            # Extract text based on file type
            if file_extension == '.pdf':
                extracted_text, metadata = pdf_parser.extract_text(file_path)
            elif file_extension == '.docx':
                extracted_text, metadata = text_processor.extract_text_from_docx(file_path)
            elif file_extension == '.txt':
                extracted_text, metadata = text_processor.extract_text_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Clean the extracted text
            cleaned_text = text_processor.clean_text(extracted_text)
            
            if not cleaned_text.strip():
                raise ValueError("No text could be extracted from the document")
            
            # Classify document type using Gemini
            document_type = await self._classify_document_type(cleaned_text)
            
            # Chunk the text for processing
            chunks = text_processor.chunk_text(cleaned_text)
            
            # Calculate additional metadata
            word_count = text_processor.get_word_count(cleaned_text)
            processing_time = time.time() - start_time
            
            # Get page count if available
            page_count = metadata.get("page_count", 0)
            if page_count == 0 and file_extension == '.pdf':
                try:
                    page_count = pdf_parser.get_page_count(file_path)
                except Exception:
                    page_count = 0
            
            # Create processed document
            processed_doc = ProcessedDocument(
                document_id=document_id,
                document_type=document_type,
                extracted_text=cleaned_text,
                chunks=chunks,
                metadata={
                    **metadata,
                    "file_path": file_path,
                    "file_extension": file_extension,
                    "chunks_count": len(chunks)
                },
                processing_time=processing_time,
                word_count=word_count,
                page_count=page_count
            )
            
            logger.info(
                f"Document processed successfully. "
                f"Type: {document_type.value}, "
                f"Words: {word_count}, "
                f"Pages: {page_count}, "
                f"Chunks: {len(chunks)}, "
                f"Time: {processing_time:.2f}s"
            )
            
            return processed_doc
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            raise
    
    async def _classify_document_type(self, text: str) -> DocumentType:
        """Classify the type of legal document using Gemini"""
        document_type = await self.gemini_service.classify_document(text)
        logger.info(f"Document classified as: {document_type.value}")
        return document_type
    
    
    def get_document_stats(self, processed_doc: ProcessedDocument) -> Dict[str, Any]:
        """Get statistics about the processed document"""
        return {
            "document_id": processed_doc.document_id,
            "document_type": processed_doc.document_type.value,
            "word_count": processed_doc.word_count,
            "page_count": processed_doc.page_count,
            "chunk_count": len(processed_doc.chunks),
            "processing_time": processed_doc.processing_time,
            "average_chunk_size": sum(len(chunk) for chunk in processed_doc.chunks) / len(processed_doc.chunks) if processed_doc.chunks else 0,
            "text_length": len(processed_doc.extracted_text)
        }
    
    def validate_document(self, file_path: str) -> Dict[str, Any]:
        """Validate document before processing"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "file_info": {}
        }
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                validation_result["valid"] = False
                validation_result["errors"].append("File does not exist")
                return validation_result
            
            # Check file size
            file_size = os.path.getsize(file_path)
            validation_result["file_info"]["size_bytes"] = file_size
            validation_result["file_info"]["size_mb"] = file_size / (1024 * 1024)
            
            # Size limits (50MB max)
            if file_size > 50 * 1024 * 1024:
                validation_result["valid"] = False
                validation_result["errors"].append("File size exceeds 50MB limit")
            elif file_size > 10 * 1024 * 1024:
                validation_result["warnings"].append("Large file size may take longer to process")
            
            # Check file extension
            file_extension = Path(file_path).suffix.lower()
            validation_result["file_info"]["extension"] = file_extension
            
            allowed_extensions = ['.pdf', '.docx', '.txt']
            if file_extension not in allowed_extensions:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Unsupported file type: {file_extension}")
            
            # Basic file content check
            if file_extension == '.txt':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(100)  # Read first 100 chars
                        if not content.strip():
                            validation_result["valid"] = False
                            validation_result["errors"].append("Text file appears to be empty")
                except UnicodeDecodeError:
                    validation_result["warnings"].append("Text file encoding may cause issues")
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"File validation error: {str(e)}")
        
        return validation_result