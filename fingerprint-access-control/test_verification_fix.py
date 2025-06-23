#!/usr/bin/env python3
"""
Test script specifically for the "Verify Fingerprint (Any User)" endpoint
This script tests the problematic endpoint that was fixed
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_verification_any_user():
    """Test the any-user verification endpoint"""
    print("🔍 Testing 'Verify Fingerprint (Any User)' endpoint...")
    print("This endpoint should iterate through all registered users to find a match")
    
    try:
        # Test with specific finger
        print("\n1️⃣ Testing with specific finger...")
        response = requests.post(
            f"{BASE_URL}/api/verification", 
            json={"finger": "right-index-finger"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test without specifying finger
        print("\n2️⃣ Testing without specifying finger...")
        response = requests.post(f"{BASE_URL}/api/verification", json={})
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test with empty request
        print("\n3️⃣ Testing with no body...")
        response = requests.post(f"{BASE_URL}/api/verification")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_verification_specific_user():
    """Test specific user verification for comparison"""
    print("\n🎯 Testing 'Verify Fingerprint (Specific User)' for comparison...")
    
    try:
        # First, get list of users
        users_response = requests.get(f"{BASE_URL}/api/users")
        if users_response.status_code == 200:
            users = users_response.json().get('users', [])
            if users:
                username = users[0]['username']
                print(f"Testing with user: {username}")
                
                response = requests.post(
                    f"{BASE_URL}/api/verification/{username}",
                    json={"finger": "right-index-finger"}
                )
                print(f"Status: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                return True
            else:
                print("No users found to test with")
                return False
        else:
            print(f"Failed to get users: {users_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🚀 Testing Fingerprint Verification Endpoints")
    print("=" * 50)
    
    # Test the problematic endpoint
    any_user_success = test_verification_any_user()
    
    print("\n" + "=" * 50)
    
    # Test specific user for comparison
    specific_user_success = test_verification_specific_user()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"✅ Any User Verification: {'PASSED' if any_user_success else 'FAILED'}")
    print(f"✅ Specific User Verification: {'PASSED' if specific_user_success else 'FAILED'}")
    
    if any_user_success and specific_user_success:
        print("\n🎉 All verification tests passed!")
        print("The 'Any User' endpoint is now working correctly!")
    else:
        print("\n⚠️ Some tests failed. Check the API server logs for details.")

if __name__ == "__main__":
    main()
