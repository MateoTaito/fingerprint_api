from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_enroll_fingerprint():
    payload = {"user_id": "test_user", "fingerprint_data": "sample_data"}
    response = client.post("/fingerprints/enroll", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Fingerprint enrolled successfully"}

