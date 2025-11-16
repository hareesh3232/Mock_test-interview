"""
Simple API test script
"""
import requests
import json

def test_server():
    print("🧪 Testing Mock Interview System API")
    print("=" * 50)

    base_url = "http://localhost:8000"

    # Test 1: Basic connection
    try:
        print("1️⃣ Testing basic connection...")
        response = requests.get(base_url)
        print(f"   ✅ Server Status: {response.status_code}")
        print(f"   📄 Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return

    # Test 2: Health check
    try:
        print("\n2️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"   ✅ Health Status: {response.status_code}")
        print(f"   📄 Health: {response.json()}")
    except Exception as e:
        print(f"   ❌ Health Error: {e}")

    # Test 3: Job search
    try:
        print("\n3️⃣ Testing job search...")
        response = requests.get(f"{base_url}/jobs/search", params={
            "skills": "Python,JavaScript,SQL,Docker,AWS",
            "location": "us",
            "count": 10
        })
        print(f"   ✅ Job Search Status: {response.status_code}")
        data = response.json()
        print(f"   📄 Found {data['total']} jobs")
        print(f"   🔍 Search skills: {data['search_skills']}")
        if data['jobs']:
            print(f"   📋 First job: {data['jobs'][0]['title']} at {data['jobs'][0]['company']}")
    except Exception as e:
        print(f"   ❌ Job Search Error: {e}")

    # Test 4: Resume upload
    try:
        print("\n4️⃣ Testing resume upload...")
        response = requests.post(f"{base_url}/resume/upload", data={
            "user_name": "Test User",
            "user_email": "test@example.com"
        }, files={"file": ("test.txt", b"test resume content")})
        print(f"   ✅ Upload Status: {response.status_code}")
        data = response.json()
        print(f"   📄 Resume ID: {data['resume_id']}")
        print(f"   🎯 Skills found: {data['skills']}")
    except Exception as e:
        print(f"   ❌ Upload Error: {e}")

if __name__ == "__main__":
    test_server()








