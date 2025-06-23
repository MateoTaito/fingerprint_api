from flask import Blueprint, request, jsonify, current_app
from services.user_service import UserService
from services.fingerprint_service import FingerprintService

enrollment_bp = Blueprint('enrollment', __name__)

@enrollment_bp.route('/<username>', methods=['POST'])
def enroll_fingerprint(username):
    """Enroll a fingerprint for an existing user"""
    try:
        data = request.get_json()
        finger = data.get('finger', 'right-index-finger') if data else 'right-index-finger'
        label = data.get('label') if data else None
        
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Check if user exists
        user = user_service.get_user(username)
        
        # Simulate fingerprint enrollment
        success = fingerprint_service.enroll_fingerprint(username, finger, label)
        
        if success:
            return jsonify({
                'message': f'Fingerprint enrolled successfully for user {username}',
                'user': {
                    'id': user.id,
                    'username': user.username
                },
                'fingerprint': {
                    'finger': finger,
                    'label': label
                }
            }), 201
        else:
            return jsonify({
                'error': 'Fingerprint enrollment failed'
            }), 500
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@enrollment_bp.route('/user', methods=['POST'])
def enroll_new_user():
    """Create a new user and enroll their first fingerprint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        finger = data.get('finger', 'right-index-finger')
        label = data.get('label')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Create new user
        user = user_service.register_user(username, password)
        
        # Enroll fingerprint
        success = fingerprint_service.enroll_fingerprint(username, finger, label)
        
        if success:
            return jsonify({
                'message': f'User {username} created and fingerprint enrolled successfully',
                'user': {
                    'id': user.id,
                    'username': user.username
                },
                'fingerprint': {
                    'finger': finger,
                    'label': label
                }
            }), 201
        else:
            return jsonify({
                'message': f'User {username} created but fingerprint enrollment failed',
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            }), 201
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@enrollment_bp.route('/<username>/fingers', methods=['GET'])
def get_enrolled_fingers(username):
    """Get list of enrolled fingers for a user"""
    try:
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Check if user exists
        user = user_service.get_user(username)
        
        # Get enrolled fingers
        enrolled_fingers = fingerprint_service.get_enrolled_fingers(username)
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username
            },
            'enrolled_fingers': enrolled_fingers,
            'count': len(enrolled_fingers)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@enrollment_bp.route('/<username>/<finger>', methods=['DELETE'])
def delete_fingerprint(username, finger):
    """Delete a specific fingerprint for a user"""
    try:
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Check if user exists
        user = user_service.get_user(username)
        
        # Delete the specific fingerprint
        success = fingerprint_service.delete_enrolled_finger(username, finger)
        
        if success:
            return jsonify({
                'message': f'Fingerprint {finger} deleted successfully for user {username}',
                'user': {
                    'id': user.id,
                    'username': user.username
                },
                'deleted_finger': finger
            }), 200
        else:
            return jsonify({
                'error': f'Failed to delete fingerprint {finger} for user {username}'
            }), 500
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@enrollment_bp.route('/<username>/all', methods=['DELETE'])
def delete_all_fingerprints(username):
    """Delete all fingerprints for a user"""
    try:
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Check if user exists
        user = user_service.get_user(username)
        
        # Delete all fingerprints
        success = fingerprint_service.delete_all_user_fingerprints(username)
        
        if success:
            return jsonify({
                'message': f'All fingerprints deleted successfully for user {username}',
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            }), 200
        else:
            return jsonify({
                'error': f'Failed to delete all fingerprints for user {username}'
            }), 500
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500