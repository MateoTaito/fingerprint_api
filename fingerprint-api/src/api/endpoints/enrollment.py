from fastapi import APIRouter, HTTPException

from services.fingerprint_service import FingerprintService

router = APIRouter()
fingerprint_service = FingerprintService()

@router.post("/fingerprints/enroll")
def enroll_fingerprint():
    """Endpoint to enroll a new fingerprint."""
    try:
        return fingerprint_service.enroll_fingerprint()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))