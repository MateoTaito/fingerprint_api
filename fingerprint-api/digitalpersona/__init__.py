class DigitalPersona:
    def capture_fingerprint(self):
        return b"fake_fingerprint"

    def verify_fingerprint(self, fingerprint_data):
        # For testing, consider 'sample_data' as valid fingerprint
        return fingerprint_data == b"sample_data"
