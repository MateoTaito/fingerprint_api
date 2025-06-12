from typing import Any, Dict
from .libfprint_driver import LibfprintDriver


class FingerprintService:
    def __init__(self) -> None:
        self.driver = LibfprintDriver()

    def enroll_fingerprint(self, user_id: str, fingerprint_data: bytes | None = None) -> Dict[str, Any]:
        self.driver.enroll_fingerprint(fingerprint_data)
        return {"message": "Fingerprint enrolled successfully", "user_id": user_id}

    def verify_fingerprint(self, fingerprint_data: bytes) -> Dict[str, Any]:
        match = self.driver.verify_fingerprint(fingerprint_data)
        if match:
            return {"match": True, "user_id": "1234"}
        return {"match": False}
