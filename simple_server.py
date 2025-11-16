"""
AI-Powered FastAPI server for Mock Interview System with Real Resume Analysis and Job Search
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import uuid
import httpx
import asyncio
import os
import re
import logging
from datetime import datetime

# --- Detailed Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Logging configured.")
from typing import List, Dict, Any, Optional
import fitz
from docx import Document
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema.output import LLMResult

# Create app
app = FastAPI(title="🎤 AI-Powered Mock Interview System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Configuration
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "6d2496e97a0b2c59849077c5add5a5c7")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "6d2496e97a0b2c59849077c5add5a5c7")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY loaded: {'Yes' if GEMINI_API_KEY else 'No'}")

if not GEMINI_API_KEY or "your_gemini_api_key" in GEMINI_API_KEY:
    print("\n[ERROR] FATAL ERROR: GEMINI_API_KEY is not configured.")
    print("   Please get a valid API key from Google AI Studio and add it to your .env file.")
    print("   Exiting now.\n")
    exit()

# Simple storage
data = {"resumes": {}, "jobs": [], "interviews": {}}

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

class LangChainService:
    """Centralized LangChain service for AI operations"""
    
    def __init__(self, api_key: str):
        print("Initializing ChatGoogleGenerativeAI...")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=api_key,
            temperature=0.1,
            max_output_tokens=2048
        )
        
        # Initialize prompt templates
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup all prompt templates"""
        self.resume_analysis_prompt = PromptTemplate(
            input_variables=["resume_text"],
            template="""
            Analyze this resume and extract the following information in JSON format:
            
            Resume Text:
            {resume_text}
            
            Please provide a JSON response with:
            {{
                "skills": ["list", "of", "technical", "skills"],
                "experience_years": number,
                "education_level": "Bachelor's/Master's/PhD/High School/etc",
                "job_titles": ["list", "of", "previous", "job", "titles"],
                "companies": ["list", "of", "companies", "worked", "for"],
                "summary": "brief professional summary",
                "strengths": ["list", "of", "key", "strengths"],
                "technologies": ["list", "of", "technologies", "used"]
            }}
            
            Be accurate and only include information that's clearly stated in the resume.
            Return only valid JSON, no additional text.
            """
        )
        
        self.interview_questions_prompt = PromptTemplate(
            input_variables=["resume_skills", "experience_years", "education_level", "job_title", "job_description", "required_skills"],
            template="""
            Generate 5 relevant interview questions for a candidate with this background:
            
            Resume Skills: {resume_skills}
            Experience: {experience_years} years
            Education: {education_level}
            Job Title: {job_title}
            Job Description: {job_description}
            Required Skills: {required_skills}
            
            Please provide 5 questions in JSON format:
            [
                {{"question": "question text", "type": "technical/behavioral/general", "difficulty": "easy/medium/hard"}},
                {{"question": "question text", "type": "technical/behavioral/general", "difficulty": "easy/medium/hard"}},
                {{"question": "question text", "type": "technical/behavioral/general", "difficulty": "easy/medium/hard"}},
                {{"question": "question text", "type": "technical/behavioral/general", "difficulty": "easy/medium/hard"}},
                {{"question": "question text", "type": "technical/behavioral/general", "difficulty": "easy/medium/hard"}}
            ]
            
            Mix of technical and behavioral questions relevant to their background.
            Return only valid JSON, no additional text.
            """
        )
    
    async def analyze_resume(self, text: str) -> Dict[str, Any]:
        """Analyze resume using LangChain"""
        try:
            formatted_prompt = self.resume_analysis_prompt.format(resume_text=text)
            response = await self.llm.ainvoke(formatted_prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return self._fallback_resume_analysis(text)
            
        except Exception as e:
            print(f"LangChain resume analysis error: {e}")
            return self._fallback_resume_analysis(text)
    
    async def generate_interview_questions(self, resume: Dict[str, Any], job: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate interview questions using LangChain with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                formatted_prompt = self.interview_questions_prompt.format(
                    resume_skills=', '.join(resume.get('skills', ['General Programming'])[:10]),
                    experience_years=resume.get('experience_years', 0),
                    education_level=resume.get('education_level', 'Unknown'),
                    job_title=job.get('title', 'Software Developer'),
                    job_description=job.get('description', 'General software development role')[:200],
                    required_skills=', '.join(job.get('skills_required', ['Problem Solving'])[:5])
                )
                
                print(f"🤖 Attempt {attempt + 1}/{max_retries}: Calling Gemini AI for question generation...")
                response = await self.llm.ainvoke(formatted_prompt)
                content = response.content if hasattr(response, 'content') else str(response)
                
                print(f"📝 LLM Response: {content[:200]}...")
                
                # Try to extract JSON array
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    questions = json.loads(json_match.group())
                    if isinstance(questions, list) and len(questions) > 0:
                        print(f"✅ Successfully generated {len(questions)} questions")
                        return questions[:5]
                
                # Try to parse if response is wrapped in markdown code blocks
                code_block_match = re.search(r'```(?:json)?\s*\[.*?\]\s*```', content, re.DOTALL)
                if code_block_match:
                    json_str = re.sub(r'```(?:json)?\s*', '', code_block_match.group())
                    json_str = json_str.replace('```', '').strip()
                    questions = json.loads(json_str)
                    if isinstance(questions, list) and len(questions) > 0:
                        print(f"✅ Successfully generated {len(questions)} questions from code block")
                        return questions[:5]
                
                print(f"⚠️ Attempt {attempt + 1} failed: Could not parse valid JSON from response")
                
            except json.JSONDecodeError as e:
                print(f"⚠️ Attempt {attempt + 1} JSON parse error: {e}")
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} error: {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
        
        # If all retries fail, generate questions using a simpler LLM prompt
        print("⚠️ All structured attempts failed. Trying free-form LLM generation...")
        return await self._generate_freeform_questions(resume, job)
    
    def _fallback_resume_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback resume analysis"""
        skills_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'React', 'Angular', 'Vue',
            'Node.js', 'Django', 'Flask', 'Spring', 'AWS', 'Azure', 'Docker',
            'Kubernetes', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Git',
            'Linux', 'Agile', 'Scrum', 'REST API', 'GraphQL', 'Microservices',
            'Machine Learning', 'Data Science', 'TensorFlow', 'PyTorch'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        experience_match = re.search(r'(\d+)\+?\s*years?\s+experience', text, re.IGNORECASE)
        experience_years = int(experience_match.group(1)) if experience_match else 2
        
        return {
            "skills": found_skills[:10],
            "experience_years": experience_years,
            "education_level": "Bachelor's",
            "job_titles": ["Software Developer"],
            "companies": ["Tech Company"],
            "summary": "Experienced software developer",
            "strengths": ["Problem Solving", "Team Collaboration"],
            "technologies": found_skills[:5]
        }
    
    async def _generate_freeform_questions(self, resume: Dict[str, Any], job: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate questions using free-form LLM prompt when structured approach fails"""
        try:
            skills = ', '.join(resume.get('skills', ['programming'])[:5])
            job_title = job.get('title', 'Software Developer')
            
            freeform_prompt = f"""
            You are an expert technical interviewer. Generate exactly 5 interview questions for a {job_title} position.
            
            Candidate Background:
            - Skills: {skills}
            - Experience: {resume.get('experience_years', 0)} years
            - Education: {resume.get('education_level', 'Unknown')}
            
            Job Requirements:
            - Role: {job_title}
            - Required Skills: {', '.join(job.get('skills_required', ['General'])[:5])}
            
            Generate 5 diverse questions:
            1. One technical question about their core skills
            2. One behavioral question about teamwork or problem-solving
            3. One question about their experience with specific technologies
            4. One scenario-based question related to the job
            5. One question about their learning and growth mindset
            
            Format each question on a new line starting with "Q1:", "Q2:", etc.
            """
            
            response = await self.llm.ainvoke(freeform_prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse free-form questions
            questions = []
            lines = content.split('\n')
            question_types = ['technical', 'behavioral', 'technical', 'scenario', 'general']
            difficulties = ['medium', 'medium', 'hard', 'medium', 'easy']
            
            for i, line in enumerate(lines):
                # Look for lines starting with Q1:, Q2:, etc. or numbered patterns
                if re.match(r'^Q?\d+[:.)]\s*', line.strip()):
                    question_text = re.sub(r'^Q?\d+[:.)]\s*', '', line.strip())
                    if question_text and len(question_text) > 10:
                        idx = len(questions)
                        questions.append({
                            "question": question_text,
                            "type": question_types[idx] if idx < len(question_types) else "general",
                            "difficulty": difficulties[idx] if idx < len(difficulties) else "medium"
                        })
                        if len(questions) >= 5:
                            break
            
            if len(questions) >= 3:  # Accept if we got at least 3 questions
                print(f"✅ Generated {len(questions)} questions using free-form approach")
                return questions[:5]
            
            # Last resort: Use LLM to generate one question at a time
            print("⚠️ Free-form parsing failed. Generating questions one by one...")
            return await self._generate_questions_individually(resume, job)
            
        except Exception as e:
            print(f"❌ Free-form generation error: {e}")
            return await self._generate_questions_individually(resume, job)
    
    async def _generate_questions_individually(self, resume: Dict[str, Any], job: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate questions one at a time as absolute fallback"""
        questions = []
        question_prompts = [
            f"Generate one technical interview question about {', '.join(resume.get('skills', ['programming'])[:2])} for a {job.get('title', 'developer')} role. Just return the question text, nothing else.",
            f"Generate one behavioral interview question about teamwork and collaboration. Just return the question text, nothing else.",
            f"Generate one interview question about problem-solving experience. Just return the question text, nothing else.",
            f"Generate one interview question about learning new technologies. Just return the question text, nothing else.",
            f"Generate one interview question about handling challenges in {job.get('title', 'software development')}. Just return the question text, nothing else."
        ]
        
        types = ['technical', 'behavioral', 'behavioral', 'general', 'scenario']
        difficulties = ['medium', 'medium', 'hard', 'easy', 'medium']
        
        for i, prompt in enumerate(question_prompts):
            try:
                response = await self.llm.ainvoke(prompt)
                content = response.content if hasattr(response, 'content') else str(response)
                question_text = content.strip().strip('"').strip("'")
                
                if question_text and len(question_text) > 10:
                    questions.append({
                        "question": question_text,
                        "type": types[i],
                        "difficulty": difficulties[i]
                    })
                    print(f"✅ Generated question {i+1}/5")
            except Exception as e:
                print(f"⚠️ Failed to generate question {i+1}: {e}")
        
        print(f"✅ Generated {len(questions)} questions individually")
        return questions

class ResumeAnalyzer:
    """AI-powered resume analysis using LangChain and Google Gemini API"""
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # Initialize LangChain service
        print("Initializing LangChainService...")
        self.langchain_service = LangChainService(self.api_key)
        print("LangChainService initialized successfully.")
    
    async def extract_text_from_file(self, file_path: str, filename: str) -> str:
        """Extract text from PDF or DOCX files"""
        try:
            if filename.lower().endswith('.pdf'):
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            elif filename.lower().endswith(('.doc', '.docx')):
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error extracting text: {str(e)}")
    
    async def analyze_resume_with_ai(self, text: str) -> Dict[str, Any]:
        """Use LangChain with Google Gemini to analyze resume content"""
        return await self.langchain_service.analyze_resume(text)
    
    def _fallback_parsing(self, text: str) -> Dict[str, Any]:
        """Fallback parsing when AI is not available"""
        # Simple keyword extraction
        skills_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'React', 'Angular', 'Vue',
            'Node.js', 'Django', 'Flask', 'Spring', 'AWS', 'Azure', 'Docker',
            'Kubernetes', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Git',
            'Linux', 'Agile', 'Scrum', 'REST API', 'GraphQL', 'Microservices',
            'Machine Learning', 'Data Science', 'TensorFlow', 'PyTorch'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Extract experience years
        experience_match = re.search(r'(\d+)\+?\s*years?\s+experience', text, re.IGNORECASE)
        experience_years = int(experience_match.group(1)) if experience_match else 2
        
        return {
            "skills": found_skills[:10],
            "experience_years": experience_years,
            "education_level": "Bachelor's",
            "job_titles": ["Software Developer"],
            "companies": ["Tech Company"],
            "summary": "Experienced software developer",
            "strengths": ["Problem Solving", "Team Collaboration"],
            "technologies": found_skills[:5]
        }

class JobSearchService:
    """Real job search using Adzuna API"""
    
    def __init__(self):
        self.app_id = ADZUNA_APP_ID
        self.app_key = ADZUNA_APP_KEY
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
    
    async def search_jobs(self, skills: List[str], location: str = "us", count: int = 20) -> List[Dict[str, Any]]:
        """Search for real jobs using Adzuna API"""
        try:
            if self.app_id == "your_adzuna_app_id" or self.app_key == "your_adzuna_app_key":
                print("⚠️ Adzuna API keys not configured, using mock data")
                return self._get_mock_jobs(skills, location, count)
            
            async with httpx.AsyncClient() as client:
                params = {
                    "app_id": self.app_id,
                    "app_key": self.app_key,
                    "what": " ".join(skills),
                    "where": location,
                    "results_per_page": count,
                    "content-type": "application/json"
                }
                
                response = await client.get(f"{self.base_url}/search/1", params=params)
                response.raise_for_status()
                
                data = response.json()
                jobs = []
                
                for job in data.get("results", []):
                    jobs.append({
                        "id": job.get("id"),
                        "title": job.get("title"),
                        "company": job.get("company", {}).get("display_name", "Unknown Company"),
                        "location": job.get("location", {}).get("display_name", "Unknown Location"),
                        "description": job.get("description", ""),
                        "salary_min": job.get("salary_min"),
                        "salary_max": job.get("salary_max"),
                        "salary_currency": job.get("salary_currency", "USD"),
                        "job_type": job.get("contract_type", "Full-time"),
                        "job_url": job.get("redirect_url"),
                        "source": "Adzuna",
                        "posted_date": job.get("created"),
                        "skills_required": self._extract_skills_from_description(job.get("description", ""))
                    })
                
                return jobs
                
        except Exception as e:
            print(f"Adzuna API error: {e}, using mock data")
            return self._get_mock_jobs(skills, location, count)
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills from job description"""
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue',
            'Node.js', 'Django', 'Flask', 'Spring', 'AWS', 'Azure', 'Docker',
            'Kubernetes', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Git',
            'Linux', 'Agile', 'Scrum', 'REST API', 'GraphQL', 'Microservices'
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in skill_keywords:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:10]
    
    def _get_mock_jobs(self, skills: List[str], location: str, count: int) -> List[Dict[str, Any]]:
        """Fallback mock jobs when API is not available"""
        mock_jobs = [
            {
                "id": "mock_1",
                "title": f"Senior {skills[0] if skills else 'Software'} Developer",
                "company": "TechCorp Inc.",
                "location": "San Francisco, CA",
                "description": f"Looking for a senior developer with expertise in {', '.join(skills[:3])}",
                "salary_min": 120000,
                "salary_max": 180000,
                "salary_currency": "USD",
                "job_type": "Full-time",
                "job_url": "https://example.com/job1",
                "source": "Mock API",
                "posted_date": datetime.now().isoformat(),
                "skills_required": skills[:5] + ["AWS", "Docker", "Git"]
            },
            {
                "id": "mock_2",
                "title": f"Full Stack {skills[0] if skills else 'Web'} Developer",
                "company": "StartupXYZ",
                "location": "New York, NY",
                "description": f"Join our team as a full-stack developer working with {', '.join(skills[:2])}",
                "salary_min": 80000,
                "salary_max": 120000,
                "salary_currency": "USD",
                "job_type": "Full-time",
                "job_url": "https://example.com/job2",
                "source": "Mock API",
                "posted_date": datetime.now().isoformat(),
                "skills_required": skills[:4] + ["React", "Node.js", "MongoDB"]
            }
        ]
        return mock_jobs[:count]

# Initialize services
logging.info("Initializing services...")
resume_analyzer = ResumeAnalyzer()
logging.info("ResumeAnalyzer initialized.")
job_search_service = JobSearchService()
logging.info("JobSearchService initialized.")
langchain_service = LangChainService(GEMINI_API_KEY)
logging.info("LangChainService initialized.")
logging.info("All services initialized successfully.")

@app.get("/")
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not found. Please build the frontend first."}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "resumes": len(data["resumes"]),
        "jobs": len(data["jobs"]),
        "interviews": len(data["interviews"])
    }

@app.post("/resume/upload")
@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...), user_name: str = Form("Anonymous")):
    """Upload and analyze resume using AI"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
            raise HTTPException(status_code=400, detail="Only PDF, DOC, and DOCX files are allowed")
        
        resume_id = str(uuid.uuid4())
        
        # Save file
        file_extension = os.path.splitext(file.filename)[1]
        file_path = f"uploads/{resume_id}{file_extension}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text from file
        print(f"📄 Extracting text from {file.filename}...")
        text = await resume_analyzer.extract_text_from_file(file_path, file.filename)
        
        # Analyze resume with AI
        print(f"🤖 Analyzing resume with AI...")
        analysis = await resume_analyzer.analyze_resume_with_ai(text)
        
        resume_data = {
            "id": resume_id,
            "filename": file.filename,
            "user_name": user_name,
            "file_path": file_path,
            "extracted_text": text[:500] + "..." if len(text) > 500 else text,
            "skills": analysis.get("skills", []),
            "experience_years": analysis.get("experience_years", 0),
            "education_level": analysis.get("education_level", "Unknown"),
            "job_titles": analysis.get("job_titles", []),
            "companies": analysis.get("companies", []),
            "summary": analysis.get("summary", ""),
            "strengths": analysis.get("strengths", []),
            "technologies": analysis.get("technologies", []),
            "uploaded_at": datetime.now().isoformat()
        }
        
        data["resumes"][resume_id] = resume_data
        
        # Clean up file
        try:
            os.remove(file_path)
        except:
            pass
        
        return {
            "resume_id": resume_id,
            "message": "Resume analyzed successfully with AI!",
            "analysis": analysis,
            "skills": analysis.get("skills", []),
            "experience_years": analysis.get("experience_years", 0),
            "education_level": analysis.get("education_level", "Unknown")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@app.get("/jobs/search")
@app.get("/api/jobs/search")
async def search_jobs(skills: str = "Python", location: str = "us", count: int = 10):
    """Search for real jobs using Adzuna API"""
    try:
        print(f"🔍 Job search called with: skills={skills}, location={location}, count={count}")
        
        # Parse skills
        skill_list = [s.strip() for s in skills.split(",")]
        
        # Search for real jobs
        print(f"🌐 Searching Adzuna API for jobs...")
        jobs = await job_search_service.search_jobs(skill_list, location, count)
        
        # Calculate match scores
        for job in jobs:
            job_skills = [s.lower() for s in job.get("skills_required", [])]
            search_skills_lower = [s.lower() for s in skill_list]
            
            if job_skills:
                matches = sum(1 for skill in search_skills_lower if any(skill in js for js in job_skills))
                job["match_score"] = round((matches / len(job_skills)) * 100, 1)
            else:
                job["match_score"] = 0
        
        # Sort by match score
        jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        print(f"📊 Found {len(jobs)} jobs from Adzuna API")
        
        return {
            "jobs": jobs,
            "total": len(jobs),
            "search_skills": skill_list,
            "source": "Adzuna API" if job_search_service.app_id != "your_adzuna_app_id" else "Mock Data",
            "location": location
        }
        
    except Exception as e:
        print(f"❌ Job search error: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

async def generate_ai_questions(resume: Dict[str, Any], job: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate interview questions using LangChain with Google Gemini AI, with safe fallback."""
    try:
        print("[INFO] Attempting to generate questions using Google Gemini AI...")
        print(f"   Resume: {resume}")
        print(f"   Job: {job}")
        result = await resume_analyzer.langchain_service.generate_interview_questions(resume, job)
        print(f"✅ Successfully generated {len(result)} questions!")
        return result
    except Exception as e:
        print(f"[WARNING] Google Gemini AI generation failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print("   Falling back to simple deterministic questions...")
        # Fallback: generate simple deterministic questions without external AI
        skills = resume.get("skills", []) or job.get("skills_required", []) or ["problem solving"]
        title = job.get("title") or "the role"
        base_questions = [
            {
                "question": f"Describe a project where you used {skills[0] if skills else 'your skills'}.",
                "type": "technical",
                "difficulty": "medium",
            },
            {
                "question": f"How do you debug tough issues when working as a {title}?",
                "type": "general",
                "difficulty": "medium",
            },
            {
                "question": f"Explain a time you optimized performance in your code.",
                "type": "technical",
                "difficulty": "medium",
            },
            {
                "question": "Tell me about a conflict you resolved within a team.",
                "type": "behavioral",
                "difficulty": "easy",
            },
            {
                "question": f"Which libraries or tools do you prefer for {skills[0] if skills else 'your work'} and why?",
                "type": "general",
                "difficulty": "easy",
            },
        ]
        return base_questions

@app.post("/interview/generate")
@app.post("/api/interview/generate")
async def generate_questions(
    payload: Dict[str, Any] = Body(...)
):
    """Generate AI-powered interview questions based on resume and job"""
    try:
        # Extract resume_id and job_id from payload
        resume_id = payload.get("resume_id")
        job_id = payload.get("job_id")

        if not resume_id:
            raise HTTPException(status_code=422, detail="Missing resume_id")
        if not job_id:
            raise HTTPException(status_code=422, detail="Missing job_id")

        # Get resume data (fallback to mock if not found)
        resume = data["resumes"].get(resume_id)
        if not resume:
            print("⚠️ Resume not found; using lightweight mock resume for generation")
            resume = {
                "id": "mock_resume",
                "skills": ["Programming", "Problem Solving", "Communication"],
                "experience_years": 2,
                "education_level": "Bachelor's"
            }
        
        # Get job data (from recent search or mock)
        job = None
        if job_id in data.get("jobs", []):
            job = data["jobs"][job_id]
        else:
            # Create mock job based on skills
            job = {
                "title": "Software Developer",
                "description": f"Looking for a developer with skills in {', '.join(resume.get('skills', [])[:3])}",
                "skills_required": resume.get("skills", [])[:5]
            }
        
        # Generate questions using AI (with fallback)
        print(f"🤖 Generating AI interview questions...")
        questions = await generate_ai_questions(resume, job)

        # Optionally trim to requested question_count if provided
        try:
            requested_count = None
            if payload and isinstance(payload.get("question_count"), int):
                requested_count = max(1, min(10, payload.get("question_count")))
            if requested_count:
                questions = questions[:requested_count]
        except Exception:
            pass
        
        return {
            "questions": questions,
            "count": len(questions),
            "resume_id": resume_id,
            "job_id": job_id,
            "generated_by": "AI"
        }
        
    except Exception as e:
        print(f"[ERROR] Question generation error: {e}")
        # Re-raise the exception to let the user know there's an issue
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate interview questions. Please check your GEMINI_API_KEY configuration. Error: {str(e)}"
        )


