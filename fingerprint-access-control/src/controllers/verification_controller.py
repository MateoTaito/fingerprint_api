from flask import Blueprint, request, jsonify, current_app
from services.user_service import UserService
from services.fingerprint_service import FingerprintService

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('', methods=['POST'])
def verify_fingerprint():
    """Verify fingerprint and identify user"""
    try:
        data = request.get_json()
        finger = data.get('finger') if data else None
        
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Get all users from our database
        users = user_service.list_users()
        
        if not users:
            return jsonify({
                'message': 'No users registered in the system',
                'verified': False,
                'access_granted': False
            }), 404
        
        # Try to verify fingerprint against each user
        for user in users:
            try:
                print(f"🔍 Trying to verify fingerprint for user: {user.username}")
                success = fingerprint_service.verify_fingerprint(user.username, finger)
                
                if success:
                    return jsonify({
                        'message': f'Fingerprint verification successful for user {user.username}',
                        'verified': True,
                        'user': {
                            'id': user.id,
                            'username': user.username
                        },
                        'access_granted': True
                    }), 200
                    
            except Exception as e:
                print(f"⚠️ Error verifying user {user.username}: {e}")
                continue
        
        # If no user matched
        return jsonify({
            'message': 'Fingerprint verification failed - no matching user found',
            'verified': False,
            'access_granted': False
        }), 401
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@verification_bp.route('/<username>', methods=['POST'])
def verify_user_fingerprint(username):
    """Verify fingerprint for a specific user"""
    try:
        data = request.get_json()
        finger = data.get('finger') if data else None
        
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Check if user exists
        user = user_service.get_user(username)
        
        # Verify fingerprint for this specific user
        success = fingerprint_service.verify_fingerprint(username, finger)
        
        if success:
            return jsonify({
                'message': f'Fingerprint verification successful for user {username}',
                'verified': True,
                'user': {
                    'id': user.id,
                    'username': user.username
                },
                'access_granted': True
            }), 200
        else:
            return jsonify({
                'message': f'Fingerprint verification failed for user {username}',
                'verified': False,
                'access_granted': False
            }), 401
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@verification_bp.route('/simulate', methods=['POST'])
def simulate_verification():
    """Simulate fingerprint verification (for testing purposes)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        username = data.get('username')
        success = data.get('success', True)  # Default to successful verification
        
        if not username:
            return jsonify({'error': 'Username is required for simulation'}), 400
        
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        
        # Check if user exists
        user = user_service.get_user(username)
        
        if success:
            return jsonify({
                'message': f'Simulated fingerprint verification successful for user {username}',
                'verified': True,
                'user': {
                    'id': user.id,
                    'username': user.username
                },
                'access_granted': True,
                'simulated': True
            }), 200
        else:
            return jsonify({
                'message': f'Simulated fingerprint verification failed for user {username}',
                'verified': False,
                'access_granted': False,
                'simulated': True
            }), 401
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500