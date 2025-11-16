"""Test if frontend is accessible"""
import requests

print("Testing frontend at http://localhost:8001...")

try:
    response = requests.get("http://localhost:8001/", timeout=5)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Content Length: {len(response.text)} bytes")
    
    if response.status_code == 200:
        if 'text/html' in response.headers.get('content-type', ''):
            print("\n✅ Frontend is accessible!")
            print(f"Preview: {response.text[:200]}...")
        else:
            print(f"\n⚠️ Response is not HTML: {response.text[:200]}")
    else:
        print(f"\n❌ Error: Status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
