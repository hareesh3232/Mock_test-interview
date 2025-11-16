"""
Simple FastAPI application for Mock Interview System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
import json
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Mock Interview AI System",
    version="1.0.0",
    description="AI-powered resume-based job-matched mock interview system"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (for demo purposes)
users_db = {}
resumes_db = {}
jobs_db = {}
interviews_db = {}
results_db = {}

# Pydantic models
class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: str

class JobSearch(BaseModel):
    skills: str
    location: str = "us"
    count: int = 10

class InterviewQuestion(BaseModel):
    question: str
    type: str = "technical"
    difficulty: str = "medium"

class InterviewStart(BaseModel):
    resume_id: str
    job_id: str
    questions: List[InterviewQuestion]

class AnswerSubmit(BaseModel):
    interview_id: str
    question_index: int
    answer: str

# Mock job data
MOCK_JOBS = [
    {
        "id": "job_1",
        "title": "Senior Python Developer",
        "company": "TechCorp Inc",
        "description": "Looking for an experienced Python developer with FastAPI, Django, and cloud experience.",
        "skills_required": ["Python", "FastAPI", "Django", "AWS", "PostgreSQL"],
        "location": "San Francisco, CA",
        "remote_work": True,
        "salary_min": 120000,
        "salary_max": 180000,
        "experience_level": "Senior"
    },
    {
        "id": "job_2", 
        "title": "Full Stack Developer",
        "company": "StartupXYZ",
        "description": "Join our team to build cutting-edge web applications using React and Node.js.",
        "skills_required": ["JavaScript", "React", "Node.js", "MongoDB", "TypeScript"],
        "location": "New York, NY",
        "remote_work": False,
        "salary_min": 90000,
        "salary_max": 130000,
        "experience_level": "Mid-level"
    },
    {
        "id": "job_3",
        "title": "AI/ML Engineer", 
        "company": "DataTech Solutions",
        "description": "Build and deploy machine learning models for production applications.",
        "skills_required": ["Python", "TensorFlow", "PyTorch", "Kubernetes", "Docker"],
        "location": "Austin, TX",
        "remote_work": True,
        "salary_min": 140000,
        "salary_max": 200000,
        "experience_level": "Senior"
    },
    {
        "id": "job_4",
        "title": "Frontend Developer",
        "company": "DesignHub",
        "description": "Create beautiful and responsive user interfaces using modern frameworks.",
        "skills_required": ["React", "Vue.js", "TypeScript", "CSS", "HTML"],
        "location": "Los Angeles, CA", 
        "remote_work": True,
        "salary_min": 80000,
        "salary_max": 120000,
        "experience_level": "Mid-level"
    },
    {
        "id": "job_5",
        "title": "DevOps Engineer",
        "company": "CloudFirst",
        "description": "Manage infrastructure and deployment pipelines for scalable applications.",
        "skills_required": ["AWS", "Docker", "Kubernetes", "Terraform", "Python"],
        "location": "Seattle, WA",
        "remote_work": True,
        "salary_min": 110000,
        "salary_max": 160000,
        "experience_level": "Senior"
    }
]

# Initialize jobs database
for job in MOCK_JOBS:
    jobs_db[job["id"]] = job

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Mock Interview AI System API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0",
        "total_users": len(users_db),
        "total_resumes": len(resumes_db),
        "total_jobs": len(jobs_db),
        "total_interviews": len(interviews_db)
    }

# Auth endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register new user"""
    user_id = str(uuid.uuid4())
    
    # Check if user exists
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    new_user = {
        "id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": datetime.now().isoformat()
    }
    
    users_db[user_id] = new_user
    return UserResponse(**new_user)

@app.post("/auth/login")
async def login(email: str = Form(...), password: str = Form(...)):
    """Login user"""
    for user in users_db.values():
        if user["email"] == email:
            return {
                "access_token": f"mock_token_{user['id']}",
                "token_type": "bearer",
                "user": user
            }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Resume endpoints
