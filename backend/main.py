"""
FastAPI main application for Mock Interview System
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import os
import uuid
import shutil
from datetime import datetime

from database import get_async_db, init_db, close_db
from models import User, Resume, Job, Interview, QAPair, InterviewStatus
from ai_service import GeminiService
from simple_resume_parser import SimpleResumeParser
from job_search_service import JobSearchService

# Global services
ai_service = GeminiService()
resume_parser = SimpleResumeParser()
job_search_service = JobSearchService()

# Request Models
class GenerateQuestionsRequest(BaseModel):
    resume_id: str
    job_id: str
    question_count: int = 10

class StartInterviewRequest(BaseModel):
    resume_id: str
    job_id: str
    questions: List[dict]

class SubmitAnswerRequest(BaseModel):
    interview_id: str
    question_index: int
    answer: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and services on startup"""
    # Initialize database
    await init_db()
    print("🚀 Mock Interview System initialized successfully!")
    yield
    # Cleanup on shutdown
    await close_db()
    print("👋 Shutting down Mock Interview System...")

# Create FastAPI app
app = FastAPI(
    title="Mock Interview System",
    description="AI-powered resume-based job-matched mock interview system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Mock Interview System API is running!", "status": "healthy"}

@app.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user_email: Optional[str] = Form(None),
    user_name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Upload and parse resume"""
    print(f"Received resume upload request: {file.filename}")
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
            raise HTTPException(status_code=400, detail="Only PDF, DOC, and DOCX files are allowed")
        
        # Save file
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = f"uploads/{file_id}{file_extension}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse resume
        parsed_data = await resume_parser.parse_resume(file_path, file.filename)
        
        # Create or get user
        user = None
        if user_email:
            result = await db.execute(select(User).where(User.email == user_email))
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(
                    email=user_email,
                    name=user_name or "Anonymous User"
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
        
        # Create resume record
        resume_data = parsed_data.get("parsed_data", {})
        resume = Resume(
            user_id=user.id if user else None,
            filename=file.filename,
            file_path=file_path,
            parsed_data=resume_data,
            skills=resume_data.get("skills", []),  
            experience_years=resume_data.get("experience_years", 0),
            education_level=resume_data.get("education_level", "Unknown")
        )
        
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        
        return {
            "resume_id": str(resume.id),
            "filename": resume.filename,
            "parsed_data": resume.parsed_data,
            "skills": resume.skills,
            "experience_years": resume.experience_years,
            "education_level": resume.education_level
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@app.get("/jobs/search")
async def search_jobs(
    skills: str,
    location: str = "us",
    count: int = 20,
    db: AsyncSession = Depends(get_async_db)
):
    """Search for jobs based on skills"""
    try:
        skills_list = [skill.strip() for skill in skills.split(",")]
        jobs = await job_search_service.search_jobs(skills_list, location, count)
        
        # Store jobs in database
        job_records = []
        for job_data in jobs:
            job = Job(
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"],
                description=job_data["description"],
                requirements=job_data.get("requirements", []),
                skills_required=job_data.get("skills_required", []),
                salary_min=job_data.get("salary_min"),
                salary_max=job_data.get("salary_max"),
                salary_currency=job_data.get("salary_currency", "USD"),
                job_type=job_data.get("job_type", "Full-time"),
                experience_level=job_data.get("experience_level", "Mid"),
                remote_work=job_data.get("remote_work", False),
                job_url=job_data.get("job_url"),
                source=job_data.get("source", "Mock API"),
                posted_date=job_data.get("posted_date", datetime.now())
            )
            db.add(job)
            job_records.append(job)
        
        await db.commit()
        
        # Refresh to get IDs
        for job in job_records:
            await db.refresh(job)
        
        return {
            "jobs": [
                {
                    "id": str(job.id),
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "description": job.description,
                    "requirements": job.requirements,
                    "skills_required": job.skills_required,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "salary_currency": job.salary_currency,
                    "job_type": job.job_type,
                    "experience_level": job.experience_level,
                    "remote_work": job.remote_work,
                    "job_url": job.job_url,
                    "source": job.source,
                    "posted_date": job.posted_date.isoformat() if job.posted_date else None
                }
                for job in job_records
            ],
            "total_count": len(job_records)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

@app.get("/jobs/{job_id}")
async def get_job_details(job_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get detailed information about a specific job"""
    try:
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "requirements": job.requirements,
            "skills_required": job.skills_required,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "job_type": job.job_type,
            "experience_level": job.experience_level,
            "remote_work": job.remote_work,
            "job_url": job.job_url,
            "source": job.source,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving job details: {str(e)}")

