from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.fingerprint_service import FingerprintService

router = APIRouter()
fingerprint_service = FingerprintService()

class EnrollmentRequest(BaseModel):
    user_id: str
    fingerprint_data: bytes


@router.post("/fingerprints/enroll")
def enroll_fingerprint(payload: EnrollmentRequest):
    try:
        fingerprint_service.enroll_fingerprint(payload.user_id, payload.fingerprint_data)
        return {"message": "Fingerprint enrolled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))