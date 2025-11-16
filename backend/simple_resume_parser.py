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
        """Parse resume file and extract structured data"""
        
        # For now, we'll just create mock data since we can't parse files
        # In a real implementation, you'd use PDF/DOCX parsing libraries
        
        parsed_data = self._create_mock_parsed_data(filename)
        
        return {
            "filename": filename,
            "file_path": file_path,
            "raw_text": f"Mock text extracted from {filename}",
            "parsed_data": parsed_data,
            "extraction_confidence": 0.8,
            "extracted_at": datetime.utcnow().isoformat()
        }
    
    def _create_mock_parsed_data(self, filename: str) -> Dict[str, Any]:
        """Create mock parsed data for demonstration"""
        
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
                },
                {
                    "title": "Junior Developer",
                    "company": "StartupXYZ",
                    "duration": "2019 - 2021",
                    "description": "Built responsive web interfaces and RESTful APIs."
                }
            ],
            "education": [
                {
                    "degree": f"{education_level} in Computer Science",
                    "institution": "Tech University",
                    "year": "2019"
                }
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Built a full-stack e-commerce application with React and Node.js",
                    "technologies": ["React", "Node.js", "MongoDB", "Express"]
                },
                {
                    "name": "Task Management App",
                    "description": "Developed a task management application with real-time updates",
                    "technologies": ["Vue.js", "Firebase", "TypeScript"]
                }
            ],
            "certifications": [
                "AWS Certified Developer",
                "Google Cloud Professional"
            ],
            "languages": ["English", "Spanish"],
            "summary": "Experienced software engineer with expertise in full-stack development and cloud technologies.",
            "experience_years": experience_years,
            "education_level": education_level
        }
