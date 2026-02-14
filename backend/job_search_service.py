"""
Job search service for finding relevant job listings
"""

import httpx
import asyncio
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import os

class JobSearchService:
    def __init__(self):
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")
    
    async def search_jobs(self, skills: List[str], location: str = "us", 
                         results_per_page: int = 20) -> List[Dict[str, Any]]:
        """Search for jobs based on skills"""
        
        # Use real API if keys are available
        if self.app_id and self.app_key:
            return await self.search_jobs_real_api(skills, location, results_per_page)
            
        # Fallback to mock data if API fails or no keys
        return self._get_mock_jobs(skills, location, results_per_page)
    
    async def search_jobs_real_api(self, skills: List[str], location: str = "us", 
                                  results_per_page: int = 20) -> List[Dict[str, Any]]:
        """Search for jobs using real API (when API keys are available)"""
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "app_id": self.app_id,
                    "app_key": self.app_key,
                    "what": " ".join(skills),
                    "where": location,
                    "results_per_page": results_per_page,
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
                        "experience_level": self._determine_experience_level(job.get("title", "")),
                        "remote_work": "remote" in job.get("description", "").lower(),
                        "job_url": job.get("redirect_url"),
                        "source": "Adzuna",
                        "posted_date": self._parse_date(job.get("created")),
                        "requirements": self._extract_requirements(job.get("description", "")),
                        "skills_required": self._extract_skills_from_description(job.get("description", ""))
                    })
                
                return jobs
                
        except Exception as e:
            print(f"Error fetching jobs from API: {e}")
            # Fallback to mock data
            return self._get_mock_jobs(skills, location, results_per_page)
    
    def _get_mock_jobs(self, skills: List[str], location: str, count: int) -> List[Dict[str, Any]]:
        """Generate mock job data for testing"""
        
        # Mock job templates based on common skills
        job_templates = [
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "location": "San Francisco, CA",
                "description": "We are looking for a Senior Software Engineer to join our team. You will be responsible for developing and maintaining our core platform using modern technologies.",
                "salary_min": 120000,
                "salary_max": 180000,
                "job_type": "Full-time",
                "experience_level": "Senior",
                "remote_work": True,
                "requirements": ["5+ years experience", "Strong problem-solving skills", "Team leadership experience"],
                "skills_required": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"]
            },
            {
                "title": "Full Stack Developer",
                "company": "StartupXYZ",
                "location": "New York, NY",
                "description": "Join our fast-growing startup as a Full Stack Developer. You'll work on both frontend and backend development, building scalable web applications.",
                "salary_min": 80000,
                "salary_max": 120000,
                "job_type": "Full-time",
                "experience_level": "Mid",
                "remote_work": False,
                "requirements": ["3+ years experience", "Full-stack development", "Agile methodology"],
                "skills_required": ["React", "Node.js", "MongoDB", "Express", "TypeScript", "Git"]
            },
            {
                "title": "Data Scientist",
                "company": "DataCorp",
                "location": "Seattle, WA",
                "description": "We're seeking a Data Scientist to analyze large datasets and build machine learning models. You'll work with our data team to extract insights and drive business decisions.",
                "salary_min": 100000,
                "salary_max": 150000,
                "job_type": "Full-time",
                "experience_level": "Mid",
                "remote_work": True,
                "requirements": ["PhD or Master's in related field", "Machine learning experience", "Statistical analysis"],
                "skills_required": ["Python", "R", "TensorFlow", "Pandas", "NumPy", "Scikit-learn", "SQL"]
            },
            {
                "title": "DevOps Engineer",
                "company": "CloudTech",
                "location": "Austin, TX",
                "description": "Looking for a DevOps Engineer to manage our cloud infrastructure and CI/CD pipelines. You'll work with our development team to ensure smooth deployments.",
                "salary_min": 90000,
                "salary_max": 140000,
                "job_type": "Full-time",
                "experience_level": "Mid",
                "remote_work": True,
                "requirements": ["Cloud platform experience", "CI/CD knowledge", "Infrastructure as Code"],
                "skills_required": ["AWS", "Docker", "Kubernetes", "Terraform", "Jenkins", "Linux", "Bash"]
            },
            {
                "title": "Frontend Developer",
                "company": "DesignStudio",
                "location": "Los Angeles, CA",
                "description": "We need a creative Frontend Developer to build beautiful, responsive user interfaces. You'll work closely with our design team to bring mockups to life.",
                "salary_min": 70000,
                "salary_max": 110000,
                "job_type": "Full-time",
                "experience_level": "Junior",
                "remote_work": False,
                "requirements": ["2+ years experience", "UI/UX understanding", "Responsive design"],
                "skills_required": ["React", "Vue.js", "CSS", "Sass", "Webpack", "Figma", "JavaScript"]
            },
            {
                "title": "Backend Developer",
                "company": "APICorp",
                "location": "Boston, MA",
                "description": "Join our backend team to build robust APIs and microservices. You'll work with large-scale systems and ensure high performance and reliability.",
                "salary_min": 85000,
                "salary_max": 130000,
                "job_type": "Full-time",
                "experience_level": "Mid",
                "remote_work": True,
                "requirements": ["API development experience", "Database design", "System architecture"],
                "skills_required": ["Python", "Django", "PostgreSQL", "Redis", "REST API", "GraphQL", "Docker"]
            },
            {
                "title": "Machine Learning Engineer",
                "company": "AI Solutions",
                "location": "Denver, CO",
                "description": "We're looking for a Machine Learning Engineer to develop and deploy ML models in production. You'll work on cutting-edge AI projects and help scale our ML infrastructure.",
                "salary_min": 110000,
                "salary_max": 160000,
                "job_type": "Full-time",
                "experience_level": "Senior",
                "remote_work": True,
                "requirements": ["ML model deployment", "Production experience", "MLOps knowledge"],
                "skills_required": ["Python", "TensorFlow", "PyTorch", "Kubernetes", "MLflow", "Docker", "AWS"]
            },
            {
                "title": "Mobile App Developer",
                "company": "MobileFirst",
                "location": "Chicago, IL",
                "description": "Develop native and cross-platform mobile applications. You'll work on both iOS and Android apps, ensuring great user experience across platforms.",
                "salary_min": 75000,
                "salary_max": 115000,
                "job_type": "Full-time",
                "experience_level": "Mid",
                "remote_work": False,
                "requirements": ["Mobile development experience", "Cross-platform knowledge", "App Store deployment"],
                "skills_required": ["React Native", "Flutter", "Swift", "Kotlin", "iOS", "Android", "Firebase"]
            }
        ]
        
        # Filter jobs based on skills
        relevant_jobs = []
        for job in job_templates:
            job_skills = [skill.lower() for skill in job["skills_required"]]
            user_skills = [skill.lower() for skill in skills]
            
            # Calculate match score
            match_score = len(set(job_skills) & set(user_skills)) / len(job_skills) if job_skills else 0
            
            if match_score > 0.2:  # At least 20% skill match
                job["match_score"] = match_score
                job["id"] = f"mock_{random.randint(1000, 9999)}"
                job["job_url"] = f"https://example.com/jobs/{job['id']}"
                job["posted_date"] = datetime.now() - timedelta(days=random.randint(1, 30))
                job["salary_currency"] = "USD"
                job["source"] = "Mock API"
                relevant_jobs.append(job)
        
        # Sort by match score and return requested count
        relevant_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        return relevant_jobs[:count]
    
    def _determine_experience_level(self, title: str) -> str:
        """Determine experience level from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ["senior", "lead", "principal", "staff"]):
            return "Senior"
        elif any(word in title_lower for word in ["junior", "entry", "intern", "trainee"]):
            return "Junior"
        else:
            return "Mid"
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            # Handle different date formats
            if isinstance(date_str, str):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return datetime.now()
        except:
            return datetime.now()
    
    def _extract_requirements(self, description: str) -> List[str]:
        """Extract job requirements from description"""
        requirements = []
        
        # Look for common requirement patterns
        req_patterns = [
            r'\d+\+?\s*years?\s+experience',
            r'Bachelor[^,\n]*',
            r'Master[^,\n]*',
            r'PhD[^,\n]*',
            r'Strong\s+[^,\n]+',
            r'Experience\s+with\s+[^,\n]+',
            r'Knowledge\s+of\s+[^,\n]+'
        ]
        
        for pattern in req_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                requirements.append(match.group().strip())
        
        return requirements[:5]  # Limit to 5 requirements
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills mentioned in job description"""
        # Common technical skills to look for
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
        
        return found_skills
