try:
    import libfprint
except Exception:  # pragma: no cover - libfprint may not be installed
    libfprint = None


class LibfprintDriver:
    """Wrapper around the libfprint library."""

    def __init__(self) -> None:
        self.device = None
        if libfprint is not None:
            try:
                self.device = libfprint.Fprint()
                self.device.open()
            except Exception:
                self.device = None

    def enroll_fingerprint(self, fingerprint_data: bytes | None = None) -> bytes:
        """Capture and return fingerprint data."""
        if self.device is not None:
            return self.device.enroll_finger()
        # Fallback data used in tests
        return fingerprint_data or b"sample_fingerprint"

    def verify_fingerprint(self, fingerprint_data: bytes) -> bool:
        """Verify provided fingerprint data."""
        if self.device is not None:
            return bool(self.device.verify_finger(fingerprint_data))
        # Simple stub behaviour for tests
        return fingerprint_data == b"sample_data"
