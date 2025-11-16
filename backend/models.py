"""
SQLAlchemy models for the Mock Interview System
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from database import Base

class InterviewStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    resumes = relationship("Resume", back_populates="user")
    interviews = relationship("Interview", back_populates="user")

class Resume(Base):
    """Resume model"""
    __tablename__ = "resumes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    parsed_data = Column(JSON)  # Structured resume data
    skills = Column(JSON, default=list)  # Extracted skills
    experience_years = Column(Float, default=0.0)
    education_level = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    interviews = relationship("Interview", back_populates="resume")

class Job(Base):
    """Job model"""
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(JSON, default=list)
    skills_required = Column(JSON, default=list)
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10), default="USD")
    job_type = Column(String(50))  # full-time, part-time, contract
    experience_level = Column(String(50))  # entry, mid, senior
    remote_work = Column(Boolean, default=False)
    job_url = Column(String(500))
    source = Column(String(100))  # linkedin, indeed, etc.
    posted_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Interview(Base):
    """Interview session model"""
    __tablename__ = "interviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    questions = Column(JSON)  # List of interview questions
    answers = Column(JSON, default=list)  # List of answers and evaluations
    status = Column(Enum(InterviewStatus), default=InterviewStatus.PENDING)
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    feedback = Column(JSON)  # Final feedback report
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    job = relationship("Job")
    qa_pairs = relationship("QAPair", back_populates="interview")

class QAPair(Base):
    """Question-Answer pair model"""
    __tablename__ = "qa_pairs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    question_type = Column(String(50))  # technical, behavioral, scenario
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    feedback = Column(Text)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    interview = relationship("Interview", back_populates="qa_pairs")
