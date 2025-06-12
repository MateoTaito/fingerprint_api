try:
    from digitalpersona import DigitalPersona  # type: ignore
except ImportError:  # pragma: no cover - fallback stub for tests
    class DigitalPersona:
        """Simple stub used when the real library is unavailable."""

        def capture_fingerprint(self):
            return b"stub_data"

        def verify_fingerprint(self, fingerprint_data):
            # Pretend that any data equal to b"sample_data" matches
            return fingerprint_data == b"sample_data"

class DigitalPersonaDriver:
    def __init__(self):
        self.device = DigitalPersona()  # Initialize the fingerprint reader

    def enroll_fingerprint(self):
        """Capture and enroll a new fingerprint."""
        fingerprint_data = self.device.capture_fingerprint()
        if fingerprint_data:
            # Process and store the fingerprint data
            return {"status": "success", "data": fingerprint_data}
        return {"status": "error", "message": "Fingerprint capture failed"}

    def verify_fingerprint(self, fingerprint_data):
        """Verify an existing fingerprint against captured data."""
        match = self.device.verify_fingerprint(fingerprint_data)
        return {"match": match}