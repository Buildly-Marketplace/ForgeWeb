#!/usr/bin/env python3
"""
ForgeWeb High-Level Functionality Test
Tests all major components and endpoints
"""

import requests
import json
import sys

def test_endpoint(url, name, expected_status=200):
    try:
        response = requests.get(url, timeout=10)
        status = "✅" if response.status_code == expected_status else "❌"
        print(f"{status} {name}: Status {response.status_code}")
        
        # Show content type and size
        content_type = response.headers.get('content-type', 'unknown')
        content_length = len(response.content)
        print(f"    Content-Type: {content_type}")
        print(f"    Size: {content_length} bytes")
        
        # If JSON, show structure
        if 'application/json' in content_type:
            try:
                data = response.json()
                print(f"    JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'Array/Other'}")
            except:
                print(f"    JSON: Invalid")
        
        return response.status_code == expected_status
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection refused (server not running)")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False

def main():
    print("🧪 ForgeWeb High-Level Functionality Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test all major endpoints
    print("\n1. MAIN WEBSITE TESTS")
    test_endpoint(f"{base_url}/", "Main Website")
    test_endpoint(f"{base_url}/assets/css/custom.css", "Custom CSS")
    
    print("\n2. ADMIN INTERFACE TESTS")  
    test_endpoint(f"{base_url}/admin/", "Admin Dashboard")
    test_endpoint(f"{base_url}/admin/css/admin.css", "Admin CSS")
    test_endpoint(f"{base_url}/admin/js/app.js", "Admin JavaScript")
    test_endpoint(f"{base_url}/admin/includes/nav.html", "Navigation Include")
    
    print("\n3. ADMIN PAGES TESTS")
    test_endpoint(f"{base_url}/admin/site-setup.html", "Site Setup Wizard")
    test_endpoint(f"{base_url}/admin/branding-manager.html", "Branding Manager")
    test_endpoint(f"{base_url}/admin/html-import.html", "HTML Import Tool")
    test_endpoint(f"{base_url}/admin/page-editor.html", "Page Editor")
    test_endpoint(f"{base_url}/admin/articles-manager.html", "Articles Manager")
    test_endpoint(f"{base_url}/admin/navigation-manager.html", "Navigation Manager")
    test_endpoint(f"{base_url}/admin/settings.html", "Settings Page")
    test_endpoint(f"{base_url}/admin/social.html", "Social Media Manager")
    
    print("\n4. API ENDPOINT TESTS")
    test_endpoint(f"{base_url}/api/branding", "Branding API")
    
    print("\n5. TEMPLATE TESTS")
    test_endpoint(f"{base_url}/templates/base.html", "Base Template")
    
    print("\n6. 404 TESTS")
    test_endpoint(f"{base_url}/nonexistent", "404 Test", 404)
    
    print("\n" + "=" * 50)
    print("✅ ForgeWeb Functionality Test Complete!")

if __name__ == "__main__":
    main()