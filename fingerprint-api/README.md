# Fingerprint API

This project is a FastAPI application designed to communicate with fingerprint readers using the `libfprint` library. It provides endpoints for enrolling new fingerprints and verifying existing ones, facilitating frontend validation.

## Features

- **Enroll Fingerprint**: Capture and store fingerprint templates.
- **Verify Fingerprint**: Compare captured fingerprints against stored templates.

## Project Structure

```
fingerprint-api
├── src
│   ├── main.py                # Entry point of the application
│   ├── api                    # API related files
│   │   ├── endpoints          # API endpoints for enrollment and verification
│   │   ├── dependencies.py     # Shared dependencies for the API
│   ├── core                   # Core application logic
│   ├── services               # Business logic and interactions with the fingerprint reader
│   ├── models                 # Data models for fingerprints and users
│   ├── database               # Database connection and migrations
│   └── utils                  # Utility functions and custom exceptions
├── tests                      # Unit tests for the application
├── requirements.txt           # Project dependencies
├── .env.example               # Example environment variables
├── docker-compose.yml         # Docker configurations
└── Dockerfile                 # Instructions for building the Docker image
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd fingerprint-api
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Copy `.env.example` to `.env` and update the values as needed.

4. **Run the application**:
   ```
   uvicorn src.main:app --reload
   ```

## Usage

- **Enroll a Fingerprint**:
  Send a POST request to `/fingerprints/enroll` with the necessary data to enroll a new fingerprint.

- **Verify a Fingerprint**:
  Send a POST request to `/fingerprints/verify` with the fingerprint data to verify against existing records.

## Testing

Run the tests using:
```
pytest
```

## License

This project is licensed under the MIT License.