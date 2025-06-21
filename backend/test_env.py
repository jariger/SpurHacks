#!/usr/bin/env python3
"""
Test script to check .env file loading
"""

import os
from dotenv import load_dotenv

def test_env():
    print("=== Environment Variable Test ===")
    
    # Check current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if .env file exists
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ .env file found at: {os.path.abspath(env_file)}")
        
        # Read and display .env file contents (without showing the actual API key)
        with open(env_file, 'r') as f:
            content = f.read()
            print(f"📄 .env file contents:")
            for line in content.split('\n'):
                if line.strip() and not line.startswith('#'):
                    key = line.split('=')[0]
                    print(f"  {key}=***")
    else:
        print(f"❌ .env file not found at: {os.path.abspath(env_file)}")
    
    # Try to load .env
    print(f"\n🔄 Loading .env file...")
    load_result = load_dotenv()
    print(f"load_dotenv() returned: {load_result}")
    
    # Check if environment variables are loaded
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    debug = os.getenv('DEBUG')
    
    print(f"\n📊 Environment variables:")
    print(f"  GOOGLE_MAPS_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    print(f"  DEBUG: {debug}")
    
    if api_key:
        print(f"  API Key length: {len(api_key)} characters")
        print(f"  API Key starts with: {api_key[:10]}...")

if __name__ == "__main__":
    test_env() 