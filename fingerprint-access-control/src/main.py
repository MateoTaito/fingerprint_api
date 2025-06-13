# Entry point of the fingerprint access control application

import sys
from services.database_service import DatabaseService
from controllers.enrollment_controller import EnrollmentController
from controllers.verification_controller import VerificationController
from controllers.user_controller import UserController

def main():
    # Initialize the database connection with SQLite database
    db_url = "sqlite:///fingerprint_access.db"
    db_service = DatabaseService(db_url)
    db_service.create_tables()

    # Initialize controllers
    enrollment_controller = EnrollmentController(db_service)
    verification_controller = VerificationController(db_service)
    user_controller = UserController(db_service)

    # Start the main application loop
    while True:
        print("\n=== Fingerprint Access Control System ===")
        print("1. Enroll User")
        print("2. Verify User")
        print("3. List Users")
        print("4. Delete User")
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            enrollment_controller.enroll_user()
        elif choice == "2":
            verification_controller.verify_user()
        elif choice == "3":
            user_controller.list_users()
        elif choice == "4":
            enrollment_controller.delete_user()
        elif choice == "5":
            print("Exiting the application...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()