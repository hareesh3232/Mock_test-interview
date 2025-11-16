"""Test OpenRouter API integration"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print(f"API Key loaded: {OPENROUTER_API_KEY[:20]}..." if OPENROUTER_API_KEY else "No API key found")

try:
    print("\nInitializing ChatOpenAI for OpenRouter...")
    llm = ChatOpenAI(
        model="openrouter/auto",
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.1,
        max_tokens=100
    )
    
    print("Sending test message...")
    response = llm.invoke([HumanMessage(content="Say 'Hello, OpenRouter is working!' in one sentence.")])
    
    print(f"\n✅ Success! Response: {response.content}")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
