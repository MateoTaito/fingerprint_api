from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.fingerprint_service import FingerprintService

router = APIRouter()
fingerprint_service = FingerprintService()

class VerificationRequest(BaseModel):
    fingerprint_data: bytes


@router.post("/fingerprints/verify")
def verify_fingerprint(payload: VerificationRequest):
    try:
        result = fingerprint_service.verify_fingerprint(payload.fingerprint_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))