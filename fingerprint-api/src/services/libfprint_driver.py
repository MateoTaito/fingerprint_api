"""Driver that interfaces with the libfprint library."""

try:
    import fprint
    fprint.init()
    HARDWARE_AVAILABLE = True
except Exception:  # pragma: no cover - fallback when libfprint is unavailable
    HARDWARE_AVAILABLE = False

    class DummyDevice:
        def enroll_finger_loop(self):
            class PrintData:
                def __init__(self, data=b"dummy_fingerprint"):
                    self.data = data
            return PrintData()

        def verify_finger_loop(self, pd):
            return pd.data == b"sample_data"

    class DummyPrintData:
        def __init__(self, data: bytes):
            self.data = data

        @staticmethod
        def from_data(data: bytes):
            return DummyPrintData(data)

    class fprint:  # type: ignore
        PrintData = DummyPrintData

        @staticmethod
        def DiscoveredDevices():
            return [DummyDevice()]


class LibfprintDriver:
    """High level driver used by the service layer."""

    def __init__(self) -> None:
        devices = fprint.DiscoveredDevices()
        if not devices:
            raise RuntimeError("No fingerprint devices found")
        self.device = devices[0].open_device() if HARDWARE_AVAILABLE else devices[0]

    def enroll_fingerprint(self):
        """Capture and return fingerprint data."""
        print_data = self.device.enroll_finger_loop()
        if print_data:
            return {"status": "success", "data": getattr(print_data, "data", b"")}
        return {"status": "error", "message": "Fingerprint capture failed"}

    def verify_fingerprint(self, fingerprint_data: bytes):
        """Verify fingerprint data with the device."""
        pd = fprint.PrintData.from_data(fingerprint_data)
        return self.device.verify_finger_loop(pd)
