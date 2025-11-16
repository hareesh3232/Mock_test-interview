import os
from dotenv import load_dotenv

print("--- Starting Environment Test ---")

try:
    print("Attempting to load .env file...")
    load_dotenv()
    print("load_dotenv() executed.")

    gemini_key = os.getenv("GEMINI_API_KEY")
    adzuna_id = os.getenv("ADZUNA_APP_ID")

    print(f"GEMINI_API_KEY is set: {'Yes' if gemini_key else 'No'}")
    if gemini_key:
        print(f"   - First 5 chars: {gemini_key[:5]}...")

    print(f"ADZUNA_APP_ID is set: {'Yes' if adzuna_id else 'No'}")

except Exception as e:
    print(f"An error occurred: {e}")

print("--- Environment Test Finished ---")
