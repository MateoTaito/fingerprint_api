from flask import Blueprint, request, jsonify, current_app
from models.user import User
from services.user_service import UserService
from services.fingerprint_service import FingerprintService

user_bp = Blueprint('users', __name__)

@user_bp.route('', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        
        # Create new user
        user = user_service.register_user(username, password)
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@user_bp.route('/<username>', methods=['GET'])
def get_user(username):
    try:
        db_service = current_app.db_service
        user_service = UserService(db_service)
        
        user = user_service.get_user(username)
        
        # Safely access fingerprints
        try:
            fingerprints_count = len(user.fingerprints) if hasattr(user, 'fingerprints') and user.fingerprints is not None else 0
        except:
            fingerprints_count = 0
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'fingerprints_count': fingerprints_count
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@user_bp.route('/<username>', methods=['DELETE'])
def delete_user(username):
    try:
        db_service = current_app.db_service
        user_service = UserService(db_service)
        
        user_service.delete_user(username)
        
        return jsonify({'message': f'User {username} deleted successfully'}), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@user_bp.route('', methods=['GET'])
def list_users():
    try:
        db_service = current_app.db_service
        user_service = UserService(db_service)
        
        users = user_service.list_users()
        
        users_data = []
        for user in users:
            # Safely access fingerprints, defaulting to empty list if None or access fails
            try:
                fingerprints_count = len(user.fingerprints) if hasattr(user, 'fingerprints') and user.fingerprints is not None else 0
            except:
                fingerprints_count = 0
                
            users_data.append({
                'id': user.id,
                'username': user.username,
                'fingerprints_count': fingerprints_count
            })
        
        return jsonify({
            'users': users_data,
            'total': len(users_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@user_bp.route('/<username>/verify', methods=['POST'])
def verify_user_fingerprint(username):
    try:
        data = request.get_json()
        finger = data.get('finger') if data else None
        
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Check if user exists
        user = user_service.get_user(username)
        
        # Simulate fingerprint verification
        verification_result = fingerprint_service.verify_fingerprint(username, finger)
        
        if verification_result:
            return jsonify({
                'message': f'Fingerprint verification successful for user {username}',
                'verified': True,
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            }), 200
        else:
            return jsonify({
                'message': 'Fingerprint verification failed',
                'verified': False
            }), 401
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500