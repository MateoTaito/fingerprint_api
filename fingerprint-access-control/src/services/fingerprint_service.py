from pydbus import SystemBus
from gi.repository import GLib
import json
import os
import pwd
import getpass

class FingerprintService:
    def __init__(self):
        self.fingerprints_file = "fingerprints_labels.json"
        self.fingerprints_with_labels = []
        self.loop = None
        self.enrollment_success = False
        self.verification_success = False
        self.verification_result = None
        
        try:
            self.bus = SystemBus()
            self.device = self.get_fingerprint_device()
            self.fingerprint_available = True
            self.load_fingerprints_labels()
            print("✅ Fingerprint service initialized successfully")
        except Exception as e:
            print(f"⚠️ Warning: Fingerprint service not available: {e}")
            print("Running in demo mode without fingerprint functionality.")
            self.device = None
            self.fingerprint_available = False

    def get_fingerprint_device(self):
        fprintd_root = self.bus.get("net.reactivated.Fprint", "/net/reactivated/Fprint")
        managed_objects = fprintd_root.GetManagedObjects()
        devices = [path for path, interfaces in managed_objects.items() 
                   if 'net.reactivated.Fprint.Device' in interfaces]
        if not devices:
            raise Exception("No fingerprint devices found!")
        
        device = self.bus.get("net.reactivated.Fprint", devices[0])
        # Connect to signals
        device.EnrollStatus.connect(self.on_enroll_status)
        device.VerifyStatus.connect(self.on_verify_status)
        return device

    def load_fingerprints_labels(self):
        """Cargar etiquetas desde archivo JSON"""
        try:
            if os.path.exists(self.fingerprints_file):
                with open(self.fingerprints_file, 'r', encoding='utf-8') as f:
                    self.fingerprints_with_labels = json.load(f)
                print(f"✅ Loaded {len(self.fingerprints_with_labels)} fingerprint labels")
            else:
                self.fingerprints_with_labels = []
                print(f"📄 Fingerprint labels file not found, starting with empty list")
        except Exception as e:
            print(f"⚠️ Error loading fingerprint labels: {e}")
            self.fingerprints_with_labels = []

    def save_fingerprints_labels(self):
        """Guardar etiquetas en archivo JSON"""
        try:
            with open(self.fingerprints_file, 'w', encoding='utf-8') as f:
                json.dump(self.fingerprints_with_labels, f, indent=2, ensure_ascii=False)
            print(f"💾 Fingerprint labels saved successfully")
        except Exception as e:
            print(f"⚠️ Error saving fingerprint labels: {e}")

    def on_enroll_status(self, result, done):
        """Callback para el estado del enrollment"""
        print(f"Enrollment status: {result}, done: {done}")
        if result == "enroll-completed":
            print("✅ Fingerprint enrollment completed successfully!")
            self.enrollment_success = True
            if self.loop:
                self.loop.quit()
        elif result == "enroll-failed":
            print("❌ Fingerprint enrollment failed")
            self.enrollment_success = False
            if self.loop:
                self.loop.quit()
        elif result == "enroll-stage-passed":
            print("📝 Enrollment stage passed, continue...")
        elif result == "enroll-retry-scan":
            print("🔄 Please retry the scan")
        elif result == "enroll-swipe-too-short":
            print("⚡ Swipe too short, try again")

    def on_verify_status(self, result, done):
        """Callback para el estado de la verificación"""
        print(f"Verify status: {result}, done: {done}")
        if result == "verify-match":
            print("✅ Fingerprint verified successfully!")
            self.verification_success = True
            self.verification_result = "match"
            if self.loop:
                self.loop.quit()
        elif result == "verify-no-match":
            print("❌ Fingerprint does not match")
            self.verification_success = False
            self.verification_result = "no-match"
            if self.loop:
                self.loop.quit()
        elif result == "verify-retry-scan":
            print("🔄 Please retry the scan")
        elif result == "verify-swipe-too-short":
            print("⚡ Swipe too short, try again")

    def get_available_fingers(self):
        """Obtener lista de dedos disponibles"""
        return [
            "left-thumb", "left-index-finger", "left-middle-finger", 
            "left-ring-finger", "left-little-finger",
            "right-thumb", "right-index-finger", "right-middle-finger", 
            "right-ring-finger", "right-little-finger"
        ]

    def enroll_fingerprint(self, username, finger, label=None):
        """Enrollar una huella dactilar para un usuario específico"""
        if not self.fingerprint_available:
            print("⚠️ Fingerprint service not available - simulating enrollment")
            return self.simulate_enrollment(username, finger, label)
        
        try:
            print(f"\n🔐 Enrolling {finger} for user {username}...")
            if label:
                print(f"📝 Label: {label}")
            print("👆 Please place your finger on the scanner multiple times when prompted...")
            
            # Reset enrollment state
            self.enrollment_success = False
            
            # Claim device for specific user
            self.device.Claim(username)
            self.device.EnrollStart(finger)
            
            # Create event loop with timeout
            self.loop = GLib.MainLoop()
            GLib.timeout_add_seconds(60, lambda: self.loop.quit())
            
            print("⏳ Waiting for enrollment... (60 seconds maximum)")
            self.loop.run()
            
            # Stop enrollment and release device
            self.device.EnrollStop()
            self.device.Release()
            
            if self.enrollment_success:
                # Save label if provided
                if label:
                    self.add_fingerprint_label(username, finger, label)
                print(f"✅ Fingerprint enrolled successfully for {username}")
                return True
            else:
                print(f"❌ Fingerprint enrollment failed for {username}")
                return False
                
        except Exception as e:
            print(f"⚠️ Error during fingerprint enrollment: {e}")
            try:
                self.device.Release()
            except:
                pass
            return False

    def verify_fingerprint(self, username, finger=None):
        """Verificar huella dactilar de un usuario"""
        if not self.fingerprint_available:
            print("⚠️ Fingerprint service not available - simulating verification")
            return self.simulate_verification(username, finger)
        
        try:
            if finger:
                print(f"\n🔍 Verifying {finger} for user {username}...")
            else:
                print(f"\n🔍 Verifying fingerprint for user {username}...")
            print("👆 Please place your finger on the scanner...")
            
            # Reset verification state
            self.verification_success = False
            self.verification_result = None
            
            # Claim device for specific user
            self.device.Claim(username)
            
            if finger:
                self.device.VerifyStart(finger)
            else:
                # If no specific finger, try to verify any enrolled finger
                enrolled_fingers = self.get_enrolled_fingers(username)
                if not enrolled_fingers:
                    print(f"❌ No enrolled fingerprints found for user {username}")
                    self.device.Release()
                    return False
                self.device.VerifyStart(enrolled_fingers[0])
            
            # Create event loop with timeout
            self.loop = GLib.MainLoop()
            GLib.timeout_add_seconds(30, lambda: self.loop.quit())
            
            print("⏳ Waiting for verification... (30 seconds maximum)")
            self.loop.run()
            
            # Stop verification and release device
            self.device.VerifyStop()
            self.device.Release()
            
            if self.verification_success and self.verification_result == "match":
                print(f"✅ Fingerprint verified successfully for {username}")
                return True
            else:
                print(f"❌ Fingerprint verification failed for {username}")
                return False
                
        except Exception as e:
            print(f"⚠️ Error during fingerprint verification: {e}")
            try:
                self.device.Release()
            except:
                pass
            return False

    def get_enrolled_fingers(self, username):
        """Obtener lista de dedos enrollados para un usuario"""
        if not self.fingerprint_available:
            return []
        
        try:
            enrolled_fingers = self.device.ListEnrolledFingers(username)
            return enrolled_fingers
        except Exception as e:
            print(f"⚠️ Error getting enrolled fingers for {username}: {e}")
            return []

    def delete_enrolled_finger(self, username, finger):
        """Eliminar una huella enrollada específica"""
        if not self.fingerprint_available:
            print("⚠️ Fingerprint service not available - simulating deletion")
            return True
        
        try:
            self.device.Claim(username)
            self.device.DeleteEnrolledFinger(finger)
            self.device.Release()
            
            # Remove from labels file
            self.remove_fingerprint_label(username, finger)
            print(f"🗑️ Fingerprint {finger} deleted for user {username}")
            return True
        except Exception as e:
            print(f"⚠️ Error deleting fingerprint: {e}")
            try:
                self.device.Release()
            except:
                pass
            return False

    def list_all_enrolled_fingerprints(self):
        """Listar todas las huellas enrolladas en el sistema"""
        if not self.fingerprint_available:
            print("⚠️ Fingerprint service not available")
            return {}
        
        enrolled_data = {}
        
        try:
            # Get all system users
            all_users = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]
            all_users.append('root')
            all_users = list(set(all_users))
            
            print(f"\n📋 Checking {len(all_users)} system users...\n")
            
            for username in sorted(all_users):
                try:
                    enrolled_fingers = self.device.ListEnrolledFingers(username)
                    if enrolled_fingers:
                        enrolled_data[username] = []
                        for finger in enrolled_fingers:
                            label = self.get_fingerprint_label(username, finger)
                            enrolled_data[username].append({
                                'finger': finger,
                                'label': label
                            })
                except Exception:
                    # Silently skip users without permissions
                    continue
            
            return enrolled_data
            
        except Exception as e:
            print(f"⚠️ Error listing enrolled fingerprints: {e}")
            return {}

    def simulate_enrollment(self, username, finger, label=None):
        """Simular enrollment para desarrollo sin hardware"""
        print(f"🎭 SIMULATION: Enrolling {finger} for user {username}")
        if label:
            print(f"📝 Label: {label}")
        print("Press Enter to simulate fingerprint enrollment...")
        input()
        
        if label:
            self.add_fingerprint_label(username, finger, label)
        
        print("✅ Simulated enrollment completed successfully!")
        return True

    def simulate_verification(self, username, finger=None):
        """Simular verificación para desarrollo sin hardware"""
        if finger:
            print(f"🎭 SIMULATION: Verifying {finger} for user {username}")
        else:
            print(f"🎭 SIMULATION: Verifying fingerprint for user {username}")
        print("Press Enter to simulate fingerprint verification...")
        input()
        print("✅ Simulated verification completed successfully!")
        return True