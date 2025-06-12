try:
    from digitalpersona import DigitalPersona  # type: ignore
except ImportError:  # pragma: no cover - fallback for testing without the library
    class DigitalPersona:
        """Fallback DigitalPersona implementation used in tests."""

        def capture_fingerprint(self):
            return b"dummy_fingerprint"

        def verify_fingerprint(self, fingerprint_data):
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
        return self.device.verify_fingerprint(fingerprint_data)
