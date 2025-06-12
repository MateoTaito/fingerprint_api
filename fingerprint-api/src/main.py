from fastapi import FastAPI
from src.api.endpoints import enrollment as enroll_fingerprint
from src.api.endpoints import verification as verify_fingerprint

app = FastAPI()

app.include_router(enroll_fingerprint.router)
app.include_router(verify_fingerprint.router)