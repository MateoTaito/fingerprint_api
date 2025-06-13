from flask import request, jsonify
from services.user_service import UserService
from services.fingerprint_service import FingerprintService

class EnrollmentController:
    def __init__(self, db_service):
        self.db_service = db_service
        self.user_service = UserService(db_service)
        self.fingerprint_service = FingerprintService()

    def enroll_user(self):
        print("\n=== User Enrollment ===")
        username = input("Enter username: ")
        password = input("Enter password: ")
        
        try:
            user = self.user_service.register_user(username, password)
            print(f"User '{username}' created successfully!")
            
            # Simulate fingerprint enrollment
            print("Please place your finger on the scanner...")
            # Here you would integrate with actual fingerprint hardware
            print("Fingerprint enrolled successfully!")
            
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def enroll_fingerprint(self, username):
        print(f"\n=== Enrolling fingerprint for {username} ===")
        try:
            user = self.user_service.get_user(username)
            print("Please place your finger on the scanner...")
            # Here you would integrate with actual fingerprint hardware
            print("Additional fingerprint enrolled successfully!")
            
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")