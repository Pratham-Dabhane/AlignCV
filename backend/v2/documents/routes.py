"""
Document upload and management routes for AlignCV V2.

Endpoints:
- POST /v2/upload - Upload PDF/DOCX document
- GET /v2/documents - List user's documents
- GET /v2/documents/{doc_id} - Get specific document
- DELETE /v2/documents/{doc_id} - Delete document
"""

import logging
import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from typing import List, Optional

from ..database import get_db
from ..auth.utils import decode_token
from .parser import parse_document, compute_text_hash, validate_text_content
from ..nlp.extractor import extract_all
from ..storage.handler import get_storage
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v2/documents", tags=["Documents"])

# Security scheme for JWT authentication
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_db)
):
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials with JWT token
        db: Supabase client
        
    Returns:
        dict: Current authenticated user
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials
    email = decode_token(token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    result = db.table('users').select('*').eq('email', email).execute()
    user = result.data[0] if result.data else None
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    Upload and parse a PDF or DOCX document.
    
    Args:
        file: Uploaded file (PDF or DOCX)
        current_user: Authenticated user (dict)
        db: Supabase client
        
    Returns:
        Dict with upload status
        
    Raises:
        HTTPException: 400 if file is invalid or too large
    """
    logger.info(f"Document upload attempt by user {current_user['id']}: {file.filename}")
    
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
        )
    
    # Save to temporary file for parsing
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Parse document
        extracted_text = parse_document(temp_path, file_ext)
        
        if not extracted_text or not validate_text_content(extracted_text):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to extract text from document or content is too short"
            )
        
        logger.info(f"Text extracted: {len(extracted_text)} characters")
        
        # Extract skills, roles, and entities
        nlp_data = extract_all(extracted_text)
        logger.info(f"NLP extraction complete: {len(nlp_data.get('skills', []))} skills found")
        
        # Compute text hash
        text_hash = compute_text_hash(extracted_text)
        
        # Save file to storage
        storage = get_storage()
        storage_path = storage.save_file(temp_path, current_user['id'], file.filename)
        
        # Save to database
        document_data = {
            'user_id': current_user['id'],
            'file_name': file.filename,
            'file_type': file_ext.replace('.', ''),
            'file_size': file_size,
            'file_path': storage_path,
            'status': 'uploaded',
            'parsed_content': {
                'text': extracted_text,
                'text_hash': text_hash,
                'skills': nlp_data.get('skills', []),
                'roles': nlp_data.get('roles', []),
                'entities': nlp_data.get('entities', {})
            }
        }
        
        result = db.table('documents').insert(document_data).execute()
        document = result.data[0]
        
        logger.info(f"✅ Document saved: {document['id']} for user {current_user['id']}")
        
        return {
            "document_id": document['id'],
            "message": "Document uploaded and parsed successfully",
            "file_name": file.filename,
            "storage_path": storage_path,
            "file_size": file_size,
            "text_length": len(extracted_text),
            "parsed_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "skills": nlp_data.get("skills", []),
            "roles": nlp_data.get("roles", []),
            "entities": nlp_data.get("entities", {})
        }
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@router.get("/")
def list_documents(
    current_user = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    List all documents for current user.
    
    Args:
        current_user: Authenticated user (dict)
        db: Supabase client
        
    Returns:
        List of user's documents
    """
    result = db.table('documents').select('*').eq('user_id', current_user['id']).order('created_at', desc=True).execute()
    documents = result.data
    
    # Normalize field names for backwards compatibility
    for doc in documents:
        # If document has 'filename', rename it to 'file_name'
        if 'filename' in doc and 'file_name' not in doc:
            doc['file_name'] = doc.pop('filename')
    
    return {
        "documents": documents,
        "total": len(documents)
    }


@router.get("/{doc_id}")
def get_document(
    doc_id: str,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    Get specific document details.
    
    Args:
        doc_id: Document ID (UUID)
        current_user: Authenticated user (dict)
        db: Supabase client
        
    Returns:
        Document details with full text
        
    Raises:
        HTTPException: 404 if document not found or doesn't belong to user
    """
    result = db.table('documents').select('*').eq('id', doc_id).eq('user_id', current_user['id']).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document = result.data[0]
    
    # Normalize field name for backwards compatibility
    if 'filename' in document and 'file_name' not in document:
        document['file_name'] = document.pop('filename')
    
    return document


@router.delete("/{doc_id}")
def delete_document(
    doc_id: str,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    Delete document.
    
    Args:
        doc_id: Document ID (UUID)
        current_user: Authenticated user (dict)
        db: Supabase client
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if document not found or doesn't belong to user
    """
    result = db.table('documents').select('*').eq('id', doc_id).eq('user_id', current_user['id']).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document = result.data[0]
    
    # Delete file from storage
    try:
        storage = get_storage()
        storage.delete_file(document['file_path'])
    except Exception as e:
        logger.warning(f"Failed to delete file from storage: {str(e)}")
    
    # Delete from database
    db.table('documents').delete().eq('id', doc_id).execute()
    
    logger.info(f"Document deleted: {doc_id} by user {current_user['id']}")
    
    return {"message": "Document deleted successfully"}
