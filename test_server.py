"""
Minimal server for testing
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Mock Interview API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy", "server": "test"}

@app.post("/resume/upload")
def upload_resume():
    return {"message": "Resume uploaded", "skills": ["Python", "JavaScript"]}

@app.get("/jobs/search")
def search_jobs(skills: str = "Python"):
    return {
        "jobs": [
            {
                "id": "1",
                "title": "Python Developer",
                "company": "TechCorp",
                "skills_required": ["Python", "FastAPI"],
                "location": "Remote"
            }
        ],
        "total": 1,
        "search_skills": skills.split(",")
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting test server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")