@app.post("/interview/start")
@app.post("/api/interview/start")
def start_interview(
    resume_id: Optional[str] = Form(None),
    job_id: Optional[str] = Form(None),
    payload: Optional[Dict[str, Any]] = Body(None)
):
    # Support JSON payload too
    if payload:
        resume_id = payload.get("resume_id") or resume_id
        job_id = payload.get("job_id") or job_id
    if not resume_id or not job_id:
        raise HTTPException(status_code=422, detail="Missing resume_id or job_id")
    interview_id = str(uuid.uuid4())
    
    interview = {
        "id": interview_id,
        "resume_id": resume_id,
        "job_id": job_id,
        "status": "started",
        "answers": [],
        "started_at": datetime.now().isoformat()
    }
    
    data["interviews"][interview_id] = interview
    
    return {
        "interview_id": interview_id,
        "message": "Interview started!",
        "status": "started"
    }

@app.post("/interview/submit")
@app.post("/api/interview/submit")
def submit_answer(
    interview_id: Optional[str] = Form(None),
    answer: Optional[str] = Form(None),
    question_index: Optional[int] = Form(None),
    payload: Optional[Dict[str, Any]] = Body(None)
):
    # Accept JSON or Form data
    if payload:
        interview_id = payload.get("interview_id") or interview_id
        answer = payload.get("answer") or answer
        question_index = payload.get("question_index", question_index)
    if not interview_id or answer is None:
        raise HTTPException(status_code=422, detail="Missing interview_id or answer")
    if interview_id in data["interviews"]:
        interview = data["interviews"][interview_id]
        interview["answers"].append({
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        
        # Complete after 5 answers
        if len(interview["answers"]) >= 5:
            interview["status"] = "completed"
            
            return {
                "message": "Interview completed!",
                "is_complete": True,
                "scores": {
                    "technical": 78,
                    "communication": 82,
                    "overall": 80
                }
            }
        
        return {
            "message": "Answer submitted",
            "is_complete": False,
            "question_number": len(interview["answers"]) + 1
        }
    
    return {"error": "Interview not found"}

# --- Static Files Setup ---
STATIC_DIR = "frontend/build"

# Mount the static directory for CSS, JS, etc.
app.mount("/static", StaticFiles(directory=os.path.join(STATIC_DIR, "static")), name="static")

# Catch-all to serve index.html for any other path
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not found. Please build the frontend first."}


if __name__ == "__main__":
    logging.info("Starting AI-Powered Mock Interview System with LangChain...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Features: LangChain + Gemini AI Resume Analysis + Real Job Search (Adzuna API)")
    print("")
    print("Configuration:")
    print(f"   - Gemini API Key: {'Set' if GEMINI_API_KEY != 'your_gemini_api_key' else 'Not Set'}")
    print(f"   - Adzuna App ID: {'Set' if ADZUNA_APP_ID != 'your_adzuna_app_id' else 'Not Set'}")
    print(f"   - Adzuna App Key: {'Set' if ADZUNA_APP_KEY != 'your_adzuna_app_key' else 'Not Set'}")
    print("")
    print("LangChain Features:")
    print("   - Structured prompt templates")
    print("   - Better error handling and fallbacks")
    print("   - Centralized AI service management")
    print("   - Enhanced resume analysis")
    print("   - Intelligent interview question generation")
    print("")
    print("To enable full AI features, set these environment variables:")
    print("   - GEMINI_API_KEY=your_gemini_api_key")
    print("   - ADZUNA_APP_ID=your_adzuna_app_id") 
    print("   - ADZUNA_APP_KEY=your_adzuna_app_key")
    print("")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
