#!/usr/bin/env python3
"""
Test ForgeWeb API Endpoints
"""

import requests
import json
import sys

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing ForgeWeb API Endpoints...")
    
    # Test 1: Site Status
    try:
        response = requests.get(f"{base_url}/api/site-status")
        print(f"✓ Site Status: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"✗ Site Status failed: {e}")
    
    # Test 2: Preview URL
    try:
        response = requests.get(f"{base_url}/api/preview-url")
        print(f"✓ Preview URL: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"✗ Preview URL failed: {e}")
    
    # Test 3: Setup Site (config update)
    try:
        test_data = {
            "action": "update-config",
            "data": {
                "siteName": "Test Site",
                "siteDescription": "A test website",
                "siteAuthor": "Test Author",
                "githubUsername": "testuser",
                "githubRepo": "testsite",
                "siteType": "blog",
                "includeAbout": True,
                "includeContact": True,
                "includeBlog": True,
                "includePortfolio": False,
                "includeServices": False,
                "includeSampleContent": True
            }
        }
        
        response = requests.post(
            f"{base_url}/api/setup-site",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"✓ Setup Site Config: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"✗ Setup Site Config failed: {e}")
    
    # Test 4: Generate Site Files
    try:
        test_data = {
            "action": "generate-site",
            "data": {
                "siteName": "Test Site",
                "siteDescription": "A test website",
                "siteAuthor": "Test Author",
                "githubUsername": "testuser",
                "githubRepo": "testsite",
                "includeAbout": True,
                "includeContact": True
            }
        }
        
        response = requests.post(
            f"{base_url}/api/setup-site",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"✓ Generate Site: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"✗ Generate Site failed: {e}")
    
    print("\n🎉 API testing complete!")

if __name__ == '__main__':
    try:
        test_api()
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")
    except Exception as e:
        print(f"❌ Test error: {e}")
        sys.exit(1)