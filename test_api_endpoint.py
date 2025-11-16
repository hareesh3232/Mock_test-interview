"""Test the actual API endpoint"""
import requests
import json

# Test data
payload = {
    "resume_id": "test_resume",
    "job_id": "test_job"
}

print("Testing /interview/generate endpoint...")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8001/interview/generate",
        json=payload,
        timeout=60
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Interview questions generated via API!")
    else:
        print(f"\n❌ ERROR: Status {response.status_code}")
        
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
