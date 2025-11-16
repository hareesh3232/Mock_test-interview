import time

print(f"[{time.time()}] Attempting to import ChatGoogleGenerativeAI...")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print(f"[{time.time()}] Successfully imported ChatGoogleGenerativeAI.")
except Exception as e:
    print(f"[{time.time()}] An error occurred during import: {e}")
