"""
Job model for storing job listings and requirements
"""
import uuid
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic job information
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Job requirements and details
    requirements = Column(JSON, default=list)  # List of job requirements
    skills_required = Column(JSON, default=list)  # Required technical skills
    qualifications = Column(JSON, default=list)  # Educational/experience qualifications
    
    # Location and compensation
    location = Column(String)
    remote_work = Column(Boolean, default=False)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String, default="USD")
    
    # Job metadata
    job_type = Column(String)  # full-time, part-time, contract, internship
    experience_level = Column(String)  # entry, mid, senior, executive
    industry = Column(String)
    department = Column(String)
    
    # External job data
    external_id = Column(String)  # ID from job search API
    external_url = Column(String)  # Link to original job posting
    source = Column(String, default="mock")  # mock, adzuna, linkedin, etc.
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    posting_date = Column(DateTime(timezone=True))
    expiry_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    interviews = relationship("Interview", back_populates="job")
    
    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title}, company={self.company})>"
    
    @property
    def salary_range(self) -> str:
        """Get formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,} - {self.salary_max:,}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to {self.salary_currency} {self.salary_max:,}"
        return "Salary not specified"
    
    @property
    def total_skills_required(self) -> int:
        """Get total number of required skills"""
        return len(self.skills_required) if self.skills_required else 0
    
    def calculate_match_score(self, candidate_skills: list) -> float:
        """
        Calculate how well candidate skills match job requirements
        Returns a score between 0.0 and 1.0
        """
        if not self.skills_required or not candidate_skills:
            return 0.0
        
        # Convert to lowercase for case-insensitive matching
        job_skills = [skill.lower() for skill in self.skills_required]
        user_skills = [skill.lower() for skill in candidate_skills]
        
        # Calculate intersection
        matching_skills = set(job_skills) & set(user_skills)
        
        # Score based on percentage of job requirements met
        match_score = len(matching_skills) / len(job_skills)
        return round(match_score, 2)
    
    def to_dict(self, candidate_skills: list = None):
        """Convert job to dictionary"""
        job_dict = {
            "id": str(self.id),
            "title": self.title,
            "company": self.company,
            "description": self.description,
            "requirements": self.requirements,
            "skills_required": self.skills_required,
            "qualifications": self.qualifications,
            "location": self.location,
            "remote_work": self.remote_work,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "salary_range": self.salary_range,
            "job_type": self.job_type,
            "experience_level": self.experience_level,
            "industry": self.industry,
            "department": self.department,
            "external_url": self.external_url,
            "source": self.source,
            "total_skills_required": self.total_skills_required,
            "posting_date": self.posting_date.isoformat() if self.posting_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        # Add match score if candidate skills provided
        if candidate_skills:
            job_dict["match_score"] = self.calculate_match_score(candidate_skills)
        
        return job_dict

