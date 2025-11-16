"""
Resume model for storing uploaded resumes and extracted data
"""
import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # File information
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(String)
    file_type = Column(String)
    
    # Extracted content
    extracted_text = Column(Text)
    
    # Parsed data (JSON fields)
    skills = Column(JSON, default=list)  # List of skills
    education = Column(JSON, default=list)  # List of education entries
    experience = Column(JSON, default=list)  # List of work experience
    personal_info = Column(JSON, default=dict)  # Name, contact info, etc.
    certifications = Column(JSON, default=list)  # Professional certifications
    
    # Metadata
    parsing_status = Column(String, default="pending")  # pending, completed, failed
    parsing_confidence = Column(String)  # low, medium, high
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    interviews = relationship("Interview", back_populates="resume")
    
    def __repr__(self):
        return f"<Resume(id={self.id}, filename={self.filename}, user_id={self.user_id})>"
    
    @property
    def total_skills(self) -> int:
        """Get total number of extracted skills"""
        return len(self.skills) if self.skills else 0
    
    @property
    def years_of_experience(self) -> int:
        """Calculate total years of experience"""
        if not self.experience:
            return 0
        
        total_years = 0
        for exp in self.experience:
            if isinstance(exp, dict) and "duration_years" in exp:
                total_years += exp.get("duration_years", 0)
        
        return total_years
    
    @property
    def education_level(self) -> str:
        """Get highest education level"""
        if not self.education:
            return "Unknown"
        
        # Simple education level detection
        levels = ["PhD", "Masters", "Bachelor", "Associate", "High School"]
        for level in levels:
            for edu in self.education:
                if isinstance(edu, dict):
                    degree = edu.get("degree", "").lower()
                    if level.lower() in degree:
                        return level
        
        return "Other"
    
    def to_dict(self):
        """Convert resume to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "filename": self.filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "skills": self.skills,
            "education": self.education,
            "experience": self.experience,
            "personal_info": self.personal_info,
            "certifications": self.certifications,
            "parsing_status": self.parsing_status,
            "parsing_confidence": self.parsing_confidence,
            "total_skills": self.total_skills,
            "years_of_experience": self.years_of_experience,
            "education_level": self.education_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

