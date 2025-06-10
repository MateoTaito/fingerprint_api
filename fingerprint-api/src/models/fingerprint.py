from pydantic import BaseModel

class Fingerprint(BaseModel):
    id: str
    user_id: str
    template: bytes
    created_at: str
    updated_at: str