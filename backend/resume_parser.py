"""
Resume parsing service for PDF and DOCX files
"""

import os
import uuid
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

# Optional imports with fallbacks
try:
    import PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

class ResumeParser:
    def __init__(self):
        # Load spaCy model for NLP processing
        self.nlp = None
        if HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except (OSError, ValueError) as e:
                print(f"Warning: spaCy model not available ({e}). Using basic text processing.")
        else:
            print("Warning: spaCy not installed. Using basic text processing.")
    
    async def parse_resume(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Parse resume file and extract structured data"""
        
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            text = self._extract_text_from_pdf(file_path)
        elif filename.lower().endswith(('.doc', '.docx')):
            text = self._extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Please upload PDF or DOCX files.")
        
        # Parse the extracted text
        parsed_data = self._parse_text(text)
        
        return {
            "filename": filename,
            "file_path": file_path,
            "raw_text": text,
            "parsed_data": parsed_data,
            "extraction_confidence": 0.8,  # Placeholder confidence score
            "extracted_at": datetime.utcnow().isoformat()
        }
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        
        # Try with PyMuPDF first
        if HAS_PYMUPDF:
            try:
                doc = PyMuPDF.open(file_path)
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            except Exception as e:
                print(f"PyMuPDF failed: {e}")
        
        # Fallback to pdfplumber
        if HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                return text
            except Exception as e2:
                print(f"pdfplumber also failed: {e2}")
        
        # If no PDF library is available, return a mock response
        return "PDF parsing not available. Please install PyMuPDF or pdfplumber."
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        if not HAS_DOCX:
            return "DOCX parsing not available. Please install python-docx."
            
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Could not extract text from DOCX: {e}"
    
    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse extracted text to extract structured information"""
        
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Extract different sections
        parsed_data = {
            "personal_info": self._extract_personal_info(text),
            "skills": self._extract_skills(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text),
            "projects": self._extract_projects(text),
            "certifications": self._extract_certifications(text),
            "languages": self._extract_languages(text),
            "summary": self._extract_summary(text)
        }
        
        # Calculate experience years
        parsed_data["experience_years"] = self._calculate_experience_years(parsed_data["experience"])
        
        # Extract education level
        parsed_data["education_level"] = self._determine_education_level(parsed_data["education"])
        
        return parsed_data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extract personal information"""
        personal_info = {}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            personal_info["email"] = email_match.group()
        
        # Phone
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            personal_info["phone"] = phone_match.group()
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            personal_info["linkedin"] = linkedin_match.group()
        
        # GitHub
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            personal_info["github"] = github_match.group()
        
        return personal_info
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills"""
        # Common technical skills
        skill_keywords = [
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'Swift', 'Kotlin',
            'PHP', 'Ruby', 'Scala', 'R', 'MATLAB', 'SQL', 'HTML', 'CSS', 'Bash', 'PowerShell',
            
            # Frameworks and Libraries
            'React', 'Angular', 'Vue.js', 'Node.js', 'Express', 'Django', 'Flask', 'Spring', 'Laravel',
            'ASP.NET', 'Ruby on Rails', 'jQuery', 'Bootstrap', 'Tailwind CSS', 'Sass', 'Less',
            
            # Databases
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'SQLite', 'Oracle', 'SQL Server',
            'DynamoDB', 'Cassandra', 'Neo4j', 'CouchDB',
            
            # Cloud and DevOps
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions',
            'Terraform', 'Ansible', 'Chef', 'Puppet', 'Linux', 'Ubuntu', 'CentOS', 'Red Hat',
            
            # Data Science and ML
            'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn',
            'Jupyter', 'Apache Spark', 'Hadoop', 'Tableau', 'Power BI', 'R Studio',
            
            # Mobile Development
            'React Native', 'Flutter', 'Xamarin', 'Ionic', 'Cordova', 'Android Studio', 'Xcode',
            
            # Other Technologies
            'Git', 'SVN', 'Mercurial', 'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum',
            'JIRA', 'Confluence', 'Slack', 'Microsoft Office', 'Google Workspace'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Use NLP to find additional skills if spaCy is available
        if self.nlp:
            doc = self.nlp(text)
            # Look for technical terms and proper nouns
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    len(token.text) > 2 and 
                    token.text.isalpha() and
                    token.text not in found_skills):
                    found_skills.append(token.text)
        
        return list(set(found_skills))  # Remove duplicates
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience"""
        experience = []
        
        # Common job title patterns
        job_titles = [
            'Software Engineer', 'Developer', 'Programmer', 'Data Scientist', 'Analyst',
            'Manager', 'Director', 'Lead', 'Senior', 'Junior', 'Intern', 'Consultant',
            'Architect', 'Designer', 'Product Manager', 'Project Manager', 'Scrum Master'
        ]
        
        # Date patterns
        date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}|\d{1,2}/\d{1,2}/\d{4}'
        
        # Split text into sections and look for experience
        lines = text.split('\n')
        current_experience = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains a job title
            for title in job_titles:
                if title.lower() in line.lower():
                    if current_experience:
                        experience.append(current_experience)
                    current_experience = {
                        "title": title,
                        "company": "",
                        "duration": "",
                        "description": ""
                    }
                    break
            
            # Look for company names (simplified)
            if current_experience and not current_experience["company"]:
                # Simple heuristic: if line doesn't contain common job words, it might be company
                if not any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst']):
                    current_experience["company"] = line
            
            # Look for dates
            if re.search(date_pattern, line):
                if current_experience:
                    current_experience["duration"] = line
        
        if current_experience:
            experience.append(current_experience)
        
        return experience
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        
        # Degree patterns
        degree_patterns = [
            r'Bachelor[^s]*\s+of\s+[^,\n]+',
            r'Master[^s]*\s+of\s+[^,\n]+',
            r'PhD[^,\n]*',
            r'Doctorate[^,\n]*',
            r'Associate[^,\n]*',
            r'Certificate[^,\n]*',
            r'Diploma[^,\n]*'
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    "degree": match.group().strip(),
                    "institution": "",
                    "year": ""
                })
        
        return education
    
    def _extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project information"""
        projects = []
        
        # Look for project-related keywords
        project_keywords = ['project', 'portfolio', 'github', 'repository', 'developed', 'built', 'created']
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in project_keywords):
                projects.append({
                    "name": line,
                    "description": "",
                    "technologies": []
                })
        
        return projects
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r'AWS\s+[A-Za-z\s]+',
            r'Microsoft\s+[A-Za-z\s]+',
            r'Google\s+[A-Za-z\s]+',
            r'Cisco\s+[A-Za-z\s]+',
            r'PMP',
            r'Scrum\s+Master',
            r'Agile\s+[A-Za-z\s]+'
        ]
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                certifications.append(match.group().strip())
        
        return certifications
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages"""
        languages = []
        
        # Common language patterns
        language_patterns = [
            r'English', r'Spanish', r'French', r'German', r'Chinese', r'Japanese',
            r'Korean', r'Portuguese', r'Italian', r'Russian', r'Arabic', r'Hindi'
        ]
        
        for pattern in language_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                languages.append(pattern)
        
        return languages
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""
        # Look for summary/objective section
        summary_keywords = ['summary', 'objective', 'profile', 'about', 'overview']
        
        lines = text.split('\n')
        summary_lines = []
        in_summary = False
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in summary_keywords):
                in_summary = True
                continue
            elif in_summary and line and not line[0].isupper() and len(line) > 20:
                summary_lines.append(line)
            elif in_summary and line and line[0].isupper():
                break
        
        return ' '.join(summary_lines)
    
    def _calculate_experience_years(self, experience: List[Dict[str, Any]]) -> float:
        """Calculate total years of experience"""
        # This is a simplified calculation
        # In a real implementation, you'd parse dates and calculate actual years
        return len(experience) * 1.5  # Rough estimate
    
    def _determine_education_level(self, education: List[Dict[str, str]]) -> str:
        """Determine highest education level"""
        if not education:
            return "High School"
        
        degrees = [edu["degree"].lower() for edu in education]
        
        if any('phd' in degree or 'doctorate' in degree for degree in degrees):
            return "PhD"
        elif any('master' in degree for degree in degrees):
            return "Master's"
        elif any('bachelor' in degree for degree in degrees):
            return "Bachelor's"
        elif any('associate' in degree for degree in degrees):
            return "Associate's"
        else:
            return "High School"
