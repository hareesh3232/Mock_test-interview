import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

print("Attempting to test Gemini API connection...")

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ FATAL ERROR: GEMINI_API_KEY not found in .env file.")
    exit()

print("GEMINI_API_KEY found.")

try:
    print("Initializing ChatGoogleGenerativeAI...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY
    )
    print("✅ Successfully initialized ChatGoogleGenerativeAI.")
    
    print("Sending a test message to Gemini...")
    response = llm.invoke("Hello, are you there?")
    
    if response and hasattr(response, 'content') and response.content:
        print("✅ Gemini API responded successfully!")
        print(f"Response: {response.content[:100]}...")
    else:
        print("⚠️ Gemini API responded, but the response was empty or invalid.")

except Exception as e:
    print(f"❌ An error occurred during Gemini API test: {e}")
