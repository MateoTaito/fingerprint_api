from fastapi import APIRouter, HTTPException, Body
from ...services.fingerprint_service import FingerprintService

router = APIRouter()
fingerprint_service = FingerprintService()


@router.post("/fingerprints/verify")
def verify_fingerprint(fingerprint_data: str | None = Body(None, embed=True)):
    try:
        data = fingerprint_data.encode() if fingerprint_data else b"sample_data"
        return fingerprint_service.verify_fingerprint(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
