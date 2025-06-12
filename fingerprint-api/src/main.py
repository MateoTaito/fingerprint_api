from fastapi import FastAPI
from src.api.endpoints import enrollment as enroll_fingerprint
from src.api.endpoints import verification as verify_fingerprint


app = FastAPI()

app.include_router(enrollment.router)
app.include_router(verification.router)
