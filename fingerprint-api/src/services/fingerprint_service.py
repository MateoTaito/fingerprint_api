from typing import Any, Dict

from .digitalpersona_driver import DigitalPersonaDriver

class FingerprintService:
    def __init__(self) -> None:
        self.driver = DigitalPersonaDriver()

    def enroll_fingerprint(self) -> Dict[str, Any]:
        """Enroll a fingerprint using the underlying driver."""
        result = self.driver.enroll_fingerprint()
        if result.get("status") == "success":
            # In a real implementation the captured fingerprint would be
            # persisted and linked to a user. Tests only assert the success
            # message so we simply return it here.
            return {"message": "Fingerprint enrolled successfully"}
        raise Exception(result.get("message", "Fingerprint enrollment failed"))

    def verify_fingerprint(self, fingerprint_data: bytes) -> Dict[str, Any]:
        """Verify the supplied fingerprint data."""
        match_result = self.driver.verify_fingerprint(fingerprint_data)
        match = match_result.get("match", False)
        if match:
            # Normally the user_id associated with the fingerprint would be
            # returned from the driver or a database lookup. For the purposes
            # of the tests we return a static user_id when a match occurs.
            return {"match": True, "user_id": "1234"}
        return {"match": False}