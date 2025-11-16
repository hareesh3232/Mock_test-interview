"""
Basic FastAPI server for Mock Interview System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="🎤 Mock Interview System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Mock Interview System API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/docs", "/health", "/resume/upload", "/jobs/search"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "server": "basic"}

@app.get("/jobs/search")
def search_jobs(skills: str = "Python", location: str = "us", count: int = 10):
    print(f"🔍 Job search: skills={skills}, location={location}, count={count}")

    # More comprehensive job data
    all_jobs = [
        {
            "id": "1",
            "title": "Senior Python Developer",
            "company": "TechCorp Inc",
            "description": "Looking for experienced Python developer with FastAPI and PostgreSQL experience",
            "skills_required": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "location": location,
            "match_score": 95.5,
            "salary": "$120,000 - $150,000",
            "type": "Full-time"
        },
        {
            "id": "2",
            "title": "Full Stack Developer",
            "company": "WebCorp",
            "description": "Full stack developer with React and Node.js experience",
            "skills_required": ["JavaScript", "React", "Node.js", "AWS"],
            "location": "Remote",
            "match_score": 88.3,
            "salary": "$100,000 - $130,000",
            "type": "Full-time"
        },
        {
            "id": "3",
            "title": "DevOps Engineer",
            "company": "CloudTech",
            "description": "DevOps engineer with Docker and AWS experience",
            "skills_required": ["Docker", "AWS", "Kubernetes", "Python"],
            "location": "San Francisco, CA",
            "match_score": 82.1,
            "salary": "$110,000 - $140,000",
            "type": "Full-time"
        },
        {
            "id": "4",
            "title": "Machine Learning Engineer",
            "company": "AITech",
            "description": "ML engineer with Python and machine learning experience",
            "skills_required": ["Python", "Machine Learning", "TensorFlow", "SQL"],
            "location": "New York, NY",
            "match_score": 90.7,
            "salary": "$130,000 - $160,000",
            "type": "Full-time"
        },
        {
            "id": "5",
            "title": "API Developer",
            "company": "DataFlow",
            "description": "API developer with FastAPI and PostgreSQL experience",
            "skills_required": ["Python", "FastAPI", "PostgreSQL", "Git"],
            "location": "Austin, TX",
            "match_score": 87.4,
            "salary": "$95,000 - $125,000",
            "type": "Full-time"
        }
    ]

    # Filter jobs based on skills
    skill_list = [s.strip().lower() for s in skills.split(",")]
    matching_jobs = []

    for job in all_jobs:
        job_skills = [s.lower() for s in job["skills_required"]]
        # Calculate match score based on skill overlap
        matches = sum(1 for skill in skill_list if any(skill in js for js in job_skills))
        if matches > 0:
            job_copy = job.copy()
            job_copy["match_score"] = round((matches / len(job_skills)) * 100, 1)
            matching_jobs.append(job_copy)

    # Sort by match score
    matching_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    print(f"📊 Found {len(matching_jobs)} matching jobs out of {len(all_jobs)} total jobs")

    return {
        "jobs": matching_jobs[:count],
        "total": len(matching_jobs),
        "search_skills": skill_list,
        "debug": f"Server processed {len(matching_jobs)} matching jobs"
    }

@app.post("/resume/upload")
def upload_resume():
    return {
        "message": "Resume uploaded successfully",
        "resume_id": "abc123",
        "skills": ["Python", "JavaScript", "SQL", "Docker", "AWS"],
        "experience_years": 3,
        "education_level": "Bachelor's"
    }

if __name__ == "__main__":
    print("🎤 Starting Mock Interview System...")
    print("🔗 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("✋ Press Ctrl+C to stop")

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
