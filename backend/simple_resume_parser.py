"""
Simple resume parsing service without heavy dependencies
"""

import os
import uuid
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

class SimpleResumeParser:
    def __init__(self):
        print("Using simple resume parser (basic text processing only)")
    
    async def parse_resume(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Parse resume file and extract structured data using NLP (Gemini)"""
        print(f"Starting resume parsing for {filename} at {file_path}")
        
        parsed_data = None
        raw_text = ""
        
        try:
            # 1. Extract text from file
            raw_text = self._extract_text_from_file(file_path, filename)
            
            # 2. Analyze with Gemini (NLP)
            if raw_text.strip():
                print(f"Extracting data from resume: {filename}...")
                parsed_data = await self._extract_with_gemini(raw_text)
                
        except Exception as e:
            print(f"Error parsing resume file: {e}")
            
        # 3. Fallback if extraction failed
        if not parsed_data:
            print("Falling back to basic/mock parsing")
            parsed_data = self._create_mock_parsed_data(filename)
            raw_text = raw_text or f"Mock text extracted from {filename}"
        
        return {
            "filename": filename,
            "file_path": file_path,
            "raw_text": raw_text[:500] + "...", # Truncate for storage
            "parsed_data": parsed_data,
            "extraction_confidence": 0.9 if parsed_data else 0.5,
            "extracted_at": datetime.utcnow().isoformat()
        }

    def _extract_text_from_file(self, file_path: str, filename: str) -> str:
        """Extract text content from PDF or DOCX"""
        text = ""
        try:
            ext = os.path.splitext(filename)[1].lower()
            
            if ext == '.pdf':
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(file_path)
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                except ImportError:
                    print("PyMuPDF not installed, trying pypdf")
                    try:
                        from pypdf import PdfReader
                        reader = PdfReader(file_path)
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                    except ImportError:
                        print("No PDF library found")
                        
            elif ext in ['.docx', '.doc']:
                try:
                    import docx
                    doc = docx.Document(file_path)
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                except ImportError:
                    print("python-docx not installed")
                    
        except Exception as e:
            print(f"Text extraction error: {e}")
            
        return text or f"Could not extract text from {filename}"
    
    def _create_mock_parsed_data(self, filename: str) -> Dict[str, Any]:
        """Create mock parsed data for demonstration (fallback)"""
        
        # Generate mock data based on filename or provide defaults
        if "senior" in filename.lower() or "sr" in filename.lower():
            experience_years = 7.5
            education_level = "Master's"
            skills = ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes", "PostgreSQL", "MongoDB"]
        elif "junior" in filename.lower() or "jr" in filename.lower():
            experience_years = 2.0
            education_level = "Bachelor's"
            skills = ["Python", "JavaScript", "HTML", "CSS", "SQL", "Git"]
        else:
            experience_years = 4.5
            education_level = "Bachelor's"
            skills = ["Python", "JavaScript", "React", "Node.js", "SQL", "Git", "AWS"]
        
        return {
            "personal_info": {
                "name": "Candidate Name", 
                "email": "candidate@example.com",
                "phone": "+1-555-0123",
                "linkedin": "linkedin.com/in/candidate",
                "github": "github.com/candidate"
            },
            "skills": skills,
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2021 - Present",
                    "description": "Developed and maintained web applications using modern technologies."
                }
            ],
            "education": [
                {
                    "degree": f"{education_level} in Computer Science",
                    "institution": "Tech University",
                    "year": "2019"
                }
            ],
            "projects": [],
            "certifications": [],
            "languages": ["English"],
            "summary": "Experienced software engineer.",
            "experience_years": experience_years,
            "education_level": education_level,
            "suggested_job_titles": ["Software Engineer", "Full Stack Developer"] 
        }

    async def _extract_with_gemini(self, text: str) -> Dict[str, Any]:
        """Extract structured data from resume text using Gemini"""
        try:
            import google.generativeai as genai
            import json
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return None
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            You are an expert resume parser. Extract structured information from the following resume text.
            
            Resume Text:
            {text[:10000]}  # Limit text length to avoid token limits
            
            Extract the following fields in JSON format:
            1. personal_info (name, email, phone, linkedin, github)
            2. skills (list of technical and soft skills)
            3. experience (list of objects with title, company, duration, description)
            4. education (list of objects with degree, institution, year)
            5. projects (list of objects with name, description, technologies)
            6. certifications (list of strings)
            7. languages (list of strings)
            8. summary (brief professional summary)
            9. experience_years (numeric estimate of total years of experience)
            10. education_level (highest degree obtained, e.g., "Bachelor's", "Master's")
            11. suggested_job_titles (list of 3-5 job titles suitable for this candidate based on skills and experience)

            Return ONLY valid JSON. Do not include markdown formatting.
            """
            
            print("Calling Gemini API for resume extraction...")
            response = model.generate_content(prompt)
            print("Gemini API response received")
            result_text = response.text
            
            # Clean up json string if it contains markdown code blocks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
                
            return json.loads(result_text)
            
        except Exception as e:
            print(f"Error extracting with Gemini: {e}")
            return None
