#!/usr/bin/env python3
"""
ForgeWeb Development Environment Tests
Tests virtual environment, dependencies, and development tools
"""

import sys
import os
import subprocess

def test_python_environment():
    print("🐍 PYTHON ENVIRONMENT TESTS")
    print("-" * 30)
    
    # Check Python version
    python_version = sys.version
    print(f"✅ Python Version: {python_version.split()[0]}")
    
    # Check virtual environment
    venv_path = sys.prefix
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    status = "✅" if in_venv else "❌"
    print(f"{status} Virtual Environment: {in_venv}")
    print(f"    Path: {venv_path}")

def test_dependencies():
    print("\n📦 DEPENDENCY TESTS")
    print("-" * 20)
    
    required_packages = [
        'python-dotenv',
        'requests', 
        'Pillow'
    ]
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: Missing")

def test_environment_variables():
    print("\n🔧 ENVIRONMENT TESTS")
    print("-" * 20)
    
    # Check .env file exists
    env_file = "/Users/greglind/Projects/buildly/THE FORGE/ForgeWeb/.env"
    env_example = "/Users/greglind/Projects/buildly/THE FORGE/ForgeWeb/.env.example"
    
    env_exists = os.path.exists(env_file)
    example_exists = os.path.exists(env_example)
    
    print(f"✅ .env.example: {'Found' if example_exists else 'Missing'}")
    print(f"{'✅' if env_exists else '⚠️'} .env: {'Found' if env_exists else 'Missing (will be created on first run)'}")

def test_buildly_compliance():
    print("\n🏢 BUILDLY MARKETPLACE TESTS")
    print("-" * 30)
    
    # Check BUILDLY.yaml
    buildly_file = "/Users/greglind/Projects/buildly/THE FORGE/ForgeWeb/BUILDLY.yaml"
    if os.path.exists(buildly_file):
        print("✅ BUILDLY.yaml: Found")
        try:
            with open(buildly_file, 'r') as f:
                content = f.read()
                if 'name: ForgeWeb' in content:
                    print("✅ App Name: Configured")
                if 'license: BSL-1.1' in content:
                    print("✅ License: BSL-1.1")
                if 'category: website-builders' in content:
                    print("✅ Category: website-builders")
        except:
            print("❌ BUILDLY.yaml: Error reading file")
    else:
        print("❌ BUILDLY.yaml: Missing")

def test_deployment_config():
    print("\n🚀 DEPLOYMENT TESTS")
    print("-" * 20)
    
    deployment_files = [
        ("ops/Dockerfile", "Docker"),
        ("ops/kubernetes.yaml", "Kubernetes"),
        ("ops/docker-compose.yml", "Docker Compose"),
        ("ci/github-pages-deploy.yml", "GitHub Actions")
    ]
    
    for file_path, description in deployment_files:
        full_path = f"/Users/greglind/Projects/buildly/THE FORGE/ForgeWeb/{file_path}"
        exists = os.path.exists(full_path)
        status = "✅" if exists else "❌"
        print(f"{status} {description}: {'Configured' if exists else 'Missing'}")

def main():
    print("🧪 ForgeWeb Development Environment Test")
    print("=" * 50)
    
    test_python_environment()
    test_dependencies() 
    test_environment_variables()
    test_buildly_compliance()
    test_deployment_config()
    
    print("\n" + "=" * 50)
    print("✅ Development Environment Test Complete!")

if __name__ == "__main__":
    main()