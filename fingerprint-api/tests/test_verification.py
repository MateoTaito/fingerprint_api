from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_verify_fingerprint_success():
    response = client.post("/fingerprints/verify", json={"fingerprint_data": "sample_data"})
    assert response.status_code == 200
    assert response.json() == {"match": True, "user_id": "1234"}

def test_verify_fingerprint_failure():
    response = client.post("/fingerprints/verify", json={"fingerprint_data": "invalid_data"})
    assert response.status_code == 200
    assert response.json() == {"match": False}