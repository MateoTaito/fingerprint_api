from typing import Any, Dict
from .digitalpersona_driver import DigitalPersonaDriver

class FingerprintService:
    def __init__(self):
        self.driver = DigitalPersonaDriver()

    def enroll_fingerprint(self, user_id: str) -> Dict[str, Any]:
        fingerprint_data = self.driver.capture_fingerprint()
        # Logic to save fingerprint_data associated with user_id
        return {"message": "Fingerprint enrolled successfully", "user_id": user_id}

    def verify_fingerprint(self, fingerprint_data: bytes) -> Dict[str, Any]:
        user_id = self.driver.verify_fingerprint(fingerprint_data)
        if user_id:
            return {"match": True, "user_id": user_id}
        return {"match": False}