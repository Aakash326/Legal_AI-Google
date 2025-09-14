#!/usr/bin/env python3
"""Simple test server to verify basic functionality"""

import os
from pathlib import Path
from fastapi import FastAPI
import uvicorn

# Load environment variables from .env file
def load_env_file():
    env_path = Path(__file__).parent / '.env'
    
    if env_path.exists():
        print(f"Loading environment variables from {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    os.environ[key] = value

# Load env vars
load_env_file()

# Simple test app
app = FastAPI(
    title="LegalClarity AI Backend - Test",
    description="Simple test version",
    version="1.0.0-test"
)

@app.get("/")
async def root():
    return {
        "message": "LegalClarity AI Backend - Test Mode",
        "status": "running",
        "google_api_key_set": bool(os.getenv("GOOGLE_API_KEY")),
        "project_id": os.getenv("GOOGLE_CLOUD_PROJECT")
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "environment": {
            "google_api_key": "configured" if os.getenv("GOOGLE_API_KEY") else "missing",
            "project_id": os.getenv("GOOGLE_CLOUD_PROJECT", "not_set"),
            "crewai_enabled": os.getenv("ENABLE_CREWAI", "false")
        }
    }

@app.get("/test-gemini")
async def test_gemini():
    """Test basic Gemini API connection"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"error": "Google API key not set"}
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Try different model names
        model_names = ['gemini-1.5-pro-latest', 'gemini-1.5-pro', 'gemini-pro']
        model = None
        last_error = None
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                break
            except Exception as e:
                last_error = e
                continue
        
        if not model:
            return {
                "status": "error",
                "message": f"Could not initialize any Gemini model: {last_error}"
            }
        
        # Test simple request
        response = model.generate_content("Say hello")
        
        return {
            "status": "success",
            "message": "Gemini API is working",
            "response": response.text[:100] + "..." if len(response.text) > 100 else response.text
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Gemini API test failed: {str(e)}"
        }

if __name__ == "__main__":
    print("🧪 Starting LegalClarity AI Test Server")
    print("📡 Test endpoints:")
    print("   - http://localhost:8000/")
    print("   - http://localhost:8000/health")
    print("   - http://localhost:8000/test-gemini")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )