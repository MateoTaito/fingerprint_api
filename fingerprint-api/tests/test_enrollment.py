from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_enroll_fingerprint():
    response = client.post("/fingerprints/enroll", json={"user_id": "1234"})
    assert response.status_code == 200
    assert response.json() == {
        "message": "Fingerprint enrolled successfully",
        "user_id": "1234",
    }

def test_verify_fingerprint():
    response = client.post(
        "/fingerprints/verify", json={"fingerprint_data": "sample_data"}
    )
    assert response.status_code == 200
    assert response.json() == {"match": True, "user_id": "1234"}