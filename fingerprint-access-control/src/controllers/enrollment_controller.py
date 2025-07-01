from flask import Blueprint, request, jsonify, current_app
from services.user_service import UserService
from services.fingerprint_service import FingerprintService
from models.fingerprint import Fingerprint

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
        
        # Check if finger is already enrolled for this user
        enrolled_fingers = fingerprint_service.get_enrolled_fingers(username)
        if finger in enrolled_fingers:
            return jsonify({
                'error': f'Finger {finger} is already enrolled for user {username}',
                'enrolled_fingers': enrolled_fingers,
                'suggestion': 'Try a different finger or delete the existing enrollment first'
            }), 409  # Conflict status code
        
        # Simulate fingerprint enrollment
        success = fingerprint_service.enroll_fingerprint(username, finger, label)
        
        if success:
            # Create fingerprint record in database
            try:
                db_service = current_app.db_service
                fingerprint_record = Fingerprint(
                    user_id=user.id,
                    finger=finger,
                    label=label
                )
                db_service.add_fingerprint(fingerprint_record)
                print(f"✅ Created fingerprint record in database: User {user.id}, Finger {finger}")
            except Exception as e:
                print(f"⚠️ Warning: Could not create fingerprint record in database: {e}")
            
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
            # Create fingerprint record in database
            try:
                fingerprint_record = Fingerprint(
                    user_id=user.id,
                    finger=finger,
                    label=label
                )
                db_service.add_fingerprint(fingerprint_record)
                print(f"✅ Created fingerprint record in database: User {user.id}, Finger {finger}")
            except Exception as e:
                print(f"⚠️ Warning: Could not create fingerprint record in database: {e}")
            
            return jsonify({
                'message_inter': f'User {username} created and fingerprint enrolled successfully',
                'user': {
                    'id': user.id,
                    'username': user.username
                },
                'fingerprint': {
                    'finger': finger,
                    'label': label
                },
                'success': True,
                'message':'Fingerprint enrolled successfully',
                'enrollmentId': user.username,
                'templateData': 'base64_encoded_template',
            }), 201
        else:
            return jsonify({
                'message_inter': f'User {username} created but fingerprint enrollment failed',
                'user': {
                    'id': user.id,
                    'username': user.username
                },
                'success': False,
                'message': "Fingerprint enrollment failed",
                'error': "Scanner not connected"
            }), 201
            
    except ValueError as e:
        return jsonify({'error': str(e),'success': False,
                'message': "Fingerprint enrollment failed",
                'error': "Scanner not connected"}), 409
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}','success': False,
                'message': "Fingerprint enrollment failed",
                'error': "Scanner not connected"}), 500

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
            # Delete fingerprint record from database
            try:
                fingerprints = db_service.get_fingerprints_by_user(user.id)
                for fp in fingerprints:
                    if fp.finger == finger:
                        db_service.delete_fingerprint(fp)
                        print(f"✅ Deleted fingerprint record from database: User {user.id}, Finger {finger}")
                        break
            except Exception as e:
                print(f"⚠️ Warning: Could not delete fingerprint record from database: {e}")
            
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
            # Delete all fingerprint records from database
            try:
                fingerprints = db_service.get_fingerprints_by_user(user.id)
                for fp in fingerprints:
                    db_service.delete_fingerprint(fp)
                print(f"✅ Deleted {len(fingerprints)} fingerprint records from database for user {user.id}")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete fingerprint records from database: {e}")
            
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

@enrollment_bp.route('/system/status', methods=['GET'])
def get_system_fingerprint_status():
    """Get comprehensive fingerprint enrollment status for the entire system"""
    try:
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Get all users from database
        users = user_service.list_users()
        
        system_status = {
            'total_users': len(users),
            'users_with_fingerprints': 0,
            'total_enrolled_fingerprints': 0,
            'users': [],
            'system_summary': {}
        }
        
        finger_distribution = {}
        
        for user in users:
            enrolled_fingers = fingerprint_service.get_enrolled_fingers(user.username)
            
            user_info = {
                'id': user.id,
                'username': user.username,
                'enrolled_fingers': [],
                'fingerprints_count': len(enrolled_fingers)
            }
            
            if enrolled_fingers:
                system_status['users_with_fingerprints'] += 1
                system_status['total_enrolled_fingerprints'] += len(enrolled_fingers)
                
                for finger in enrolled_fingers:
                    label = fingerprint_service.get_fingerprint_label(user.username, finger)
                    user_info['enrolled_fingers'].append({
                        'finger': finger,
                        'label': label or 'No label'
                    })
                    
                    # Count finger distribution
                    finger_distribution[finger] = finger_distribution.get(finger, 0) + 1
            
            system_status['users'].append(user_info)
        
        # Add system summary
        system_status['system_summary'] = {
            'enrollment_percentage': round((system_status['users_with_fingerprints'] / max(system_status['total_users'], 1)) * 100, 2),
            'average_fingerprints_per_user': round(system_status['total_enrolled_fingerprints'] / max(system_status['users_with_fingerprints'], 1), 2) if system_status['users_with_fingerprints'] > 0 else 0,
            'most_used_fingers': sorted(finger_distribution.items(), key=lambda x: x[1], reverse=True)[:3],
            'finger_distribution': finger_distribution
        }
        
        return jsonify(system_status), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@enrollment_bp.route('/search/<finger>', methods=['GET'])
