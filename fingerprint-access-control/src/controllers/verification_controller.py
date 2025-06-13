from flask import request, jsonify
from services.user_service import UserService
from services.fingerprint_service import FingerprintService

class VerificationController:
    def __init__(self, db_service):
        self.db_service = db_service
        self.user_service = UserService(db_service)
        self.fingerprint_service = FingerprintService()

    def verify_user(self):
        print("\n=== User Verification ===")
        print("Please place your finger on the scanner...")
        
        try:
            # Here you would integrate with actual fingerprint hardware
            # For now, simulate by asking for username
            username = input("Enter username to simulate verification: ")
            user = self.user_service.get_user(username)
            
            print(f"Access granted for user: {username}")
            return True
            
        except ValueError as e:
            print(f"Access denied: {e}")
            return False
        except Exception as e:
            print(f"Verification error: {e}")
            return False