from fastapi import APIRouter, HTTPException
from src.services.fingerprint_service import FingerprintService

router = APIRouter()
fingerprint_service = FingerprintService()

@router.post("/fingerprints/verify")
def verify_fingerprint(user_id: str, fingerprint_data: bytes):
    try:
        match = fingerprint_service.verify_fingerprint(user_id, fingerprint_data)
        return {"match": match, "user_id": user_id} if match else {"match": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))