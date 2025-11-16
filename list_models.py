import os
import google.generativeai as genai
from dotenv import load_dotenv

print("Attempting to list available Gemini models...")

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ FATAL ERROR: GEMINI_API_KEY not found in .env file.")
    exit()

print("GEMINI_API_KEY found.")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Available models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")

except Exception as e:
    print(f"❌ An error occurred while listing models: {e}")
