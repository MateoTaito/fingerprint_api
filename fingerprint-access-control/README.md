# Fingerprint Access Control System

This project is a fingerprint access control system designed to manage user access through fingerprint verification. It allows for the enrollment of multiple users and their fingerprints, and provides functionality for verifying users based on their fingerprints.

## Project Structure

The project is organized into several directories and files:

- **src/**: Contains the main application code.
  - **main.py**: Entry point of the application.
  - **models/**: Contains the data models for users, fingerprints, and access logs.
  - **services/**: Contains service classes for handling business logic related to fingerprints, users, and database operations.
  - **controllers/**: Contains controller classes that manage the flow of data between the models and views.
  - **utils/**: Contains utility functions and configuration settings.
  - **database/**: Contains database-related files, including migrations and models.

- **config/**: Contains configuration files for the application.
  - **config.yaml**: YAML configuration settings.
  - **database.conf**: Database configuration settings.

- **data/**: Contains the SQLite database file.
  - **access_control.db**: Database file that stores user and fingerprint data.

- **logs/**: Contains log files for access attempts.
  - **access.log**: Log file for recording access attempts and related information.

- **requirements.txt**: Lists the dependencies required for the project.

- **setup.py**: Used for packaging and installing the application.

- **README.md**: Documentation for the project.

## Features

- **User Enrollment**: Allows for the registration of new users and their fingerprints.
- **Fingerprint Verification**: Enables users to verify their identity using their fingerprints.
- **Access Logging**: Records access attempts and their outcomes for auditing purposes.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fingerprint-access-control
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   - Run the SQL migration scripts located in `src/database/migrations/create_tables.sql` to create the necessary tables.

4. Configure the application settings in `config/config.yaml` and `config/database.conf` as needed.

## Usage

To start the application, run:
```
python src/main.py
```

Follow the prompts to enroll users and verify fingerprints.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.