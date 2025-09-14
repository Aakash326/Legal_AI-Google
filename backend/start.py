#!/usr/bin/env python3
"""Startup script for LegalClarity AI Backend with environment loading"""

import os
from pathlib import Path

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
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
                    print(f"Set {key}={value[:10]}{'...' if len(value) > 10 else ''}")
    else:
        print(f"Warning: .env file not found at {env_path}")
        print("Please create .env file with your configuration")

if __name__ == "__main__":
    print("🚀 Starting LegalClarity AI Backend with CrewAI Integration")
    print("=" * 60)
    
    # Load environment variables
    load_env_file()
    
    # Verify required environment variables
    required_vars = ['GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file")
        exit(1)
    
    print("\n✅ Environment variables loaded successfully")
    print(f"   - Google API Key: {'*' * 20}...{os.getenv('GOOGLE_API_KEY', '')[-4:]}")
    print(f"   - Google Cloud Project: {os.getenv('GOOGLE_CLOUD_PROJECT', 'Not set')}")
    print(f"   - CrewAI Enabled: {os.getenv('ENABLE_CREWAI', 'true')}")
    
    print("\n🤖 Initializing AI agents...")
    
    # Import and start the main application
    try:
        import uvicorn
        from main import app
        
        print("\n🌐 Starting FastAPI server...")
        print("📡 API Documentation: http://localhost:8000/docs")
        print("💚 Health Check: http://localhost:8000/health")
        print("🔍 System Status: http://localhost:8000/system/status")
        print("\n" + "=" * 60)
        
        # Start the server
        uvicorn.run(
            app,
            host=os.getenv("FASTAPI_HOST", "0.0.0.0"),
            port=int(os.getenv("FASTAPI_PORT", "8000")),
            reload=os.getenv("FASTAPI_DEBUG", "true").lower() == "true"
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server startup failed: {str(e)}")
        print("\nCommon solutions:")
        print("1. Check your .env file configuration")
        print("2. Verify Google API key is valid")
        print("3. Ensure all dependencies are installed: pip install -r requirements.txt")
        exit(1)