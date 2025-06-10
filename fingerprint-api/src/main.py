from fastapi import FastAPI
from api.endpoints.enrollment import enroll_fingerprint
from api.endpoints.verification import verify_fingerprint

app = FastAPI()

app.include_router(enroll_fingerprint.router)
app.include_router(verify_fingerprint.router)