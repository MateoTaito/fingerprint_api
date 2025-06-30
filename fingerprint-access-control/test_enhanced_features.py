#!/usr/bin/env python3
"""
Test script for improved fingerprint enrollment and verification
Tests duplicate fingerprint handling and system status
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        return response.status_code == 200
    except:
        return False

def test_system_status():
    """Test the new system status endpoint"""
    print("📊 Testing System Status Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/enrollment/system/status")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            print(f"\n📈 System Summary:")
            print(f"   👥 Total users: {data.get('total_users')}")
            print(f"   🔐 Users with fingerprints: {data.get('users_with_fingerprints')}")
            print(f"   👆 Total fingerprints: {data.get('total_enrolled_fingerprints')}")
            
            summary = data.get('system_summary', {})
            print(f"   📊 Enrollment percentage: {summary.get('enrollment_percentage')}%")
            print(f"   📱 Avg fingerprints per user: {summary.get('average_fingerprints_per_user')}")
            
            if summary.get('most_used_fingers'):
                print(f"   🥇 Most used fingers:")
                for finger, count in summary.get('most_used_fingers', []):
                    print(f"      • {finger}: {count} users")
            
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_duplicate_enrollment():
    """Test duplicate fingerprint enrollment handling"""
    print("\n🔄 Testing Duplicate Enrollment Handling...")
    
    # First, let's see what users exist
    try:
        users_response = requests.get(f"{BASE_URL}/api/users")
        if users_response.status_code == 200:
            users = users_response.json().get('users', [])
            if users:
                username = users[0]['username']
                print(f"Testing with existing user: {username}")
                
                # Get current enrolled fingers
                fingers_response = requests.get(f"{BASE_URL}/api/enrollment/{username}/fingers")
                if fingers_response.status_code == 200:
                    enrolled_fingers = fingers_response.json().get('enrolled_fingers', [])
                    print(f"Current enrolled fingers: {enrolled_fingers}")
                    
                    if enrolled_fingers:
                        # Try to enroll an already enrolled finger
                        duplicate_finger = enrolled_fingers[0]
                        print(f"Attempting to enroll duplicate finger: {duplicate_finger}")
                        
                        enrollment_data = {
                            "finger": duplicate_finger,
                            "label": "Duplicate Test"
                        }
                        
                        response = requests.post(
                            f"{BASE_URL}/api/enrollment/{username}",
                            json=enrollment_data
                        )
                        
                        print(f"Duplicate enrollment status: {response.status_code}")
                        print(f"Response: {json.dumps(response.json(), indent=2)}")
                        
                        if response.status_code == 409:
                            print("✅ Duplicate handling working correctly (409 Conflict)")
                            return True
                        else:
                            print("⚠️ Expected 409 Conflict for duplicate")
                            return False
                    else:
                        print("No enrolled fingers found to test duplicate")
                        return True
                else:
                    print("Could not get enrolled fingers")
                    return False
            else:
                print("No users found to test with")
                return True
        else:
            print("Could not get users list")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_enhanced_verification():
    """Test enhanced verification with stats"""
    print("\n🔍 Testing Enhanced Verification...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/verification", json={})
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 401]:
            data = response.json()
            
            if 'verification_stats' in data:
                stats = data['verification_stats']
                print(f"\n📊 Verification Statistics:")
                print(f"   👥 Users checked: {stats.get('users_checked')}")
                print(f"   👆 Total fingerprints: {stats.get('total_fingerprints_in_system')}")
                
                if stats.get('message'):
                    print(f"   💬 Info: {stats.get('message')}")
                
                print("✅ Enhanced verification stats working")
                return True
            else:
                print("⚠️ No verification stats in response")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🚀 Testing Enhanced Fingerprint API Features")
    print("=" * 60)
    
    # Check if API is running
    if not test_health_check():
        print("❌ API is not running. Please start the API first.")
        print("Run: python3 src/main.py")
        return
    
    print("✅ API is running\n")
    
    # Run tests
    system_status_success = test_system_status()
    duplicate_handling_success = test_duplicate_enrollment()
    enhanced_verification_success = test_enhanced_verification()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"✅ System Status: {'PASSED' if system_status_success else 'FAILED'}")
    print(f"✅ Duplicate Handling: {'PASSED' if duplicate_handling_success else 'FAILED'}")
    print(f"✅ Enhanced Verification: {'PASSED' if enhanced_verification_success else 'FAILED'}")
    
    all_passed = all([system_status_success, duplicate_handling_success, enhanced_verification_success])
    
    if all_passed:
        print("\n🎉 All enhanced features are working correctly!")
        print("\nNew Features:")
        print("  🔄 Duplicate fingerprint detection")
        print("  📊 System status and statistics")
        print("  📈 Enhanced verification with stats")
        print("  🎯 Better error messages")
    else:
        print("\n⚠️ Some tests failed. Check the API server logs.")

if __name__ == "__main__":
    main()
