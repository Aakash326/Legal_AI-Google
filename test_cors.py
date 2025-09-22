#!/usr/bin/env python3
"""
Test CORS and JavaScript-like request to backend
"""
import requests
import json

def test_cors_and_frontend_request():
    url = "http://localhost:8000/upload/enhanced"
    
    # Headers that a browser would send
    headers = {
        'Accept': 'application/json',
        'Origin': 'http://localhost:3000',
        'Referer': 'http://localhost:3000/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    # Test OPTIONS request first (CORS preflight)
    try:
        options_response = requests.options(url, headers=headers)
        print(f"OPTIONS Status: {options_response.status_code}")
        print(f"CORS Headers: {dict(options_response.headers)}")
        print()
    except Exception as e:
        print(f"OPTIONS request failed: {e}")
    
    # Test actual POST request
    try:
        with open('/tmp/sample_contract.txt', 'rb') as f:
            files = {'file': ('sample_contract.txt', f, 'text/plain')}
            data = {'use_crew_enhancement': 'true'}
            
            response = requests.post(url, files=files, data=data, headers=headers)
            
        print(f"POST Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
    except Exception as e:
        print(f"POST request failed: {e}")

if __name__ == "__main__":
    test_cors_and_frontend_request()
