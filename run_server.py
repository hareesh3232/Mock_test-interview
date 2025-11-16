"""
Simple server runner for Mock Interview System
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
from datetime import datetime
from typing import Optional

# Create FastAPI app
app = FastAPI(
    title="🎤 Mock Interview AI System",
    version="1.0.0",
    description="Complete AI-powered interview practice platform"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
data_store = {
    "resumes": {},
    "jobs": [
        {
            "id": "1",
            "title": "Senior Python Developer",
            "company": "TechCorp Inc",
            "description": "Looking for experienced Python developer with FastAPI knowledge.",
            "skills_required": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "location": "San Francisco, CA",
            "remote_work": True,
            "salary_min": 120000,
            "salary_max": 180000
        },
        {
            "id": "2",
            "title": "Full Stack Developer", 
            "company": "StartupXYZ",
            "description": "Join our team building modern web applications with React and Node.js.",
            "skills_required": ["JavaScript", "React", "Node.js", "MongoDB"],
            "location": "New York, NY",
            "remote_work": False,
            "salary_min": 90000,
            "salary_max": 130000
        },
        {
            "id": "3",
            "title": "AI/ML Engineer",
            "company": "DataTech Solutions", 
            "description": "Build and deploy machine learning models at scale.",
            "skills_required": ["Python", "TensorFlow", "PyTorch", "AWS", "Docker"],
            "location": "Austin, TX",
            "remote_work": True,
            "salary_min": 140000,
            "salary_max": 200000
        }
    ],
    "interviews": {},
    "results": {}
}

@app.get("/")
async def root():
    return {
        "message": "🎤 Mock Interview AI System API",
        "version": "1.0.0", 
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "upload": "/resume/upload",
            "jobs": "/jobs/search",
            "interview": "/interview/start"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "total_resumes": len(data_store["resumes"]),
        "total_jobs": len(data_store["jobs"]),
        "total_interviews": len(data_store["interviews"])
    }

@app.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user_name: Optional[str] = Form(None),
    user_email: Optional[str] = Form(None)
):
    """Upload and analyze resume"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    resume_id = str(uuid.uuid4())
    
    # Mock skills extraction
    mock_skills = [
        "Python", "JavaScript", "React", "FastAPI", "PostgreSQL",
        "Docker", "AWS", "Git", "Machine Learning", "API Development"
    ]
    
    resume_data = {
        "id": resume_id,
        "filename": file.filename,
        "user_name": user_name or "John Doe",
        "user_email": user_email or "john.doe@example.com", 
        "skills": mock_skills,
        "experience_years": 3,
        "education_level": "Bachelor's",
        "uploaded_at": datetime.now().isoformat()
    }
    
    data_store["resumes"][resume_id] = resume_data
    
    return {
        "resume_id": resume_id,
        "message": "Resume uploaded and analyzed successfully!",
        "skills": mock_skills,
        "experience_years": 3,
        "education_level": "Bachelor's"
    }

@app.get("/jobs/search")
async def search_jobs(skills: str = "Python", location: str = "us", count: int = 10):
    """Search for relevant jobs"""
    skill_list = [s.strip().lower() for s in skills.split(",")]
    
    matching_jobs = []
    for job in data_store["jobs"]:
        job_skills = [s.lower() for s in job["skills_required"]]
        
        # Simple matching
        matches = sum(1 for skill in skill_list if any(skill in js for js in job_skills))
        if matches > 0:
            job_copy = job.copy()
            job_copy["match_score"] = round((matches / len(job_skills)) * 100, 1)
            matching_jobs.append(job_copy)
    
    matching_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "jobs": matching_jobs[:count],
        "total_found": len(matching_jobs),
        "search_skills": skill_list
    }

@app.post("/interview/generate")
async def generate_questions(resume_id: str = Form(...), job_id: str = Form(...)):
    """Generate interview questions"""
    
    questions = [
        {
            "question": "Tell me about your experience with Python and how you've used it in previous projects.",
            "type": "technical",
            "difficulty": "medium"
        },
        {
            "question": "Describe a challenging project you worked on and how you overcame the difficulties.",
            "type": "behavioral", 
            "difficulty": "medium"
        },
        {
            "question": "How would you design a scalable API using FastAPI?",
            "type": "technical",
            "difficulty": "hard"
        },
        {
            "question": "Where do you see yourself in 5 years?",
            "type": "behavioral",
            "difficulty": "easy"
        },
        {
            "question": "Explain the difference between SQL and NoSQL databases.",
            "type": "technical", 
            "difficulty": "medium"
        }
    ]
    
    return {
        "questions": questions,
        "total_questions": len(questions),
        "generated_at": datetime.now().isoformat()
    }

@app.post("/interview/start")
async def start_interview(resume_id: str = Form(...), job_id: str = Form(...)):
    """Start interview session"""
    interview_id = str(uuid.uuid4())
    
    interview_data = {
        "id": interview_id,
        "resume_id": resume_id,
        "job_id": job_id,
        "status": "in_progress",
        "started_at": datetime.now().isoformat(),
        "current_question": 0,
        "answers": []
    }
    
    data_store["interviews"][interview_id] = interview_data
    
    return {
        "interview_id": interview_id,
        "message": "Interview started successfully!",
        "status": "in_progress"
    }

@app.post("/interview/submit")
async def submit_answer(
    interview_id: str = Form(...),
    question_index: int = Form(...),
    answer: str = Form(...)
):
    """Submit interview answer"""
    
    if interview_id not in data_store["interviews"]:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview = data_store["interviews"][interview_id]
    
    interview["answers"].append({
        "question_index": question_index,
        "answer": answer,
        "answered_at": datetime.now().isoformat()
    })
    
    # Check if interview is complete (5 questions)
    if len(interview["answers"]) >= 5:
        interview["status"] = "completed"
        interview["completed_at"] = datetime.now().isoformat()
        
        # Generate mock scores
        result_id = str(uuid.uuid4())
        results = {
            "id": result_id,
            "interview_id": interview_id,
            "scores": {
                "technical": 78.5,
                "communication": 82.0,
                "job_match": 75.5,
                "overall": 78.7
            },
            "feedback": {
                "strengths": [
                    "Clear communication",
                    "Good technical knowledge", 
                    "Relevant experience"
                ],
                "improvements": [
                    "Provide more specific examples",
                    "Ask clarifying questions",
                    "Show more enthusiasm"
                ]
            },
            "created_at": datetime.now().isoformat()
        }
        
        data_store["results"][result_id] = results
        
        return {
            "message": "Interview completed!",
            "is_complete": True,
            "results": results
        }
    
    return {
        "message": "Answer submitted successfully",
        "is_complete": False,
        "next_question": len(interview["answers"])
    }

@app.get("/interview/{interview_id}/results")
async def get_results(interview_id: str):
    """Get interview results"""
    
    for result in data_store["results"].values():
        if result["interview_id"] == interview_id:
            return result
    
    raise HTTPException(status_code=404, detail="Results not found")

if __name__ == "__main__":
    print("🎤 Starting Mock Interview AI System...")
    print("=" * 50)
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )








