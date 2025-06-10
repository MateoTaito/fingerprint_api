from fastapi import APIRouter, HTTPException
from services.fingerprint_service import FingerprintService

router = APIRouter()
fingerprint_service = FingerprintService()

@router.post("/fingerprints/enroll")
def enroll_fingerprint(user_id: str, fingerprint_data: bytes):
    try:
        fingerprint_service.enroll_fingerprint(user_id, fingerprint_data)
        return {"message": "Fingerprint enrolled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))