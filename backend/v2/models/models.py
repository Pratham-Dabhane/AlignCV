"""
Database models for AlignCV V2.

Models:
- User: User accounts with email/password or Google OAuth
- Document: Uploaded resumes/CVs with parsed content
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
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
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_text_hash', 'text_hash'),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, user_id={self.user_id}, file_name='{self.file_name}')>"
