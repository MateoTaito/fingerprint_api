from pydbus import SystemBus
from gi.repository import GLib
import json
import os

class FingerprintService:
    def __init__(self):
        self.bus = SystemBus()
        self.device = self.get_fingerprint_device()
        self.loop = None

    def get_fingerprint_device(self):
        fprintd_root = self.bus.get("net.reactivated.Fprint", "/net/reactivated/Fprint")
        managed_objects = fprintd_root.GetManagedObjects()
        devices = [path for path, interfaces in managed_objects.items() 
                   if 'net.reactivated.Fprint.Device' in interfaces]
        if not devices:
            raise Exception("No fingerprint devices found!")
        return self.bus.get("net.reactivated.Fprint", devices[0])

    def enroll_fingerprint(self, username, finger):
        self.device.Claim(username)
        self.device.EnrollStart(finger)
        self.loop = GLib.MainLoop()
        GLib.timeout_add_seconds(60, lambda: self.loop.quit())
        print("Esperando enrollment... (60 segundos máximo)")
        self.loop.run()
        self.device.EnrollStop()
        self.device.Release()

    def verify_fingerprint(self, username, finger):
        self.device.Claim(username)
        self.device.VerifyStart(finger)
        self.loop = GLib.MainLoop()
        GLib.timeout_add_seconds(60, lambda: self.loop.quit())
        print("Esperando verificación... (60 segundos máximo)")
        self.loop.run()
        self.device.VerifyStop()
        self.device.Release()

    def add_fingerprint_label(self, username, finger, label):
        # Load existing fingerprints
        fingerprints_file = "fingerprints_labels.json"
        if os.path.exists(fingerprints_file):
            with open(fingerprints_file, 'r', encoding='utf-8') as f:
                fingerprints_with_labels = json.load(f)
        else:
            fingerprints_with_labels = []

        # Check for existing entry
        for i, (stored_user, stored_finger, stored_label) in enumerate(fingerprints_with_labels):
            if stored_user == username and stored_finger == finger:
                fingerprints_with_labels[i] = (username, finger, label)
                break
        else:
            fingerprints_with_labels.append((username, finger, label))

        # Save updated fingerprints
        with open(fingerprints_file, 'w', encoding='utf-8') as f:
            json.dump(fingerprints_with_labels, f, indent=2, ensure_ascii=False)

    def get_fingerprint_label(self, username, finger):
        fingerprints_file = "fingerprints_labels.json"
        if os.path.exists(fingerprints_file):
            with open(fingerprints_file, 'r', encoding='utf-8') as f:
                fingerprints_with_labels = json.load(f)
            for stored_user, stored_finger, stored_label in fingerprints_with_labels:
                if stored_user == username and stored_finger == finger:
                    return stored_label
        return "Sin etiqueta"