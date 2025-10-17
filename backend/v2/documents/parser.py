"""
Document parsing utilities for PDF and DOCX files.

Supports:
- PDF parsing with PyMuPDF (fitz)
- DOCX parsing with python-docx
"""

import logging
import fitz  # PyMuPDF
from docx import Document
from typing import Optional
import hashlib

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str) -> Optional[str]:
    """
    Extract text from PDF file using PyMuPDF.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text or None if parsing fails
    """
    try:
        logger.info(f"Parsing PDF: {file_path}")
        doc = fitz.open(file_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        
        doc.close()
        
        logger.info(f"PDF parsed successfully: {len(text)} characters")
        return text.strip()
        
    except Exception as e:
        logger.error(f"PDF parsing failed: {str(e)}")
        return None


def parse_docx(file_path: str) -> Optional[str]:
    """
    Extract text from DOCX file using python-docx.
    
    Args:
        file_path: Path to DOCX file
        
    Returns:
        Extracted text or None if parsing fails
    """
    try:
        logger.info(f"Parsing DOCX: {file_path}")
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        logger.info(f"DOCX parsed successfully: {len(text)} characters")
        return text.strip()
        
    except Exception as e:
        logger.error(f"DOCX parsing failed: {str(e)}")
        return None


def parse_document(file_path: str, file_type: str) -> Optional[str]:
    """
    Parse document based on file type.
    
    Args:
        file_path: Path to document file
        file_type: File extension ('pdf' or 'docx')
        
    Returns:
        Extracted text or None if parsing fails
    """
    file_type = file_type.lower().replace('.', '')
    
    if file_type == 'pdf':
        return parse_pdf(file_path)
    elif file_type in ['docx', 'doc']:
        return parse_docx(file_path)
    else:
        logger.error(f"Unsupported file type: {file_type}")
        return None


def compute_text_hash(text: str) -> str:
    """
    Compute SHA-256 hash of text for deduplication.
    
    Args:
        text: Input text
        
    Returns:
        SHA-256 hash as hex string
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def validate_text_content(text: Optional[str], min_length: int = 50) -> bool:
    """
    Validate that extracted text has sufficient content.
    
    Args:
        text: Extracted text
        min_length: Minimum character count
        
    Returns:
        True if text is valid, False otherwise
    """
    if not text:
        return False
    
    text = text.strip()
    return len(text) >= min_length
