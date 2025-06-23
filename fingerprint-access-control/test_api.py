#!/usr/bin/env python3
"""
Test script for the Fingerprint Access Control API
Run this after starting the API server to test basic functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_create_user():
    """Test creating a new user"""
    print("\n👤 Testing user creation...")
    user_data = {
        "username": "test_user",
        "password": "test_password"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/users", json=user_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return False

def test_list_users():
    """Test listing users"""
    print("\n📋 Testing user listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/users")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ User listing failed: {e}")
        return False

def test_get_user():
    """Test getting specific user"""
    print("\n🔍 Testing get specific user...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/test_user")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get user failed: {e}")
        return False

def test_enroll_fingerprint():
    """Test fingerprint enrollment"""
    print("\n👆 Testing fingerprint enrollment...")
    enrollment_data = {
        "finger": "right-index-finger",
        "label": "Test fingerprint"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/enrollment/test_user", json=enrollment_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Fingerprint enrollment failed: {e}")
        return False

def test_verification_simulation():
    """Test simulated fingerprint verification"""
    print("\n🔒 Testing simulated verification...")
    verification_data = {
        "username": "test_user",
        "success": True
    }
    try:
        response = requests.post(f"{BASE_URL}/api/verification/simulate", json=verification_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Verification simulation failed: {e}")
        return False

def test_delete_user():
    """Test user deletion"""
    print("\n🗑️ Testing user deletion...")
    try:
        response = requests.delete(f"{BASE_URL}/api/users/test_user")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ User deletion failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Fingerprint Access Control API Tests\n")
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    tests = [
        ("Health Check", test_health_check),
        ("Create User", test_create_user),
        ("List Users", test_list_users),
        ("Get User", test_get_user),
        ("Enroll Fingerprint", test_enroll_fingerprint),
        ("Verification Simulation", test_verification_simulation),
        ("Delete User", test_delete_user),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        result = test_func()
        if result:
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the API server and logs.")

if __name__ == "__main__":
    main()
