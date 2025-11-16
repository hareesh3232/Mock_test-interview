#!/usr/bin/env python3
"""
Test script for JobSearchService
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from job_search_service import JobSearchService

async def test_job_search():
    """Test the job search service with sample skills"""
    
    print("🔍 Testing Job Search Service...")
    print("=" * 50)
    
    # Initialize the service
    job_service = JobSearchService()
    
    # Test with sample skills
    test_skills = ["Python", "React", "JavaScript", "AWS"]
    location = "us"
    count = 5
    
    print(f"Searching for jobs with skills: {', '.join(test_skills)}")
    print(f"Location: {location}")
    print(f"Number of results: {count}")
    print()
    
    try:
        # Search for jobs
        jobs = await job_service.search_jobs(test_skills, location, count)
        
        print(f"✅ Found {len(jobs)} jobs:")
        print("-" * 50)
        
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Salary: ${job.get('salary_min', 'N/A')} - ${job.get('salary_max', 'N/A')} {job.get('salary_currency', 'USD')}")
            print(f"   Experience: {job.get('experience_level', 'N/A')}")
            print(f"   Remote: {'Yes' if job.get('remote_work', False) else 'No'}")
            print(f"   Match Score: {job.get('match_score', 0):.2f}")
            print(f"   Skills Required: {', '.join(job.get('skills_required', [])[:5])}")
            print(f"   Description: {job.get('description', '')[:100]}...")
            print()
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return False
    
    print("✅ Job search test completed successfully!")
    return True

async def test_real_api():
    """Test the real API functionality (will fallback to mock data)"""
    
    print("\n🌐 Testing Real API (with fallback to mock data)...")
    print("=" * 50)
    
    job_service = JobSearchService()
    test_skills = ["Data Science", "Machine Learning", "Python"]
    
    try:
        jobs = await job_service.search_jobs_real_api(test_skills, "us", 3)
        print(f"✅ Real API test completed - found {len(jobs)} jobs")
        
        for job in jobs:
            print(f"- {job['title']} at {job['company']} (Source: {job.get('source', 'Unknown')})")
            
    except Exception as e:
        print(f"❌ Real API test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Job Search Service Test")
    print("=" * 50)
    
    # Run the async test
    asyncio.run(test_job_search())
    asyncio.run(test_real_api())
    
    print("\n🎉 All tests completed!")







