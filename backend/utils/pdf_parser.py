import PyPDF2
import pdfplumber
import os
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self):
        pass
    
    def extract_text_pypdf2(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text using PyPDF2 (basic extraction)"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                text = ""
                metadata = {
                    "page_count": len(pdf_reader.pages),
                    "title": pdf_reader.metadata.title if pdf_reader.metadata and pdf_reader.metadata.title else "",
                    "author": pdf_reader.metadata.author if pdf_reader.metadata and pdf_reader.metadata.author else "",
                    "creator": pdf_reader.metadata.creator if pdf_reader.metadata and pdf_reader.metadata.creator else "",
                    "extraction_method": "pypdf2"
                }
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
                        continue
                
                return text, metadata
                
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {str(e)}")
            raise
    
    def extract_text_pdfplumber(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text using pdfplumber (better formatting preservation)"""
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                metadata = {
                    "page_count": len(pdf.pages),
                    "extraction_method": "pdfplumber"
                }
                
                # Try to get document metadata
                if hasattr(pdf, 'metadata') and pdf.metadata:
                    metadata.update({
                        "title": pdf.metadata.get("Title", ""),
                        "author": pdf.metadata.get("Author", ""),
                        "creator": pdf.metadata.get("Creator", ""),
                        "creation_date": str(pdf.metadata.get("CreationDate", ""))
                    })
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            # Preserve some structure
                            cleaned_text = self._clean_page_text(page_text)
                            text += f"\n--- Page {page_num + 1} ---\n{cleaned_text}\n"
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
                        continue
                
                return text, metadata
                
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            raise
    
    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text from PDF using the best available method"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Try pdfplumber first (better text extraction)
        try:
            text, metadata = self.extract_text_pdfplumber(file_path)
            if text.strip():  # If we got meaningful text
                return text, metadata
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {str(e)}")
        
        # Fallback to PyPDF2
        try:
            text, metadata = self.extract_text_pypdf2(file_path)
            return text, metadata
        except Exception as e:
            logger.error(f"All PDF extraction methods failed: {str(e)}")
            raise ValueError(f"Could not extract text from PDF: {str(e)}")
    
    def _clean_page_text(self, text: str) -> str:
        """Clean and normalize page text"""
        if not text:
            return ""
        
        # Remove excessive whitespace while preserving structure
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Strip whitespace but keep non-empty lines
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
            elif cleaned_lines and cleaned_lines[-1]:  # Preserve paragraph breaks
                cleaned_lines.append("")
        
        # Join lines back together
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove excessive blank lines (more than 2 consecutive)
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
        return cleaned_text
    
    def get_page_count(self, file_path: str) -> int:
        """Get the number of pages in a PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            logger.error(f"Failed to get page count: {str(e)}")
            return 0
    
    def extract_text_from_page(self, file_path: str, page_num: int) -> str:
        """Extract text from a specific page (0-indexed)"""
        try:
            with pdfplumber.open(file_path) as pdf:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    return page.extract_text() or ""
                else:
                    raise ValueError(f"Page {page_num + 1} does not exist in the PDF")
        except Exception as e:
            logger.error(f"Failed to extract text from page {page_num + 1}: {str(e)}")
            return ""

# Global instance
pdf_parser = PDFParser()