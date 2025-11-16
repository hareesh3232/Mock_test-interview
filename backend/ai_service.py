"""
AI service for Gemini LLM integration
"""

import google.generativeai as genai
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_interview_questions(self, job_description: str, resume_skills: List[str], 
                                         job_requirements: List[str], question_count: int = 10) -> List[Dict[str, Any]]:
        """Generate job-specific interview questions based on job description and resume skills"""
        
        prompt = f"""
        You are an expert HR professional and technical interviewer. Generate {question_count} interview questions for the following job position.
        
        Job Description:
        {job_description}
        
        Job Requirements:
        {', '.join(job_requirements)}
        
        Candidate Skills (from resume):
        {', '.join(resume_skills)}
        
        Generate a mix of:
        1. Technical questions (40%) - specific to the role and technologies mentioned
        2. Behavioral questions (30%) - STAR method questions about past experiences
        3. Situational questions (20%) - hypothetical scenarios
        4. Company/role-specific questions (10%) - about the position and company
        
        For each question, provide:
        - question: The actual question text
        - type: technical, behavioral, situational, or company
        - difficulty: easy, medium, or hard
        - expected_keywords: List of key terms that should be in a good answer
        - time_limit: Suggested time to answer (in minutes)
        
        Return the response as a JSON array of objects.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse the response and return structured data
            questions = self._parse_questions_response(response.text)
            return questions
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_fallback_questions(job_description, resume_skills, question_count)
    
    async def evaluate_answer(self, question: str, answer: str, question_type: str, 
                            expected_keywords: List[str] = None) -> Dict[str, Any]:
        """Evaluate a candidate's answer and provide scores and feedback"""
        
        prompt = f"""
        You are an expert interviewer evaluating a candidate's answer. Provide a detailed evaluation.
        
        Question: {question}
        Question Type: {question_type}
        Candidate's Answer: {answer}
        Expected Keywords: {', '.join(expected_keywords) if expected_keywords else 'Not specified'}
        
        Evaluate the answer on these criteria (score 0-10 for each):
        1. Technical Accuracy - How correct and technically sound is the answer?
        2. Communication Clarity - How clear and well-structured is the response?
        3. Relevance - How well does the answer address the question?
        4. Depth - How comprehensive and detailed is the response?
        5. Examples/Evidence - Does the answer include relevant examples or evidence?
        
        Provide:
        - technical_score: Score for technical accuracy (0-10)
        - communication_score: Score for communication clarity (0-10)
        - relevance_score: Score for relevance to the question (0-10)
        - overall_score: Average of all scores (0-10)
        - feedback: Detailed written feedback
        - strengths: List of what the candidate did well
        - weaknesses: List of areas for improvement
        - suggestions: Specific suggestions for better answers
        
        Return the response as a JSON object.
        """
        
        try:
            response = self.model.generate_content(prompt)
            evaluation = self._parse_evaluation_response(response.text)
            return evaluation
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return self._get_fallback_evaluation(question, answer)
    
    async def generate_final_feedback(self, interview_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive final feedback for the entire interview"""
        
        prompt = f"""
        You are an expert career coach providing final feedback for a mock interview session.
        
        Interview Performance Data:
        {interview_data}
        
        Provide a comprehensive analysis including:
        - overall_performance: Summary of overall performance
        - technical_strengths: Technical areas where the candidate excelled
        - communication_strengths: Communication skills that were strong
        - improvement_areas: Specific areas that need improvement
        - recommendations: Actionable recommendations for improvement
        - next_steps: Suggested next steps for career development
        
        Return the response as a JSON object.
        """
        
        try:
            response = self.model.generate_content(prompt)
            feedback = self._parse_feedback_response(response.text)
            return feedback
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return self._get_fallback_feedback()
    
    def _parse_questions_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse the Gemini response for questions"""
        try:
            import json
            # Try to extract JSON from the response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: return basic questions
        return self._get_fallback_questions("", [], 5)
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the Gemini response for evaluation"""
        try:
            import json
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback evaluation
        return self._get_fallback_evaluation("", "")
    
    def _parse_feedback_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the Gemini response for feedback"""
        try:
            import json
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback feedback
        return self._get_fallback_feedback()
    
    def _get_fallback_questions(self, job_description: str, resume_skills: List[str], count: int) -> List[Dict[str, Any]]:
        """Fallback questions if AI fails"""
        return [
            {
                "question": "Tell me about yourself and your relevant experience.",
                "type": "behavioral",
                "difficulty": "easy",
                "expected_keywords": ["experience", "skills", "background"],
                "time_limit": 3
            },
            {
                "question": "What interests you about this role?",
                "type": "company",
                "difficulty": "easy",
                "expected_keywords": ["passion", "growth", "challenge"],
                "time_limit": 2
            },
            {
                "question": "Describe a challenging project you worked on.",
                "type": "behavioral",
                "difficulty": "medium",
                "expected_keywords": ["problem", "solution", "outcome"],
                "time_limit": 5
            }
        ][:count]
    
    def _get_fallback_evaluation(self, question: str, answer: str) -> Dict[str, Any]:
        """Fallback evaluation if AI fails"""
        return {
            "technical_score": 7.0,
            "communication_score": 7.0,
            "relevance_score": 7.0,
            "overall_score": 7.0,
            "feedback": "Good answer with room for improvement. Consider providing more specific examples.",
            "strengths": ["Clear communication", "Relevant experience"],
            "weaknesses": ["Could be more specific", "Missing technical details"],
            "suggestions": ["Provide specific examples", "Include metrics and results"]
        }
    
    def _get_fallback_feedback(self) -> Dict[str, Any]:
        """Fallback feedback if AI fails"""
        return {
            "overall_performance": "Good performance with areas for improvement",
            "technical_strengths": ["Problem-solving", "Technical knowledge"],
            "communication_strengths": ["Clear articulation", "Good structure"],
            "improvement_areas": ["More specific examples", "Technical depth"],
            "recommendations": ["Practice technical questions", "Prepare STAR examples"],
            "next_steps": ["Continue learning", "Practice interviews"]
        }
