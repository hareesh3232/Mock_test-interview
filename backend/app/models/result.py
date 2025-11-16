"""
Result model for storing interview evaluation and scoring data
"""
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Result(Base):
    __tablename__ = "results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id"), nullable=False, unique=True)
    
    # Core scoring metrics (0.0 to 100.0)
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    job_match_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    
    # Detailed scoring breakdown
    individual_scores = Column(JSON, default=list)  # Score for each question
    
    # AI-generated feedback
    strengths = Column(JSON, default=list)  # List of identified strengths
    weaknesses = Column(JSON, default=list)  # List of areas for improvement
    recommendations = Column(JSON, default=list)  # Specific recommendations
    
    # Detailed analysis
    technical_feedback = Column(Text)  # Detailed technical analysis
    communication_feedback = Column(Text)  # Communication skills analysis
    overall_feedback = Column(Text)  # General interview feedback
    
    # Performance metrics
    response_quality_score = Column(Float, default=0.0)  # Quality of answers
    relevance_score = Column(Float, default=0.0)  # Relevance to job requirements
    depth_score = Column(Float, default=0.0)  # Depth of technical knowledge
    clarity_score = Column(Float, default=0.0)  # Communication clarity
    
    # AI evaluation metadata
    evaluation_model = Column(String)  # AI model used for evaluation
    evaluation_version = Column(String)  # Version of evaluation prompt
    confidence_score = Column(Float)  # AI confidence in evaluation (0.0-1.0)
    
    # Comparative data
    percentile_rank = Column(Float)  # Rank compared to other candidates
    industry_average_score = Column(Float)  # Average score for similar roles
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    interview = relationship("Interview", back_populates="result")
    
    def __repr__(self):
        return f"<Result(id={self.id}, interview_id={self.interview_id}, overall_score={self.overall_score})>"
    
    @property
    def performance_level(self) -> str:
        """Get performance level based on overall score"""
        if self.overall_score >= 90:
            return "Excellent"
        elif self.overall_score >= 80:
            return "Very Good"
        elif self.overall_score >= 70:
            return "Good"
        elif self.overall_score >= 60:
            return "Fair"
        else:
            return "Needs Improvement"
    
    @property
    def score_breakdown(self) -> dict:
        """Get comprehensive score breakdown"""
        return {
            "technical": self.technical_score,
            "communication": self.communication_score,
            "job_match": self.job_match_score,
            "overall": self.overall_score,
            "response_quality": self.response_quality_score,
            "relevance": self.relevance_score,
            "depth": self.depth_score,
            "clarity": self.clarity_score
        }
    
    @property
    def passing_score(self) -> bool:
        """Check if candidate achieved passing score (>= 70%)"""
        return self.overall_score >= 70.0
    
    def calculate_overall_score(self):
        """Calculate overall score from component scores"""
        # Weighted average calculation
        weights = {
            "technical": 0.4,
            "communication": 0.3,
            "job_match": 0.3
        }
        
        weighted_sum = (
            self.technical_score * weights["technical"] +
            self.communication_score * weights["communication"] +
            self.job_match_score * weights["job_match"]
        )
        
        self.overall_score = round(weighted_sum, 1)
        return self.overall_score
    
    def add_strength(self, strength: str):
        """Add a strength to the list"""
        if not self.strengths:
            self.strengths = []
        if strength not in self.strengths:
            self.strengths.append(strength)
    
    def add_weakness(self, weakness: str):
        """Add a weakness to the list"""
        if not self.weaknesses:
            self.weaknesses = []
        if weakness not in self.weaknesses:
            self.weaknesses.append(weakness)
    
    def add_recommendation(self, recommendation: str):
        """Add a recommendation to the list"""
        if not self.recommendations:
            self.recommendations = []
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
    
    def get_improvement_areas(self) -> list:
        """Get areas that need improvement (scores < 70)"""
        improvement_areas = []
        scores = self.score_breakdown
        
        for area, score in scores.items():
            if score < 70.0:
                improvement_areas.append({
                    "area": area.replace("_", " ").title(),
                    "score": score,
                    "improvement_needed": 70.0 - score
                })
        
        return improvement_areas
    
    def to_dict(self):
        """Convert result to dictionary"""
        return {
            "id": str(self.id),
            "interview_id": str(self.interview_id),
            "scores": self.score_breakdown,
            "overall_score": self.overall_score,
            "performance_level": self.performance_level,
            "passing_score": self.passing_score,
            "individual_scores": self.individual_scores,
            "feedback": {
                "strengths": self.strengths,
                "weaknesses": self.weaknesses,
                "recommendations": self.recommendations,
                "technical": self.technical_feedback,
                "communication": self.communication_feedback,
                "overall": self.overall_feedback
            },
            "improvement_areas": self.get_improvement_areas(),
            "percentile_rank": self.percentile_rank,
            "industry_average_score": self.industry_average_score,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

