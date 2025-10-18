"""
Database models for AlignCV V2.

Models:
- User: User accounts with email/password or Google OAuth
- Document: Uploaded resumes/CVs with parsed content
- DocumentVersion: Rewritten versions of documents with AI metadata
- Job: Job postings from various sources
- JobBookmark: User-saved jobs
- JobApplication: User job applications
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
    bookmarks = relationship("JobBookmark", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
    notification_settings = relationship("NotificationSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
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


class Job(Base):
    """
    Job posting model.
    
    Stores job listings from various sources with normalized fields.
    """
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(255), unique=True, nullable=False, index=True)  # External job ID
    source = Column(String(50), nullable=False, index=True)  # linkedin, angellist, indeed, etc.
    title = Column(String(500), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)  # Skills, technologies, etc.
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    employment_type = Column(String(50), nullable=True)  # full-time, part-time, contract
    experience_level = Column(String(50), nullable=True)  # entry, mid, senior
    vector_id = Column(String(255), nullable=True, index=True)  # Qdrant vector ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    bookmarks = relationship("JobBookmark", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="job", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_source_created', 'source', 'created_at'),
        Index('idx_company_title', 'company', 'title'),
    )
    
    def __repr__(self):
        return f"<Job(id={self.id}, job_id='{self.job_id}', title='{self.title}', company='{self.company}')>"


class JobBookmark(Base):
    """
    Job bookmark model.
    
    Tracks user-saved jobs for later review.
    """
    __tablename__ = "job_bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    job = relationship("Job", back_populates="bookmarks")
    
    # Unique constraint: user can only bookmark a job once
    __table_args__ = (
        Index('idx_user_job_unique', 'user_id', 'job_id', unique=True),
    )
    
    def __repr__(self):
        return f"<JobBookmark(id={self.id}, user_id={self.user_id}, job_id={self.job_id})>"


class JobApplication(Base):
    """
    Job application model.
    
    Tracks jobs the user has applied to.
    """
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="applied")  # applied, interviewing, offered, rejected
    applied_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    
    # Unique constraint: user can only apply to a job once
    __table_args__ = (
        Index('idx_user_job_app_unique', 'user_id', 'job_id', unique=True),
        Index('idx_user_status', 'user_id', 'status'),
    )
    
    def __repr__(self):
        return f"<JobApplication(id={self.id}, user_id={self.user_id}, job_id={self.job_id}, status='{self.status}')>"


class NotificationSettings(Base):
    """
    User notification preferences (Phase 7).
    
    Controls email digest frequency and notification types.
    """
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Email notification settings
    email_enabled = Column(Integer, nullable=False, default=1)  # SQLite doesn't have boolean, use 1/0
    digest_frequency = Column(String(20), nullable=False, default="daily")  # daily, weekly, disabled
    
    # Notification types
    notify_new_matches = Column(Integer, nullable=False, default=1)  # Notify on new job matches
    notify_application_updates = Column(Integer, nullable=False, default=1)  # Notify on application status changes
    
    # Matching thresholds
    min_match_score = Column(Float, nullable=False, default=0.85)  # Only notify if match > 85%
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notification_settings")
    
    def __repr__(self):
        return f"<NotificationSettings(user_id={self.user_id}, digest={self.digest_frequency}, enabled={bool(self.email_enabled)})>"


class Notification(Base):
    """
    Notification history (Phase 7).
    
    Stores all notifications sent to users.
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Notification details
    type = Column(String(50), nullable=False)  # job_match, application_update, digest
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Job reference (if applicable)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    match_score = Column(Float, nullable=True)  # For job_match type
    
    # Email delivery status
    email_sent = Column(Integer, nullable=False, default=0)  # 0 = pending, 1 = sent
    email_sent_at = Column(DateTime, nullable=True)
    email_error = Column(Text, nullable=True)  # Store error if email failed
    
    # Read status
    is_read = Column(Integer, nullable=False, default=0)  # 0 = unread, 1 = read
    read_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    job = relationship("Job", back_populates="notifications")
    
    __table_args__ = (
        Index('idx_user_unread', 'user_id', 'is_read'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type}', read={bool(self.is_read)})>"
