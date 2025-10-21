#!/usr/bin/env python3
"""
ForgeWeb Enhancement Verification Test
Tests all the enhancements we just implemented
"""

import requests
import json
import os
from datetime import datetime

def test_enhancement(name, test_func):
    """Run a test and report results"""
    print(f"\n🧪 Testing: {name}")
    try:
        result = test_func()
        if result:
            print(f"✅ PASSED: {name}")
            return True
        else:
            print(f"❌ FAILED: {name}")
            return False
    except Exception as e:
        print(f"❌ ERROR in {name}: {str(e)}")
        return False

def test_site_setup_api():
    """Test the enhanced site-setup API endpoint"""
    url = "http://localhost:8000/api/site-setup"
    data = {
        "siteName": "Test Enhancement Site",
        "siteDescription": "Testing enhanced site setup API",
        "githubUsername": "testuser",
        "githubRepo": "test-enhancement-repo"
    }
    
    response = requests.post(url, json=data, timeout=10)
    return response.status_code == 200

def test_setup_site_alternate():
    """Test the alternate setup-site endpoint"""
    url = "http://localhost:8000/api/setup-site"
    data = {
        "action": "update-config",
        "data": {
            "siteName": "Alternate API Test",
            "siteDescription": "Testing alternate endpoint"
        }
    }
    
    response = requests.post(url, json=data, timeout=10)
    return response.status_code == 200

def test_dependencies():
    """Test that all required dependencies are available"""
    try:
        import requests
        import json
        from dotenv import load_dotenv
        from PIL import Image
        return True
    except ImportError:
        return False

def test_buildly_head_js():
    """Test that buildly-head.js is accessible"""
    url = "http://localhost:8000/js/buildly-head.js"
    response = requests.get(url, timeout=10)
    return response.status_code == 200 and 'ForgeWeb' in response.text

def test_file_structure():
    """Test that all expected files exist"""
    base_path = "/Users/greglind/Projects/buildly/THE FORGE/ForgeWeb"
    required_files = [
        "js/buildly-head.js",
        "requirements.txt",
        ".env.example",
        "BUILDLY.yaml",
        "admin/file-api.py"
    ]
    
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if not os.path.exists(full_path):
            print(f"  Missing: {file_path}")
            return False
    return True

def test_site_generation():
    """Test the site generation functionality"""
    url = "http://localhost:8000/api/setup-site"
    data = {
        "action": "generate-site",
        "data": {
            "siteName": "Generated Test Site",
            "siteDescription": "Testing site generation",
            "includeAbout": True,
            "includeContact": True
        }
    }
    
    response = requests.post(url, json=data, timeout=10)
    if response.status_code == 200:
        result = response.json()
        return result.get('success', False)
    return False

def main():
    print("🔧 ForgeWeb Enhancement Verification")
    print("=" * 50)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all enhancement tests
    tests = [
        ("File Structure Complete", test_file_structure),
        ("Dependencies Available", test_dependencies),
        ("Buildly Head JS Accessible", test_buildly_head_js),
        ("Site Setup API (new endpoint)", test_site_setup_api),
        ("Setup Site API (original endpoint)", test_setup_site_alternate),
        ("Site Generation Functionality", test_site_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        results.append(test_enhancement(test_name, test_func))
    
    # Summary
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print("\n" + "=" * 50)
    print(f"📊 ENHANCEMENT TEST RESULTS")
    print(f"   Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("✅ All enhancements successfully implemented!")
    elif success_rate >= 70:
        print("⚠️  Most enhancements working, minor issues remain")
    else:
        print("❌ Major issues with enhancements")
    
    print(f"\n🎯 Enhancement Status: {'COMPLETE' if success_rate >= 90 else 'IN PROGRESS'}")

if __name__ == "__main__":
    main()