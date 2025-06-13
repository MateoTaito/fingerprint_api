def generate_unique_id():
    """Generate a unique identifier for users or fingerprints."""
    import uuid
    return str(uuid.uuid4())

def validate_username(username):
    """Validate the username format."""
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters long.")
    if not username.isalnum():
        raise ValueError("Username must be alphanumeric.")
    return True

def validate_fingerprint_data(fingerprint_data):
    """Validate the fingerprint data format."""
    if not fingerprint_data or len(fingerprint_data) < 128:
        raise ValueError("Fingerprint data is invalid or too short.")
    return True

def log_access_attempt(user, success):
    """Log access attempts to the access log."""
    from datetime import datetime
    log_entry = f"{datetime.now()}: User '{user}' access {'granted' if success else 'denied'}."
    with open('logs/access.log', 'a') as log_file:
        log_file.write(log_entry + "\n")

def load_config(config_file):
    """Load configuration settings from a YAML file."""
    import yaml
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def save_to_database(db_connection, query, params):
    """Execute a query to save data to the database."""
    cursor = db_connection.cursor()
    cursor.execute(query, params)
    db_connection.commit()
    return cursor.lastrowid

def fetch_from_database(db_connection, query, params):
    """Execute a query to fetch data from the database."""
    cursor = db_connection.cursor()
    cursor.execute(query, params)
    return cursor.fetchall()