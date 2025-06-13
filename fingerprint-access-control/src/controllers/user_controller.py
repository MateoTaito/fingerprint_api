from flask import Blueprint, request, jsonify
from models.user import User
from services.user_service import UserService
from services.fingerprint_service import FingerprintService
import pwd

user_controller = Blueprint('user_controller', __name__)

@user_controller.route('/users', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User(username=username, password=password)
    result = UserService().register_user(user)
    
    if result:
        return jsonify({'message': 'User created successfully'}), 201
    else:
        return jsonify({'error': 'User already exists'}), 409

@user_controller.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = UserService().get_user_by_username(username)
    
    if user:
        return jsonify({'username': user.username, 'fingerprints': user.fingerprints}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@user_controller.route('/users/<username>', methods=['DELETE'])
def delete_user(username):
    result = UserService().delete_user(username)
    
    if result:
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@user_controller.route('/users', methods=['GET'])
def list_users():
    users = UserService().get_all_users()
    return jsonify(users), 200

class UserController:
    def __init__(self, db_service):
        self.db_service = db_service
        self.user_service = UserService(db_service)
        self.fingerprint_service = FingerprintService()

    def list_users(self):
        try:
            users = self.user_service.list_users()
            print("\n=== Registered Users ===")
            if not users:
                print("No users registered yet.")
            else:
                for user in users:
                    enrolled_fingers = self.fingerprint_service.get_enrolled_fingers(user.username)
                    flag = "[✔]" if enrolled_fingers else "[ ]"
                    if enrolled_fingers:
                        print(f"- {user.username} {flag} [fprintd] (/var/lib/fprint/)")
                        print(f"    Dedos enrolados: {', '.join(enrolled_fingers)}")
                    else:
                        print(f"- {user.username} {flag}")
        except Exception as e:
            print(f"Error listing users: {e}")

    def delete_user(self, username):
        try:
            self.user_service.delete_user(username)
            print(f"User '{username}' deleted successfully!")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_user_info(self, username):
        try:
            user = self.user_service.get_user(username)
            print(f"\n=== User Information ===")
            print(f"Username: {user.username}")
            # Add more user details as needed
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def identify_user_by_fingerprint(self):
        print("\n=== Identificación biométrica (simulada) ===")
        username = self.fingerprint_service.identify_user_by_fingerprint()
        if username:
            print(f"Usuario identificado: {username}")
            return username
        else:
            print("No se pudo identificar al usuario por huella.")
            return None
    
    def verify_fingerprint(self, username, finger=None):
        """Verify fingerprint for a user (simulated or real)"""
        try:
            return self.fingerprint_service.verify_fingerprint(username, finger)
        except Exception as e:
            print(f"Verification error: {e}")
            return False