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

    def delete_all_user_fingerprints(self, username):
        """Eliminar todas las huellas enrolladas de un usuario"""
        if not self.fingerprint_available:
            print("⚠️ Fingerprint service not available - simulating deletion of all fingerprints")
            return True
        
        try:
            # Get all enrolled fingers for the user
            enrolled_fingers = self.get_enrolled_fingers(username)
            
            if not enrolled_fingers:
                print(f"ℹ️ No enrolled fingerprints found for user {username}")
                return True
            
            print(f"🗑️ Deleting {len(enrolled_fingers)} fingerprints for user {username}...")
            
            success_count = 0
            for finger in enrolled_fingers:
                if self.delete_enrolled_finger(username, finger):
                    success_count += 1
                else:
                    print(f"⚠️ Failed to delete {finger} for user {username}")
            
            # Remove all labels for this user
            self.remove_all_user_fingerprint_labels(username)
            
            if success_count == len(enrolled_fingers):
                print(f"✅ All {success_count} fingerprints deleted successfully for user {username}")
                return True
            else:
                print(f"⚠️ Only {success_count}/{len(enrolled_fingers)} fingerprints deleted for user {username}")
                return False
                
        except Exception as e:
            print(f"⚠️ Error deleting all fingerprints for user {username}: {e}")
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

    def identify_user_by_fingerprint(self, possible_usernames=None):
        """Identifica el usuario colocando la huella, sin pedir username. Fallback a verificación secuencial si Identify no está disponible."""
        if not self.fingerprint_available:
            print("⚠️ Fingerprint service not available - identificación simulada")
            print("Presiona Enter para simular identificación...")
            input()
            print("Usuario simulado identificado: demo_user")
            return "demo_user"
        try:
            print("\n=== Identificación biométrica ===")
            print("Coloca tu dedo en el lector para identificarte...")
            # Intentar identificación directa
            if possible_usernames is None:
                possible_usernames = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]
                possible_usernames.append('root')
                possible_usernames = list(set(possible_usernames))
            # Fallback: verificación secuencial si IdentifyStatus no está disponible
            if not hasattr(self.device, 'IdentifyStatus'):
                print("⚠️ Identificación directa no soportada, usando verificación secuencial...")
                for username in possible_usernames:
                    enrolled_fingers = self.get_enrolled_fingers(username)
                    if not enrolled_fingers:
                        continue
                    for finger in enrolled_fingers:
                        print(f"Intentando verificar con usuario: {username}, dedo: {finger}")
                        if self.verify_fingerprint(username, finger):
                            print(f"✅ Usuario identificado: {username}")
                            return username
                print("❌ No se pudo identificar al usuario por huella.")
                return None
            # Si existe IdentifyStatus, intentar identificación directa
            self.identify_result = None
            def on_identify_status(result, username, finger, done):
                print(f"Identify status: {result}, username: {username}, finger: {finger}, done: {done}")
                if result == "identify-match":
                    print(f"✅ Usuario identificado: {username} (dedo: {finger})")
                    self.identify_result = username
                    if self.loop:
                        self.loop.quit()
                elif result == "identify-no-match":
                    print("❌ No se encontró coincidencia de huella")
                    self.identify_result = None
                    if self.loop:
                        self.loop.quit()
                elif result == "identify-retry-scan":
                    print("🔄 Reintenta el escaneo")
                elif result == "identify-swipe-too-short":
                    print("⚡ Deslizamiento muy corto, intenta de nuevo")
            self.device.IdentifyStatus.connect(on_identify_status)
            self.device.IdentifyStart(possible_usernames)
            self.loop = GLib.MainLoop()
            GLib.timeout_add_seconds(30, lambda: self.loop.quit())
            print("⏳ Esperando identificación... (30 segundos máximo)")
            self.loop.run()
            self.device.IdentifyStop()
            self.device.Release()
            return self.identify_result
        except Exception as e:
            print(f"⚠️ Error durante la identificación: {e}")
            try:
                self.device.Release()
            except:
                pass
            # Fallback: verificación secuencial si ocurre cualquier error
            print("⚠️ Fallback a verificación secuencial...")
            if possible_usernames is None:
                possible_usernames = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]
                possible_usernames.append('root')
                possible_usernames = list(set(possible_usernames))
            for username in possible_usernames:
                enrolled_fingers = self.get_enrolled_fingers(username)
                if not enrolled_fingers:
                    continue
                for finger in enrolled_fingers:
                    print(f"Intentando verificar con usuario: {username}, dedo: {finger}")
                    if self.verify_fingerprint(username, finger):
                        print(f"✅ Usuario identificado: {username}")
                        return username
            print("❌ No se pudo identificar al usuario por huella.")
            return None

    def add_fingerprint_label(self, username, finger, label):
        """Agregar o actualizar etiqueta para una huella"""
        try:
            # Buscar si ya existe una entrada para este usuario y dedo
            for item in self.fingerprints_with_labels:
                if item['username'] == username and item['finger'] == finger:
                    item['label'] = label
                    self.save_fingerprints_labels()
                    return
            
            # Si no existe, agregar nueva entrada
            self.fingerprints_with_labels.append({
                'username': username,
                'finger': finger,
                'label': label
            })
            self.save_fingerprints_labels()
            print(f"📝 Label '{label}' added for {username} - {finger}")
            
        except Exception as e:
            print(f"⚠️ Error adding fingerprint label: {e}")

    def remove_fingerprint_label(self, username, finger):
        """Eliminar etiqueta para una huella específica"""
        try:
            self.fingerprints_with_labels = [
                item for item in self.fingerprints_with_labels 
                if not (item['username'] == username and item['finger'] == finger)
            ]
            self.save_fingerprints_labels()
            print(f"🗑️ Label removed for {username} - {finger}")
            
        except Exception as e:
            print(f"⚠️ Error removing fingerprint label: {e}")

    def remove_all_user_fingerprint_labels(self, username):
        """Eliminar todas las etiquetas de un usuario"""
        try:
            original_count = len(self.fingerprints_with_labels)
            self.fingerprints_with_labels = [
                item for item in self.fingerprints_with_labels 
                if item['username'] != username
            ]
            removed_count = original_count - len(self.fingerprints_with_labels)
            self.save_fingerprints_labels()
            print(f"🗑️ Removed {removed_count} labels for user {username}")
            
        except Exception as e:
            print(f"⚠️ Error removing all labels for user {username}: {e}")

    def get_fingerprint_label(self, username, finger):
        """Obtener etiqueta para una huella específica"""
        try:
            for item in self.fingerprints_with_labels:
                if item['username'] == username and item['finger'] == finger:
                    return item['label']
            return None
            
        except Exception as e:
            print(f"⚠️ Error getting fingerprint label: {e}")
            return None