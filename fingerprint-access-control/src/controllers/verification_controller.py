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
        username = input("Enter username to verify: ")
        finger = input("Enter finger to verify (e.g. right-index-finger, leave blank to try any): ")
        try:
            user = self.user_service.get_user(username)
            print("Please place your finger on the scanner...")
            success = self.fingerprint_service.verify_fingerprint(username, finger if finger else None)
            if success:
                print(f"Access granted for user: {username}")
                return True
            else:
                print(f"Access denied for user: {username}")
                return False
        except ValueError as e:
            print(f"Access denied: {e}")
            return False
        except Exception as e:
            print(f"Verification error: {e}")
            return False