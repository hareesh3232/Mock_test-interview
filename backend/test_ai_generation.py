
import asyncio
import os
from dotenv import load_dotenv
import ai_service
from database import AsyncSessionLocal
from models import Resume, Job
from sqlalchemy import select

# Load environment variables
load_dotenv()

async def test_generation():
    print("Testing AI Question Generation...")
    
    # Check API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in .env")
        return
    print(f"GEMINI_API_KEY found: {api_key[:5]}...")

    # Initialize AI Service
    service = ai_service.GeminiService()
    
    # Mock Data
    job_description = "We are looking for a Python Developer with experience in FastAPI and React."
    resume_skills = ["Python", "Django", "JavaScript", "React"]
    job_requirements = ["Strong Python skills", "Experience with REST APIs"]
    job_title = "Senior Python Developer"
    company_name = "Tech Corp"
    
    print("\nCalling generate_interview_questions...")
    try:
        questions = await service.generate_interview_questions(
            job_description=job_description,
            resume_skills=resume_skills,
            job_requirements=job_requirements,
            job_title=job_title,
            company_name=company_name,
            question_count=3
        )
        print("\nSuccess! Generated Questions:")
        import json
        print(json.dumps(questions, indent=2))
        
        if not questions:
            print("\nERROR: Returned empty list!")
            
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generation())
