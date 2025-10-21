#!/usr/bin/env python3
"""
ForgeWeb Advanced Functionality Tests
Tests API endpoints, file operations, and specific features
"""

import requests
import json
import os

def test_post_endpoint(url, data, name):
    try:
        response = requests.post(url, json=data, timeout=10)
        status = "✅" if response.status_code in [200, 201] else "❌"
        print(f"{status} {name}: Status {response.status_code}")
        
        if 'application/json' in response.headers.get('content-type', ''):
            try:
                result = response.json()
                print(f"    Response: {json.dumps(result, indent=2)[:200]}...")
            except:
                pass
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False

def test_file_operations():
    print("\n7. FILE SYSTEM TESTS")
    
    # Check important files exist
    files_to_check = [
        ".env.example",
        "requirements.txt", 
        "setup-dev.sh",
        "BUILDLY.yaml",
        "admin/file-api.py",
        "templates/base.html",
        "assets/forgeweb-logo-512.svg"
    ]
    
    for file_path in files_to_check:
        full_path = f"/Users/greglind/Projects/buildly/THE FORGE/ForgeWeb/{file_path}"
        exists = os.path.exists(full_path)
        status = "✅" if exists else "❌"
        print(f"{status} File exists: {file_path}")

def test_api_functionality():
    print("\n8. API FUNCTIONALITY TESTS")
    
    base_url = "http://localhost:8000"
    
    # Test branding API POST
    branding_data = {
        "colors": {
            "primary": "#1b5fa3",
            "secondary": "#f9943b"
        },
        "typography": {
            "headingFont": "Inter",
            "bodyFont": "Inter"
        }
    }
    
    test_post_endpoint(f"{base_url}/api/branding", branding_data, "Branding API POST")
    
    # Test site setup API
    site_data = {
        "siteName": "Test Site",
        "siteDescription": "A test website",
        "githubUsername": "testuser",
        "githubRepo": "test-repo"
    }
    
    test_post_endpoint(f"{base_url}/api/site-setup", site_data, "Site Setup API POST")

def main():
    print("🔧 ForgeWeb Advanced Functionality Tests")
    print("=" * 50)
    
    test_file_operations()
    test_api_functionality()
    
    print("\n" + "=" * 50)
    print("✅ Advanced ForgeWeb Tests Complete!")

if __name__ == "__main__":
    main()