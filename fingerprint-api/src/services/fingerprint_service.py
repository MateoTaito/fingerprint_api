from typing import Any, Dict

from .digitalpersona_driver import DigitalPersonaDriver

class FingerprintService:
    def __init__(self) -> None:
        self.driver = DigitalPersonaDriver()

    def enroll_fingerprint(self, user_id: str) -> Dict[str, Any]:
        result = self.driver.enroll_fingerprint()
        if result.get("status") != "success":
            raise ValueError(result.get("message", "Enrollment failed"))
        fingerprint_data = result.get("data")
        # Logic to save fingerprint_data associated with user_id
        return {"message": "Fingerprint enrolled successfully", "user_id": user_id}

    def verify_fingerprint(self, fingerprint_data: bytes) -> Dict[str, Any]:
        result = self.driver.verify_fingerprint(fingerprint_data)
        if result.get("match"):
            # In a real implementation the user_id would be determined from
            # the verified fingerprint data

            return {"match": True, "user_id": "1234"}
        return {"match": False}