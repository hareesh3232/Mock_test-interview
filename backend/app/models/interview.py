"""
Interview model for storing interview sessions and Q&A data
"""
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    # Interview configuration
    interview_type = Column(String, default="standard")  # standard, behavioral, technical
    difficulty_level = Column(String, default="medium")  # easy, medium, hard
    question_count = Column(Integer, default=5)
    time_limit_minutes = Column(Integer, default=30)
    
    # Interview content
    questions = Column(JSON, default=list)  # List of generated questions
    answers = Column(JSON, default=list)  # List of user answers
    
    # Session data
    current_question_index = Column(Integer, default=0)
    status = Column(String, default="pending")  # pending, in_progress, completed, abandoned
    
    # AI-generated content metadata
    questions_generated_at = Column(DateTime(timezone=True))
    ai_model_used = Column(String)  # gpt-3.5-turbo, gpt-4, etc.
    prompt_version = Column(String)  # For tracking prompt changes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    result = relationship("Result", back_populates="interview", uselist=False)
    
    def __repr__(self):
        return f"<Interview(id={self.id}, user_id={self.user_id}, status={self.status})>"
    
    @property
    def duration_minutes(self) -> int:
        """Calculate interview duration in minutes"""
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            return int(duration.total_seconds() / 60)
        return 0
    
    @property
    def progress_percentage(self) -> float:
        """Get interview completion percentage"""
        if self.question_count == 0:
            return 0.0
        return (self.current_question_index / self.question_count) * 100
    
    @property
    def answered_questions_count(self) -> int:
        """Get number of answered questions"""
        return len(self.answers) if self.answers else 0
    
    @property
    def is_completed(self) -> bool:
        """Check if interview is completed"""
        return self.status == "completed"
    
    @property
    def is_in_progress(self) -> bool:
        """Check if interview is in progress"""
        return self.status == "in_progress"
    
    def get_current_question(self) -> dict:
        """Get current question object"""
        if (self.questions and 
            0 <= self.current_question_index < len(self.questions)):
            return self.questions[self.current_question_index]
        return {}
    
    def get_question_by_index(self, index: int) -> dict:
        """Get question by index"""
        if self.questions and 0 <= index < len(self.questions):
            return self.questions[index]
        return {}
    
    def add_answer(self, question_index: int, answer: str, time_taken_seconds: int = None):
        """Add an answer to the interview"""
        if not self.answers:
            self.answers = []
        
        answer_data = {
            "question_index": question_index,
            "answer": answer,
            "answered_at": func.now().isoformat(),
            "time_taken_seconds": time_taken_seconds
        }
        
        # Update existing answer or add new one
        existing_answer_index = None
        for i, existing_answer in enumerate(self.answers):
            if existing_answer.get("question_index") == question_index:
                existing_answer_index = i
                break
        
        if existing_answer_index is not None:
            self.answers[existing_answer_index] = answer_data
        else:
            self.answers.append(answer_data)
    
    def mark_as_started(self):
        """Mark interview as started"""
        self.status = "in_progress"
        self.started_at = func.now()
    
    def mark_as_completed(self):
        """Mark interview as completed"""
        self.status = "completed"
        self.completed_at = func.now()
    
    def to_dict(self):
        """Convert interview to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "resume_id": str(self.resume_id),
            "job_id": str(self.job_id),
            "interview_type": self.interview_type,
            "difficulty_level": self.difficulty_level,
            "question_count": self.question_count,
            "time_limit_minutes": self.time_limit_minutes,
            "questions": self.questions,
            "answers": self.answers,
            "current_question_index": self.current_question_index,
            "status": self.status,
            "progress_percentage": self.progress_percentage,
            "answered_questions_count": self.answered_questions_count,
            "duration_minutes": self.duration_minutes,
            "ai_model_used": self.ai_model_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

