"""
Database models for AlignCV V2.

Models:
- User: User accounts with email/password or Google OAuth
- Document: Uploaded resumes/CVs with parsed content
- DocumentVersion: Rewritten versions of documents with AI metadata
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class User(Base):
    """
    User account model.
    
    Supports both email/password and Google OAuth authentication.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    google_id = Column(String(255), unique=True, nullable=True, index=True)  # Google OAuth ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    document_versions = relationship("DocumentVersion", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"


class Document(Base):
    """
    Uploaded document model (resume/CV).
    
    Stores file metadata and extracted text content.
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # 'pdf' or 'docx'
    file_size = Column(Integer, nullable=False)  # Size in bytes
    storage_url = Column(Text, nullable=False)  # S3 URL or local path
    text_hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash of extracted text
    extracted_text = Column(Text, nullable=False)  # Full text content
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_text_hash', 'text_hash'),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, user_id={self.user_id}, file_name='{self.file_name}')>"


class DocumentVersion(Base):
    """
    Document version model (AI-rewritten resume versions).
    
    Stores original and rewritten text with metadata about improvements.
    """
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_text = Column(Text, nullable=False)  # Original resume text
    rewritten_text = Column(Text, nullable=False)  # AI-rewritten text
    rewrite_style = Column(String(50), nullable=False)  # Technical, Management, Creative
    improvements = Column(JSON, nullable=False)  # List of improvements made
    impact_score = Column(Integer, nullable=False, default=0)  # 0-100 score
    keyphrases = Column(JSON, nullable=True)  # Extracted keyphrases
    api_latency = Column(Float, nullable=False, default=0.0)  # API call latency in seconds
    api_status = Column(String(20), nullable=False)  # success, fallback, error
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    document = relationship("Document", back_populates="versions")
    user = relationship("User", back_populates="document_versions")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_doc_created', 'document_id', 'created_at'),
        Index('idx_user_style', 'user_id', 'rewrite_style'),
    )
    
    def __repr__(self):
        return f"<DocumentVersion(id={self.id}, document_id={self.document_id}, style='{self.rewrite_style}')>"
