# Entry point of the fingerprint access control API

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from services.database_service import DatabaseService
from controllers.enrollment_controller import enrollment_bp
from controllers.verification_controller import verification_bp
from controllers.user_controller import user_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fingerprint_access.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    
    # Initialize database
    db_url = "sqlite:///fingerprint_access.db"
    db_service = DatabaseService(db_url)
    db_service.create_tables()
    
    # Store db_service in app context for controllers to access
    app.db_service = db_service
    
    # Register blueprints
    app.register_blueprint(enrollment_bp, url_prefix='/api/enrollment')
    app.register_blueprint(verification_bp, url_prefix='/api/verification')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Fingerprint Access Control API is running'
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

def main():
    app = create_app()
    print("Starting Fingerprint Access Control API...")
    print("Available endpoints:")
    print("- GET  /api/health - Health check")
    print("- POST /api/users - Create user")
    print("- GET  /api/users - List all users")
    print("- GET  /api/users/{username} - Get specific user")
    print("- DELETE /api/users/{username} - Delete user")
    print("- POST /api/enrollment/{username} - Enroll fingerprint")
    print("- POST /api/verification - Verify fingerprint (identify any user)")
    print("- POST /api/verification/{username} - Verify fingerprint (specific user)")
    print("- DELETE /api/enrollment/{username}/{finger} - Delete specific fingerprint")
    print("- DELETE /api/enrollment/{username}/all - Delete all user fingerprints")
    print("\nAPI running on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()