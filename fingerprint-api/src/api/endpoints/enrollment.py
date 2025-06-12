from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.fingerprint_service import FingerprintService


router = APIRouter()
fingerprint_service = FingerprintService()

class EnrollRequest(BaseModel):
    user_id: str


@router.post("/fingerprints/enroll")
def enroll_fingerprint(request: EnrollRequest):
    try:
        result = fingerprint_service.enroll_fingerprint(request.user_id)
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))