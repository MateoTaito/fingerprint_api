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
        finger = input("Enter finger to enroll (e.g. right-index-finger): ")
        label = input("Enter label for this fingerprint (optional): ")
        try:
            user = self.user_service.register_user(username, password)
            print(f"User '{username}' created successfully!")
            print("Please place your finger on the scanner...")
            success = self.fingerprint_service.enroll_fingerprint(username, finger, label if label else None)
            if success:
                print("Fingerprint enrolled and saved successfully!")
            else:
                print("Fingerprint enrollment failed!")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def enroll_fingerprint(self, username):
        print(f"\n=== Enrolling fingerprint for {username} ===")
        finger = input("Enter finger to enroll (e.g. right-index-finger): ")
        label = input("Enter label for this fingerprint (optional): ")
        try:
            user = self.user_service.get_user(username)
            print("Please place your finger on the scanner...")
            success = self.fingerprint_service.enroll_fingerprint(username, finger, label if label else None)
            if success:
                print("Additional fingerprint enrolled and saved successfully!")
            else:
                print("Fingerprint enrollment failed!")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_user(self):
        print("\n=== Delete User ===")
        username = input("Enter username to delete: ")
        try:
            # Eliminar usuario de la base de datos
            self.user_service.delete_user(username)
            # Eliminar huellas asociadas (si existen)
            enrolled_fingers = self.fingerprint_service.get_enrolled_fingers(username)
            for finger in enrolled_fingers:
                self.fingerprint_service.delete_enrolled_finger(username, finger)
            print(f"User '{username}' and associated fingerprints deleted successfully!")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")