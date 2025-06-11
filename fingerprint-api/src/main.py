from fastapi import FastAPI

from api.endpoints import enrollment, verification

app = FastAPI()

app.include_router(enrollment.router)
app.include_router(verification.router)
