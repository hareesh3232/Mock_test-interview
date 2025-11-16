"""Test interview question generation directly"""
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print(f"API Key loaded: {'Yes' if OPENROUTER_API_KEY else 'No'}")

# Mock resume and job data
resume = {
    "skills": ["Python", "JavaScript", "React"],
    "experience_years": 3,
    "education_level": "Bachelor's"
}

job = {
    "title": "Full Stack Developer",
    "description": "Looking for a developer with Python and React experience",
    "skills_required": ["Python", "React", "Node.js"]
}

async def test_generation():
    try:
        print("\n1. Initializing ChatOpenAI...")
        llm = ChatOpenAI(
            model="openrouter/auto",
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.1,
            max_tokens=2048
        )
        print("✅ ChatOpenAI initialized")
        
        print("\n2. Creating prompt template...")
        prompt_template = PromptTemplate(
            input_variables=["skills", "job_title", "experience"],
            template="""
You are an expert technical interviewer. Generate exactly 5 interview questions for a {job_title} position.

Candidate Background:
- Skills: {skills}
- Experience: {experience} years

Generate 5 diverse questions (one per line):
1. One technical question
2. One behavioral question
3. One scenario-based question
4. One problem-solving question
5. One growth mindset question

Format: Just list the questions, one per line, numbered 1-5.
"""
        )
        print("✅ Prompt template created")
        
        print("\n3. Formatting prompt...")
        formatted_prompt = prompt_template.format(
            skills=", ".join(resume["skills"]),
            job_title=job["title"],
            experience=resume["experience_years"]
        )
        print(f"Prompt preview: {formatted_prompt[:200]}...")
        
        print("\n4. Sending request to OpenRouter...")
        response = await llm.ainvoke(formatted_prompt)
        print("✅ Response received!")
        
        print("\n5. Response content:")
        print("-" * 50)
        print(response.content)
        print("-" * 50)
        
        print("\n✅ SUCCESS! Interview questions generated successfully!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        import traceback
        print(f"\n   Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generation())
