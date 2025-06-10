from pydantic import BaseModel

class User(BaseModel):
    id: str
    name: str
    email: str
    fingerprint_template: bytes  # Store the fingerprint template as bytes
    created_at: str  # Timestamp for when the user was created
    updated_at: str  # Timestamp for when the user was last updated