#!/usr/bin/env python3
"""
Test script to debug analysis results and check what explanations are being returned
"""
import requests
import json
import time

def test_latest_analysis():
    """Check the latest successful analysis to see what explanation data is being returned"""
    
    # Try a known document ID from recent logs
    document_ids = [
        "15f2d8e3-932d-47c0-9ec4-7e71c975efd1",
        "ae823a2b-1d95-46ec-8f8d-6515d0ac8489", 
        "5b83b779-dd4a-4935-9299-341857e17b85"
    ]
    
    for doc_id in document_ids:
        print(f"\n🔍 Testing document ID: {doc_id}")
        
        # Test basic analysis endpoint
        url = f"http://localhost:8000/analysis/{doc_id}"
        try:
            response = requests.get(url, timeout=10)
            print(f"Basic analysis status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Basic analysis found!")
                
                # Check what explanation fields are present
                explanation_fields = [
                    'document_explanation',
                    'key_provisions_explained', 
                    'legal_implications',
                    'practical_impact',
                    'clause_by_clause_summary',
                    'overall_risk_explanation'
                ]
                
                print("\n📊 Explanation data found:")
                for field in explanation_fields:
                    if field in data:
                        value = data[field]
                        if isinstance(value, str):
                            preview = value[:100] + "..." if len(value) > 100 else value
                        else:
                            preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                        print(f"  • {field}: {preview}")
                    else:
                        print(f"  ❌ {field}: NOT FOUND")
                
                # Check overall risk score and breakdown
                if 'overall_risk_score' in data:
                    print(f"\n📈 Overall Risk Score: {data['overall_risk_score']}")
                
                if 'risk_categories' in data:
                    print(f"📋 Risk Categories: {len(data['risk_categories'])} found")
                    for cat in data['risk_categories'][:3]:  # Show first 3
                        print(f"  • {cat.get('category', 'Unknown')}: {cat.get('description', 'No description')[:50]}...")
                
                return data
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error checking {doc_id}: {e}")
            continue
    
    print("❌ No successful analysis found")
    return None

def test_upload_and_analyze():
    """Upload a new document and wait for analysis"""
    test_content = """
    RENTAL AGREEMENT
    
    This agreement is made between Landlord and Tenant for the rental of property located at 123 Main St.
    
    PAYMENT TERMS: Rent is due on the 1st of each month. Late fees of $50 apply after 5 days.
    
    TERMINATION: Either party may terminate with 30 days notice. Early termination penalty is 2 months rent.
    
    LIABILITY: Tenant is responsible for all damages. Landlord liability is limited to $500.
    """
    
    print("\n🚀 Testing new upload...")
    
    # Create test file
    test_file_path = "/tmp/test_rental_agreement.txt"
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    try:
        # Upload file
        url = "http://localhost:8000/upload/enhanced"
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_rental_agreement.txt', f, 'text/plain')}
            response = requests.post(url, files=files, timeout=30)
        
        print(f"Upload status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            document_id = data.get('document_id')
            print(f"✅ Uploaded! Document ID: {document_id}")
            
            # Wait for processing
            print("⏳ Waiting for analysis...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                
                try:
                    analysis_url = f"http://localhost:8000/analysis/{document_id}"
                    analysis_response = requests.get(analysis_url, timeout=5)
                    
                    if analysis_response.status_code == 200:
                        print(f"✅ Analysis completed in {i+1} seconds!")
                        return analysis_response.json()
                    
                except:
                    continue
            
            print("❌ Analysis timed out")
            return None
        else:
            print(f"❌ Upload failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        # Clean up
        import os
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    print("🧪 Testing Legal AI Analysis Results")
    print("="*50)
    
    # First check existing analysis
    existing_data = test_latest_analysis()
    
    # If no existing data or we want fresh data, upload new
    if not existing_data:
        print("\n" + "="*50)
        new_data = test_upload_and_analyze()
        if new_data:
            print("\n📋 New Analysis Summary:")
            print(f"Risk Score: {new_data.get('overall_risk_score', 'N/A')}")
            print(f"Document Explanation: {new_data.get('document_explanation', 'Missing')[:100]}...")
    
    print("\n✅ Test completed!")