@app.post("/api/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user_name: Optional[str] = Form(None),
    user_email: Optional[str] = Form(None)
):
    """Upload and parse resume"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file type
    allowed_types = [".pdf", ".doc", ".docx"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Generate resume ID
    resume_id = str(uuid.uuid4())
    
    # Read file content
    content = await file.read()
    
    # Mock resume parsing (in real app, use PyMuPDF, spaCy, etc.)
    mock_skills = [
        "Python", "JavaScript", "React", "FastAPI", "PostgreSQL", 
        "Docker", "AWS", "Git", "Machine Learning", "Data Analysis"
    ]
    
    mock_experience = [
        {
            "title": "Software Developer",
            "company": "Tech Company",
            "duration_years": 3,
            "description": "Developed web applications using Python and React"
        }
    ]
    
    mock_education = [
        {
            "degree": "Bachelor's in Computer Science",
            "university": "University Name",
            "graduation_year": 2020
        }
    ]
    
    # Store resume data
    resume_data = {
        "id": resume_id,
        "filename": file.filename,
        "file_size": len(content),
        "file_type": file.content_type,
        "user_name": user_name,
        "user_email": user_email,
        "skills": mock_skills,
        "experience": mock_experience,
        "education": mock_education,
        "experience_years": 3,
        "education_level": "Bachelor's",
        "parsing_status": "completed",
        "created_at": datetime.now().isoformat()
    }
    
    resumes_db[resume_id] = resume_data
    
    return {
        "resume_id": resume_id,
        "message": "Resume uploaded and parsed successfully",
        "skills": mock_skills,
        "experience_years": 3,
        "education_level": "Bachelor's"
    }

@app.get("/api/resume/{resume_id}")
async def get_resume(resume_id: str):
    """Get resume details"""
    if resume_id not in resumes_db:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return resumes_db[resume_id]

# Job search endpoints
@app.get("/api/jobs/search")
async def search_jobs(skills: str, location: str = "us", count: int = 10):
    """Search for relevant jobs"""
    # Split skills into list
    skill_list = [s.strip().lower() for s in skills.split(",")]
    
    # Filter jobs based on skills
    matching_jobs = []
    for job in MOCK_JOBS:
        job_skills = [s.lower() for s in job["skills_required"]]
        
        # Calculate match score
        matching_skills = set(skill_list) & set(job_skills)
        match_score = len(matching_skills) / len(job_skills) if job_skills else 0
        
        if match_score > 0:  # Include jobs with any skill match
            job_copy = job.copy()
            job_copy["match_score"] = round(match_score * 100, 1)
            matching_jobs.append(job_copy)
    
    # Sort by match score
    matching_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Limit results
    limited_jobs = matching_jobs[:count]
    
    return {
        "jobs": limited_jobs,
        "total_found": len(matching_jobs),
        "search_terms": skill_list
    }

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job details"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs_db[job_id]

# Interview endpoints
@app.post("/api/interview/generate")
async def generate_questions(resume_id: str = Form(...), job_id: str = Form(...), question_count: int = Form(5)):
    """Generate interview questions"""
    if resume_id not in resumes_db:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    resume = resumes_db[resume_id]
    job = jobs_db[job_id]
    
    # Mock question generation (in real app, use OpenAI)
    mock_questions = [
        {
            "question": f"Tell me about your experience with {', '.join(resume['skills'][:3])} and how it relates to this {job['title']} position.",
            "type": "behavioral",
            "difficulty": "medium",
            "expected_keywords": resume['skills'][:3]
        },
        {
            "question": f"How would you approach building a scalable application using {job['skills_required'][0]}?",
            "type": "technical", 
            "difficulty": "medium",
            "expected_keywords": [job['skills_required'][0], "scalability", "architecture"]
        },
        {
            "question": "Describe a challenging project you worked on and how you overcame the difficulties.",
            "type": "behavioral",
            "difficulty": "medium",
            "expected_keywords": ["project management", "problem solving", "teamwork"]
        },
        {
            "question": f"What's the difference between {job['skills_required'][0]} and {job['skills_required'][1] if len(job['skills_required']) > 1 else 'similar technologies'}?",
            "type": "technical",
            "difficulty": "hard", 
            "expected_keywords": job['skills_required'][:2]
        },
        {
            "question": "Where do you see yourself in 5 years and how does this role fit into your career goals?",
            "type": "behavioral",
            "difficulty": "easy",
            "expected_keywords": ["career goals", "growth", "development"]
        }
    ]
    
    # Limit to requested count
    questions = mock_questions[:question_count]
    
    return {
        "questions": questions,
        "job_title": job['title'],
        "company": job['company'],
        "generated_at": datetime.now().isoformat()
    }

@app.post("/api/interview/start")
async def start_interview(interview_data: InterviewStart):
    """Start interview session"""
    interview_id = str(uuid.uuid4())
    
    # Store interview session
    interview_session = {
        "id": interview_id,
        "resume_id": interview_data.resume_id,
        "job_id": interview_data.job_id,
        "questions": [q.dict() for q in interview_data.questions],
        "answers": [],
        "current_question_index": 0,
        "status": "in_progress",
        "started_at": datetime.now().isoformat()
    }
    
    interviews_db[interview_id] = interview_session
    
    return {
        "interview_id": interview_id,
        "message": "Interview started successfully",
        "total_questions": len(interview_data.questions)
    }

@app.post("/api/interview/submit")
async def submit_answer(answer_data: AnswerSubmit):
    """Submit answer for interview question"""
    if answer_data.interview_id not in interviews_db:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = interviews_db[answer_data.interview_id]
    
    # Add answer
    answer_entry = {
        "question_index": answer_data.question_index,
        "answer": answer_data.answer,
        "answered_at": datetime.now().isoformat()
    }
    
    interview["answers"].append(answer_entry)
    interview["current_question_index"] = answer_data.question_index + 1
    
    # Check if interview is complete
    is_complete = len(interview["answers"]) >= len(interview["questions"])
    
    if is_complete:
        interview["status"] = "completed"
        interview["completed_at"] = datetime.now().isoformat()
        
        # Generate mock results
        result_id = str(uuid.uuid4())
        mock_result = {
            "id": result_id,
            "interview_id": answer_data.interview_id,
            "scores": {
                "technical": round(75 + (hash(answer_data.answer) % 20), 1),
                "communication": round(70 + (hash(answer_data.answer) % 25), 1),
                "job_match": round(80 + (hash(answer_data.answer) % 15), 1),
                "overall": 0
            },
            "feedback": {
                "strengths": [
                    "Clear communication skills",
                    "Good technical knowledge",
                    "Relevant experience"
                ],
                "improvements": [
                    "Provide more specific examples",
                    "Explain thought process in detail",
                    "Ask clarifying questions"
                ],
                "overall": "Good performance overall. Continue practicing to improve confidence and clarity."
            },
            "created_at": datetime.now().isoformat()
        }
        
        # Calculate overall score
        scores = mock_result["scores"]
        scores["overall"] = round((scores["technical"] + scores["communication"] + scores["job_match"]) / 3, 1)
        
        results_db[result_id] = mock_result
        
        return {
            "message": "Interview completed successfully",
            "is_complete": True,
            "result_id": result_id,
            "scores": mock_result["scores"]
        }
    
    return {
        "message": "Answer submitted successfully",
        "is_complete": False,
        "next_question_index": interview["current_question_index"]
    }

@app.get("/api/interview/{interview_id}")
async def get_interview(interview_id: str):
    """Get interview details"""
    if interview_id not in interviews_db:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    return interviews_db[interview_id]

@app.get("/api/interview/{interview_id}/results")
async def get_interview_results(interview_id: str):
    """Get interview results"""
    if interview_id not in interviews_db:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Find result for this interview
    for result in results_db.values():
        if result["interview_id"] == interview_id:
            return result
    
    raise HTTPException(status_code=404, detail="Results not found")

# Dashboard endpoints
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    completed_interviews = len([i for i in interviews_db.values() if i["status"] == "completed"])
    
    return {
        "total_users": len(users_db),
        "total_resumes": len(resumes_db),
        "total_interviews": len(interviews_db),
        "completed_interviews": completed_interviews,
        "average_score": 78.5,  # Mock average
        "top_skills": ["Python", "JavaScript", "React", "AWS", "Docker"]
    }

@app.get("/api/dashboard/history")
async def get_interview_history(user_id: Optional[str] = None):
    """Get interview history"""
    # Return all interviews (in real app, filter by user)
    history = []
    for interview in interviews_db.values():
        if interview["status"] == "completed":
            # Find corresponding result
            result = None
            for r in results_db.values():
                if r["interview_id"] == interview["id"]:
                    result = r
                    break
            
            # Get job info
            job = jobs_db.get(interview["job_id"], {})
            
            history.append({
                "interview_id": interview["id"],
                "job_title": job.get("title", "Unknown"),
                "company": job.get("company", "Unknown"),
                "completed_at": interview.get("completed_at"),
                "overall_score": result["scores"]["overall"] if result else 0
            })
    
    return {"history": history}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)