@app.post("/interview/generate")
async def generate_interview_questions(
    request: GenerateQuestionsRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Generate job-specific interview questions"""
    try:
        # Convert string IDs to UUIDs
        try:
            resume_uuid = uuid.UUID(request.resume_id)
            job_uuid = uuid.UUID(request.job_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")

        # Get resume and job data
        resume_result = await db.execute(select(Resume).where(Resume.id == resume_uuid))
        resume = resume_result.scalar_one_or_none()
        
        job_result = await db.execute(select(Job).where(Job.id == job_uuid))
        job = job_result.scalar_one_or_none()
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Generate questions using AI
        questions = await ai_service.generate_interview_questions(
            job_description=job.description,
            resume_skills=resume.skills,
            job_requirements=job.requirements,
            job_title=job.title,
            company_name=job.company,
            question_count=request.question_count
        )
        
        return {
            "resume_id": request.resume_id,
            "job_id": request.job_id,
            "questions": questions,
            "total_questions": len(questions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

@app.post("/interview/start")
async def start_interview(
    request: StartInterviewRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Start a new interview session"""
    try:
        # Convert string IDs to UUIDs
        try:
            resume_uuid = uuid.UUID(request.resume_id)
            job_uuid = uuid.UUID(request.job_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")

        # Get resume and job data
        resume_result = await db.execute(select(Resume).where(Resume.id == resume_uuid))
        resume = resume_result.scalar_one_or_none()
        
        job_result = await db.execute(select(Job).where(Job.id == job_uuid))
        job = job_result.scalar_one_or_none()
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Create interview record
        interview = Interview(
            user_id=resume.user_id,
            resume_id=resume_uuid,
            job_id=job_uuid,
            questions=request.questions,
            status=InterviewStatus.IN_PROGRESS
        )
        
        db.add(interview)
        await db.commit()
        await db.refresh(interview)
        
        return {
            "interview_id": str(interview.id),
            "resume_id": request.resume_id,
            "job_id": request.job_id,
            "questions": request.questions,
            "current_question_index": 0,
            "total_questions": len(request.questions),
            "status": interview.status.value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")

@app.post("/interview/submit")
async def submit_answer(
    request: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Submit an answer and get evaluation"""
    try:
        # Convert interview ID to UUID
        try:
            interview_uuid = uuid.UUID(request.interview_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")

        # Get interview data
        interview_result = await db.execute(select(Interview).where(Interview.id == interview_uuid))
        interview = interview_result.scalar_one_or_none()
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        if request.question_index >= len(interview.questions):
            raise HTTPException(status_code=400, detail="Invalid question index")
        
        current_question = interview.questions[request.question_index]
        
        # Evaluate answer using AI
        evaluation = await ai_service.evaluate_answer(
            question=current_question["question"],
            answer=request.answer,
            question_type=current_question.get("type", "technical"),
            expected_keywords=current_question.get("expected_keywords", [])
        )
        
        # Create QA pair record
        qa_pair = QAPair(
            interview_id=interview_uuid,
            question_text=current_question["question"],
            answer_text=request.answer,
            question_type=current_question.get("type", "technical"),
            technical_score=evaluation["technical_score"],
            communication_score=evaluation["communication_score"],
            relevance_score=evaluation["relevance_score"],
            overall_score=evaluation["overall_score"],
            feedback=evaluation["feedback"],
            strengths=evaluation["strengths"],
            weaknesses=evaluation["weaknesses"],
            suggestions=evaluation["suggestions"]
        )
        
        db.add(qa_pair)
        
        # Update interview answers
        current_answers = interview.answers or []
        current_answers.append({
            "question_index": request.question_index,
            "question": current_question,
            "answer": request.answer,
            "evaluation": evaluation
        })
        interview.answers = current_answers
        
        # Check if interview is complete
        is_complete = request.question_index + 1 >= len(interview.questions)
        
        if is_complete:
            interview.status = InterviewStatus.COMPLETED
            interview.completed_at = datetime.utcnow()
            
            # Calculate overall scores
            qa_pairs_result = await db.execute(
                select(QAPair).where(QAPair.interview_id == interview_uuid)
            )
            qa_pairs = qa_pairs_result.scalars().all()
            
            if qa_pairs:
                interview.technical_score = sum(qa.technical_score for qa in qa_pairs) / len(qa_pairs)
                interview.communication_score = sum(qa.communication_score for qa in qa_pairs) / len(qa_pairs)
                interview.overall_score = sum(qa.overall_score for qa in qa_pairs) / len(qa_pairs)
                
                # Generate final feedback
                interview_data = [
                    {
                        "question": qa.question_text,
                        "answer": qa.answer_text,
                        "scores": {
                            "technical": qa.technical_score,
                            "communication": qa.communication_score,
                            "overall": qa.overall_score
                        }
                    }
                    for qa in qa_pairs
                ]
                
                final_feedback = await ai_service.generate_final_feedback(interview_data)
                interview.feedback = final_feedback
        
        await db.commit()
        
        # Get next question if not complete
        next_question = None
        if not is_complete:
            next_question = interview.questions[request.question_index + 1]
        
        return {
            "interview_id": str(interview.id),
            "question_index": request.question_index,
            "evaluation": evaluation,
            "is_complete": is_complete,
            "next_question": next_question,
            "overall_scores": {
                "technical": interview.technical_score,
                "communication": interview.communication_score,
                "overall": interview.overall_score
            } if is_complete else None,
            "final_feedback": interview.feedback if is_complete else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting answer: {str(e)}")

@app.get("/interview/{interview_id}/status")
async def get_interview_status(interview_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get interview status and progress"""
    try:
        interview_result = await db.execute(select(Interview).where(Interview.id == interview_id))
        interview = interview_result.scalar_one_or_none()
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        current_answers = len(interview.answers) if interview.answers else 0
        total_questions = len(interview.questions)
        
        return {
            "interview_id": interview_id,
            "status": interview.status.value,
            "current_question": current_answers,
            "total_questions": total_questions,
            "progress_percentage": (current_answers / total_questions) * 100 if total_questions > 0 else 0,
            "scores": {
                "technical": interview.technical_score,
                "communication": interview.communication_score,
                "overall": interview.overall_score
            },
            "is_complete": interview.status == InterviewStatus.COMPLETED
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving interview status: {str(e)}")

@app.get("/interview/{interview_id}/results")
async def get_interview_results(interview_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get detailed interview results and feedback"""
    try:
        interview_result = await db.execute(select(Interview).where(Interview.id == interview_id))
        interview = interview_result.scalar_one_or_none()
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        if interview.status != InterviewStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Interview not completed yet")
        
        # Get QA pairs
        qa_pairs_result = await db.execute(
            select(QAPair).where(QAPair.interview_id == interview_id)
        )
        qa_pairs = qa_pairs_result.scalars().all()
        
        return {
            "interview_id": interview_id,
            "scores": {
                "technical": interview.technical_score,
                "communication": interview.communication_score,
                "overall": interview.overall_score
            },
            "feedback": interview.feedback,
            "qa_pairs": [
                {
                    "question": qa.question_text,
                    "answer": qa.answer_text,
                    "question_type": qa.question_type,
                    "scores": {
                        "technical": qa.technical_score,
                        "communication": qa.communication_score,
                        "relevance": qa.relevance_score,
                        "overall": qa.overall_score
                    },
                    "feedback": qa.feedback,
                    "strengths": qa.strengths,
                    "weaknesses": qa.weaknesses,
                    "suggestions": qa.suggestions
                }
                for qa in qa_pairs
            ],
            "completed_at": interview.completed_at.isoformat() if interview.completed_at else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving interview results: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