def search_fingerprint_by_finger(finger):
    """Search which users have enrolled a specific finger"""
    try:
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Get all users from database
        users = user_service.list_users()
        
        users_with_finger = []
        
        for user in users:
            enrolled_fingers = fingerprint_service.get_enrolled_fingers(user.username)
            
            if finger in enrolled_fingers:
                label = fingerprint_service.get_fingerprint_label(user.username, finger)
                users_with_finger.append({
                    'id': user.id,
                    'username': user.username,
                    'finger': finger,
                    'label': label or 'No label'
                })
        
        return jsonify({
            'finger': finger,
            'users_count': len(users_with_finger),
            'users': users_with_finger,
            'message': f'Found {len(users_with_finger)} users with {finger} enrolled'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@enrollment_bp.route('/analytics', methods=['GET'])
def get_fingerprint_analytics():
    """Get advanced analytics about fingerprint usage patterns"""
    try:
        # Get db_service from app context
        db_service = current_app.db_service
        user_service = UserService(db_service)
        fingerprint_service = FingerprintService()
        
        # Get all users from database
        users = user_service.list_users()
        
        analytics = {
            'finger_popularity': {},
            'label_usage': {},
            'user_patterns': {
                'single_finger_users': 0,
                'multi_finger_users': 0,
                'no_finger_users': 0
            },
            'recommendations': [],
            'security_insights': {}
        }
        
        total_fingerprints = 0
        users_with_labels = 0
        fingerprints_with_labels = 0
        
        available_fingers = fingerprint_service.get_available_fingers()
        
        # Initialize finger popularity
        for finger in available_fingers:
            analytics['finger_popularity'][finger] = 0
        
        for user in users:
            enrolled_fingers = fingerprint_service.get_enrolled_fingers(user.username)
            user_has_labels = False
            
            if len(enrolled_fingers) == 0:
                analytics['user_patterns']['no_finger_users'] += 1
            elif len(enrolled_fingers) == 1:
                analytics['user_patterns']['single_finger_users'] += 1
            else:
                analytics['user_patterns']['multi_finger_users'] += 1
            
            for finger in enrolled_fingers:
                total_fingerprints += 1
                analytics['finger_popularity'][finger] += 1
                
                label = fingerprint_service.get_fingerprint_label(user.username, finger)
                if label:
                    fingerprints_with_labels += 1
                    user_has_labels = True
                    
                    # Count label usage
                    if label in analytics['label_usage']:
                        analytics['label_usage'][label] += 1
                    else:
                        analytics['label_usage'][label] = 1
            
            if user_has_labels:
                users_with_labels += 1
        
        # Generate recommendations
        recommendations = []
        
        # Security recommendations
        if analytics['user_patterns']['single_finger_users'] > analytics['user_patterns']['multi_finger_users']:
            recommendations.append({
                'type': 'security',
                'priority': 'high',
                'message': 'Consider enrolling backup fingers for users with only one fingerprint',
                'impact': 'Improves system reliability and reduces lockout risk'
            })
        
        # Usability recommendations
        if users_with_labels < len(users) * 0.5:
            recommendations.append({
                'type': 'usability',
                'priority': 'medium',
                'message': 'Encourage users to add labels to their fingerprints for better identification',
                'impact': 'Improves user experience and fingerprint management'
            })
        
        # Most/least popular fingers
        sorted_fingers = sorted(analytics['finger_popularity'].items(), key=lambda x: x[1], reverse=True)
        most_popular = sorted_fingers[0] if sorted_fingers else None
        least_popular = [f for f, count in sorted_fingers if count == 0]
        
        if most_popular and most_popular[1] > 0:
            recommendations.append({
                'type': 'insight',
                'priority': 'low',
                'message': f'Most popular finger: {most_popular[0]} ({most_popular[1]} users)',
                'impact': 'Usage pattern insight'
            })
        
        analytics['recommendations'] = recommendations
        
        # Security insights
        analytics['security_insights'] = {
            'total_fingerprints': total_fingerprints,
            'backup_coverage': round((analytics['user_patterns']['multi_finger_users'] / max(len(users), 1)) * 100, 2),
            'label_coverage': round((fingerprints_with_labels / max(total_fingerprints, 1)) * 100, 2),
            'enrollment_rate': round(((len(users) - analytics['user_patterns']['no_finger_users']) / max(len(users), 1)) * 100, 2)
        }
        
        # Sort results
        analytics['finger_popularity'] = dict(sorted(analytics['finger_popularity'].items(), key=lambda x: x[1], reverse=True))
        analytics['label_usage'] = dict(sorted(analytics['label_usage'].items(), key=lambda x: x[1], reverse=True))
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500