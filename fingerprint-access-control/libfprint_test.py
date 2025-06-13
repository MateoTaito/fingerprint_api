from pydbus import SystemBus
import sys
from gi.repository import GLib
import getpass
import json
import os

# Archivo para almacenar las etiquetas
FINGERPRINTS_FILE = "fingerprints_labels.json"

# Variable global para almacenar huellas con etiquetas
fingerprints_with_labels = []

def load_fingerprints_labels():
    """Cargar etiquetas desde archivo JSON"""
    global fingerprints_with_labels
    try:
        if os.path.exists(FINGERPRINTS_FILE):
            with open(FINGERPRINTS_FILE, 'r', encoding='utf-8') as f:
                fingerprints_with_labels = json.load(f)
            print(f"✅ Cargadas {len(fingerprints_with_labels)} etiquetas desde {FINGERPRINTS_FILE}")
        else:
            fingerprints_with_labels = []
            print(f"📄 Archivo {FINGERPRINTS_FILE} no existe, iniciando con lista vacía")
    except Exception as e:
        print(f"⚠️  Error cargando etiquetas: {e}")
        fingerprints_with_labels = []

def save_fingerprints_labels():
    """Guardar etiquetas en archivo JSON"""
    global fingerprints_with_labels
    try:
        with open(FINGERPRINTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(fingerprints_with_labels, f, indent=2, ensure_ascii=False)
        print(f"💾 Etiquetas guardadas en {FINGERPRINTS_FILE}")
    except Exception as e:
        print(f"⚠️  Error guardando etiquetas: {e}")

def add_fingerprint_label(username, finger, label):
    """Agregar nueva etiqueta y guardar en archivo"""
    global fingerprints_with_labels
    
    # Verificar si ya existe esta combinación usuario-dedo
    for i, (stored_user, stored_finger, stored_label) in enumerate(fingerprints_with_labels):
        if stored_user == username and stored_finger == finger:
            # Actualizar etiqueta existente
            fingerprints_with_labels[i] = (username, finger, label)
            save_fingerprints_labels()
            print(f"🔄 Etiqueta actualizada: {username} - {finger} -> {label}")
            return
    
    # Agregar nueva etiqueta
    fingerprints_with_labels.append((username, finger, label))
    save_fingerprints_labels()
    print(f"➕ Nueva etiqueta agregada: {username} - {finger} -> {label}")

def get_fingerprint_label(username, finger):
    """Obtener etiqueta para una huella específica"""
    global fingerprints_with_labels
    for stored_user, stored_finger, stored_label in fingerprints_with_labels:
        if stored_user == username and stored_finger == finger:
            return stored_label
    return "Sin etiqueta"

def remove_fingerprint_label(username, finger):
    """Eliminar etiqueta de una huella"""
    global fingerprints_with_labels
    fingerprints_with_labels = [(u, f, l) for u, f, l in fingerprints_with_labels 
                               if not (u == username and f == finger)]
    save_fingerprints_labels()
    print(f"🗑️  Etiqueta eliminada: {username} - {finger}")

def view_fingerprints_file():
    """Ver contenido del archivo de etiquetas"""
    try:
        if os.path.exists(FINGERPRINTS_FILE):
            print(f"\n📄 CONTENIDO DE {FINGERPRINTS_FILE}:")
            print("=" * 50)
            with open(FINGERPRINTS_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
            print("=" * 50)
            
            # También mostrar la ruta completa
            full_path = os.path.abspath(FINGERPRINTS_FILE)
            print(f"📁 Ruta completa: {full_path}")
        else:
            print(f"❌ El archivo {FINGERPRINTS_FILE} no existe")
    except Exception as e:
        print(f"⚠️  Error leyendo archivo: {e}")

def on_enroll_status(result, done):
    print(f"Enrollment status: {result}, done: {done}")
    if result == "enroll-completed":
        print("¡Enrollment completado!")
        loop.quit()
    elif result == "enroll-failed":
        print("Enrollment falló")
        loop.quit()
    elif result == "enroll-stage-passed":
        print("Etapa pasada, continúa...")
    elif result == "enroll-retry-scan":
        print("Reintenta el escaneo")
    elif result == "enroll-swipe-too-short":
        print("Deslizamiento muy corto")

def on_verify_status(result, done):
    print(f"Verify status: {result}, done: {done}")
    if result == "verify-match":
        print("¡Huella verificada correctamente!")
        loop.quit()
    elif result == "verify-no-match":
        print("Huella no coincide")
        loop.quit()
    elif result == "verify-retry-scan":
        print("Reintenta el escaneo")
    elif result == "verify-swipe-too-short":
        print("Deslizamiento muy corto")

def enroll_fingerprint_with_label(device, username, finger, label):
    """Función para enrollar una huella específica con etiqueta"""
    global loop
    print(f"\nEnrollando {finger} ({label}) para usuario {username}...")
    print("Coloca tu dedo en el lector varias veces cuando se te indique...")
    
    # Claim device for specific user
    device.Claim(username)
    device.EnrollStart(finger)
    
    # Create event loop
    loop = GLib.MainLoop()
    GLib.timeout_add_seconds(60, lambda: loop.quit())
    
    print("Esperando enrollment... (60 segundos máximo)")
    loop.run()
    
    device.EnrollStop()
    device.Release()
    
    # Agregar a la lista con etiqueta y guardar en archivo
    add_fingerprint_label(username, finger, label)

def enroll_fingerprint(device, username, finger):
    """Función para enrollar una huella específica"""
    global loop
    print(f"\nEnrollando {finger} para usuario {username}...")
    print("Coloca tu dedo en el lector varias veces cuando se te indique...")
    
    # Claim device for specific user
    device.Claim(username)
    device.EnrollStart(finger)
    
    # Create event loop
    loop = GLib.MainLoop()
    GLib.timeout_add_seconds(60, lambda: loop.quit())
    
    print("Esperando enrollment... (60 segundos máximo)")
    loop.run()
    
    device.EnrollStop()
    device.Release()

def multiple_enrollment():
    """Función para enrollar múltiples huellas"""
    import pwd
    
    # Obtener usuarios válidos del sistema
    valid_users = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]
    valid_users.append('root')
    valid_users = sorted(set(valid_users))
    
    users_and_fingers = []
    
    print("\n=== ENROLLMENT MÚLTIPLE ===")
    print(f"Usuarios válidos en el sistema: {', '.join(valid_users)}")
    
    while True:
        username = input("Ingresa el nombre de usuario (o 'fin' para terminar): ").strip()
        if username.lower() == 'fin':
            break
        
        if username not in valid_users:
            print(f"⚠️  Usuario '{username}' no existe en el sistema!")
            print(f"Usuarios disponibles: {', '.join(valid_users)}")
            continue
            
        print("\nDedos disponibles:")
        fingers = [
            "left-thumb", "left-index-finger", "left-middle-finger", "left-ring-finger", "left-little-finger",
            "right-thumb", "right-index-finger", "right-middle-finger", "right-ring-finger", "right-little-finger"
        ]
        
        for i, finger in enumerate(fingers, 1):
            print(f"{i}. {finger}")
        
        finger_choice = input("Selecciona el número del dedo: ").strip()
        try:
            finger_index = int(finger_choice) - 1
            if 0 <= finger_index < len(fingers):
                selected_finger = fingers[finger_index]
                users_and_fingers.append((username, selected_finger))
                print(f"✓ Agregado: {username} - {selected_finger}")
            else:
                print("Opción inválida")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    return users_and_fingers

def multiple_enrollment_with_labels():
    """Función para enrollar múltiples huellas con etiquetas personalizadas"""
    current_user = getpass.getuser()
    fingerprints = []
    
    print(f"\n=== ENROLLMENT MÚLTIPLE PARA {current_user} ===")
    
    while True:
        label = input("Ingresa una etiqueta para esta huella (ej: 'personal', 'trabajo') o 'fin': ").strip()
        if label.lower() == 'fin':
            break
            
        print("\nDedos disponibles:")
        fingers = [
            "left-thumb", "left-index-finger", "left-middle-finger", "left-ring-finger", "left-little-finger",
            "right-thumb", "right-index-finger", "right-middle-finger", "right-ring-finger", "right-little-finger"
        ]
        
        for i, finger in enumerate(fingers, 1):
            print(f"{i}. {finger}")
        
        finger_choice = input("Selecciona el número del dedo: ").strip()
        try:
            finger_index = int(finger_choice) - 1
            if 0 <= finger_index < len(fingers):
                selected_finger = fingers[finger_index]
                fingerprints.append((current_user, selected_finger, label))
                print(f"✓ Agregado: {label} - {selected_finger}")
            else:
                print("Opción inválida")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    return fingerprints

def list_enrolled_fingers():
    """Función para listar todas las huellas enrolladas automáticamente"""
    global fingerprints_with_labels
    
    try:
        bus = SystemBus()
        fprintd_root = bus.get("net.reactivated.Fprint", "/net/reactivated/Fprint")
        managed_objects = fprintd_root.GetManagedObjects()
        
        devices = [path for path, interfaces in managed_objects.items() 
                  if 'net.reactivated.Fprint.Device' in interfaces]
        
        if not devices:
            print("No fingerprint devices found!")
            return
        
        device_path = devices[0]
        fprintd_device = bus.get("net.reactivated.Fprint", device_path)
        
        print("\n=== HUELLAS ENROLLADAS - TODOS LOS USUARIOS ===")
        
        # Obtener todos los usuarios del sistema
        import subprocess
        import pwd
        
        total_fingerprints = 0
        users_with_fingerprints = 0
        
        # Obtener lista de usuarios del sistema
        try:
            all_users = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]  # Usuarios normales
            all_users.append('root')  # Agregar root también
            all_users = list(set(all_users))  # Eliminar duplicados
            
            print(f"Verificando {len(all_users)} usuarios del sistema...\n")
            
            for username in sorted(all_users):
                try:
                    enrolled_fingers = fprintd_device.ListEnrolledFingers(username)
                    if enrolled_fingers:
                        users_with_fingerprints += 1
                        total_fingerprints += len(enrolled_fingers)
                        print(f"👤 Usuario: {username}")
                        print(f"   📱 Huellas ({len(enrolled_fingers)}):")
                        
                        for i, finger in enumerate(enrolled_fingers, 1):
                            # Buscar etiqueta en archivo
                            label = get_fingerprint_label(username, finger)
                            
                            if label != "Sin etiqueta":
                                print(f"      {i}. {finger} (Etiqueta: {label})")
                            else:
                                print(f"      {i}. {finger}")
                        print()
                except Exception as e:
                    # Silenciar errores para usuarios sin permisos
                    pass
            
            # Mostrar huellas con etiquetas desde archivo
            if fingerprints_with_labels:
                print("🏷️  HUELLAS CON ETIQUETAS (Archivo):")
                for username, finger, label in fingerprints_with_labels:
                    print(f"   • {username}: {finger} -> {label}")
                print()
            
            # Mostrar información del archivo
            if os.path.exists(FINGERPRINTS_FILE):
                full_path = os.path.abspath(FINGERPRINTS_FILE)
                file_size = os.path.getsize(FINGERPRINTS_FILE)
                print(f"📁 Archivo de etiquetas: {full_path}")
                print(f"📊 Tamaño del archivo: {file_size} bytes")
                print()
            
            # Resumen
            print("=" * 50)
            print(f"📊 RESUMEN:")
            print(f"   • Total usuarios con huellas: {users_with_fingerprints}")
            print(f"   • Total huellas enrolladas: {total_fingerprints}")
            print(f"   • Usuarios verificados: {len(all_users)}")
            print(f"   • Huellas con etiquetas (archivo): {len(fingerprints_with_labels)}")
            
            if users_with_fingerprints == 0:
                print("\n⚠️  No se encontraron huellas enrolladas en el sistema")
                
        except Exception as e:
            print(f"Error al obtener usuarios del sistema: {e}")
                
    except Exception as e:
        print(f"Error general: {e}")
        import traceback
        traceback.print_exc()

def on_verify_status_with_identification(result, done):
    """Callback para verificación con identificación de etiqueta"""
    global loop, verification_result
    if result == "verify-match":
        print("✅ ¡Huella coincide!")
        verification_result = True
        loop.quit()
    elif result == "verify-no-match":
        print("❌ No coincide")
        verification_result = False
        loop.quit()
    elif result == "verify-retry-scan":
        print("🔄 Vuelve a colocar tu dedo")
    elif result == "verify-swipe-too-short":
        print("⚠️  Deslizamiento muy corto, inténtalo de nuevo")

def enroll_fingerprint_with_label(device, username, finger, label):
    """Función para enrollar una huella específica con etiqueta"""
    global loop
    print(f"\nEnrollando {finger} ({label}) para usuario {username}...")
    print("Coloca tu dedo en el lector varias veces cuando se te indique...")
    
    # Claim device for specific user
    device.Claim(username)
    device.EnrollStart(finger)
    
    # Create event loop
    loop = GLib.MainLoop()
    GLib.timeout_add_seconds(60, lambda: loop.quit())
    
    print("Esperando enrollment... (60 segundos máximo)")
    loop.run()
    
    device.EnrollStop()
    device.Release()
    
    # Agregar a la lista con etiqueta y guardar en archivo
    add_fingerprint_label(username, finger, label)

def enroll_fingerprint(device, username, finger):
    """Función para enrollar una huella específica"""
    global loop
    print(f"\nEnrollando {finger} para usuario {username}...")
    print("Coloca tu dedo en el lector varias veces cuando se te indique...")
    
    # Claim device for specific user
    device.Claim(username)
    device.EnrollStart(finger)
    
    # Create event loop
    loop = GLib.MainLoop()
    GLib.timeout_add_seconds(60, lambda: loop.quit())
    
    print("Esperando enrollment... (60 segundos máximo)")
    loop.run()
    
    device.EnrollStop()
    device.Release()

def multiple_enrollment():
    """Función para enrollar múltiples huellas"""
    import pwd
    
    # Obtener usuarios válidos del sistema
    valid_users = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]
    valid_users.append('root')
    valid_users = sorted(set(valid_users))
    
    users_and_fingers = []
    
    print("\n=== ENROLLMENT MÚLTIPLE ===")
    print(f"Usuarios válidos en el sistema: {', '.join(valid_users)}")
    
    while True:
        username = input("Ingresa el nombre de usuario (o 'fin' para terminar): ").strip()
        if username.lower() == 'fin':
            break
        
        if username not in valid_users:
            print(f"⚠️  Usuario '{username}' no existe en el sistema!")
            print(f"Usuarios disponibles: {', '.join(valid_users)}")
            continue
            
        print("\nDedos disponibles:")
        fingers = [
            "left-thumb", "left-index-finger", "left-middle-finger", "left-ring-finger", "left-little-finger",
            "right-thumb", "right-index-finger", "right-middle-finger", "right-ring-finger", "right-little-finger"
        ]
        
        for i, finger in enumerate(fingers, 1):
            print(f"{i}. {finger}")
        
        finger_choice = input("Selecciona el número del dedo: ").strip()
        try:
            finger_index = int(finger_choice) - 1
            if 0 <= finger_index < len(fingers):
                selected_finger = fingers[finger_index]
                users_and_fingers.append((username, selected_finger))
                print(f"✓ Agregado: {username} - {selected_finger}")
            else:
                print("Opción inválida")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    return users_and_fingers

def multiple_enrollment_with_labels():
    """Función para enrollar múltiples huellas con etiquetas personalizadas"""
    current_user = getpass.getuser()
    fingerprints = []
    
    print(f"\n=== ENROLLMENT MÚLTIPLE PARA {current_user} ===")
    
    while True:
        label = input("Ingresa una etiqueta para esta huella (ej: 'personal', 'trabajo') o 'fin': ").strip()
        if label.lower() == 'fin':
            break
            
        print("\nDedos disponibles:")
        fingers = [
            "left-thumb", "left-index-finger", "left-middle-finger", "left-ring-finger", "left-little-finger",
            "right-thumb", "right-index-finger", "right-middle-finger", "right-ring-finger", "right-little-finger"
        ]
        
        for i, finger in enumerate(fingers, 1):
            print(f"{i}. {finger}")
        
        finger_choice = input("Selecciona el número del dedo: ").strip()
        try:
            finger_index = int(finger_choice) - 1
            if 0 <= finger_index < len(fingers):
                selected_finger = fingers[finger_index]
                fingerprints.append((current_user, selected_finger, label))
                print(f"✓ Agregado: {label} - {selected_finger}")
            else:
                print("Opción inválida")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    return fingerprints

def list_enrolled_fingers():
    """Función para listar todas las huellas enrolladas automáticamente"""
    global fingerprints_with_labels
    
    try:
        bus = SystemBus()
        fprintd_root = bus.get("net.reactivated.Fprint", "/net/reactivated/Fprint")
        managed_objects = fprintd_root.GetManagedObjects()
        
        devices = [path for path, interfaces in managed_objects.items() 
                  if 'net.reactivated.Fprint.Device' in interfaces]
        
        if not devices:
            print("No fingerprint devices found!")
            return
        
        device_path = devices[0]
        fprintd_device = bus.get("net.reactivated.Fprint", device_path)
        
        print("\n=== HUELLAS ENROLLADAS - TODOS LOS USUARIOS ===")
        
        # Obtener todos los usuarios del sistema
        import subprocess
        import pwd
        
        total_fingerprints = 0
        users_with_fingerprints = 0
        
        # Obtener lista de usuarios del sistema
        try:
            all_users = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]  # Usuarios normales
            all_users.append('root')  # Agregar root también
            all_users = list(set(all_users))  # Eliminar duplicados
            
            print(f"Verificando {len(all_users)} usuarios del sistema...\n")
            
            for username in sorted(all_users):
                try:
                    enrolled_fingers = fprintd_device.ListEnrolledFingers(username)
                    if enrolled_fingers:
                        users_with_fingerprints += 1
                        total_fingerprints += len(enrolled_fingers)
                        print(f"👤 Usuario: {username}")
                        print(f"   📱 Huellas ({len(enrolled_fingers)}):")
                        
                        for i, finger in enumerate(enrolled_fingers, 1):
                            # Buscar etiqueta en archivo
                            label = get_fingerprint_label(username, finger)
                            
                            if label != "Sin etiqueta":
                                print(f"      {i}. {finger} (Etiqueta: {label})")
                            else:
                                print(f"      {i}. {finger}")
                        print()
                except Exception as e:
                    # Silenciar errores para usuarios sin permisos
                    pass
            
            # Mostrar huellas con etiquetas desde archivo
            if fingerprints_with_labels:
                print("🏷️  HUELLAS CON ETIQUETAS (Archivo):")
                for username, finger, label in fingerprints_with_labels:
                    print(f"   • {username}: {finger} -> {label}")
                print()
            
            # Mostrar información del archivo
            if os.path.exists(FINGERPRINTS_FILE):
                full_path = os.path.abspath(FINGERPRINTS_FILE)
                file_size = os.path.getsize(FINGERPRINTS_FILE)
                print(f"📁 Archivo de etiquetas: {full_path}")
                print(f"📊 Tamaño del archivo: {file_size} bytes")
                print()
            
            # Resumen
            print("=" * 50)
            print(f"📊 RESUMEN:")
            print(f"   • Total usuarios con huellas: {users_with_fingerprints}")
            print(f"   • Total huellas enrolladas: {total_fingerprints}")
            print(f"   • Usuarios verificados: {len(all_users)}")
            print(f"   • Huellas con etiquetas (archivo): {len(fingerprints_with_labels)}")
            
            if users_with_fingerprints == 0:
                print("\n⚠️  No se encontraron huellas enrolladas en el sistema")
                
        except Exception as e:
            print(f"Error al obtener usuarios del sistema: {e}")
                
    except Exception as e:
        print(f"Error general: {e}")
        import traceback
        traceback.print_exc()

def on_verify_status_with_identification(result, done):
    """Callback para verificación con identificación de etiqueta"""
    global loop, verification_result
    if result == "verify-match":
        print("✅ ¡Huella coincide!")
        verification_result = True
        loop.quit()
    elif result == "verify-no-match":
        print("❌ No coincide")
        verification_result = False
        loop.quit()
    elif result == "verify-retry-scan":
        print("🔄 Vuelve a colocar tu dedo")
    elif result == "verify-swipe-too-short":
        print("⚠️  Deslizamiento muy corto, inténtalo de nuevo")

def enroll_fingerprint_with_label(device, username, finger, label):
    """Función para enrollar una huella específica con etiqueta"""
    global loop
    print(f"\nEnrollando {finger} ({label}) para usuario {username}...")
    print("Coloca tu dedo en el lector varias veces cuando se te indique...")
    
    # Claim device for specific user
    device.Claim(username)
    device.EnrollStart(finger)
    
    # Create event loop
    loop = GLib.MainLoop()
    GLib.timeout_add_seconds(60, lambda: loop.quit())
    
    print("Esperando enrollment... (60 segundos máximo)")
    loop.run()
    
    device.EnrollStop()
    device.Release()
    
    # Agregar a la lista con etiqueta y guardar en archivo
    add_fingerprint_label(username, finger, label)

def enroll_fingerprint(device, username, finger):
    """Función para enrollar una huella específica"""
    global loop
    print(f"\nEnrollando {finger} para usuario {username}...")
    print("Coloca tu dedo en el lector varias veces cuando se te indique...")
    
    # Claim device for specific user
    device.Claim(username)
    device.EnrollStart(finger)
    
    # Create event loop
    loop = GLib.MainLoop()
    GLib.timeout_add_seconds(60, lambda: loop.quit())
    
    print("Esperando enrollment... (60 segundos máximo)")
    loop.run()
    
    device.EnrollStop()
    device.Release()

def multiple_enrollment():
    """Función para enrollar múltiples huellas"""
    import pwd
    
    # Obtener usuarios válidos del sistema
    valid_users = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]
    valid_users.append('root')
    valid_users = sorted(set(valid_users))
    
    users_and_fingers = []
    
    print("\n=== ENROLLMENT MÚLTIPLE ===")
    print(f"Usuarios válidos en el sistema: {', '.join(valid_users)}")
    
    while True:
        username = input("Ingresa el nombre de usuario (o 'fin' para terminar): ").strip()
        if username.lower() == 'fin':
            break
        
        if username not in valid_users:
            print(f"⚠️  Usuario '{username}' no existe en el sistema!")
            print(f"Usuarios disponibles: {', '.join(valid_users)}")
            continue
            
        print("\nDedos disponibles:")
        fingers = [
            "left-thumb", "left-index-finger", "left-middle-finger", "left-ring-finger", "left-little-finger",
            "right-thumb", "right-index-finger", "right-middle-finger", "right-ring-finger", "right-little-finger"
        ]
        
        for i, finger in enumerate(fingers, 1):
            print(f"{i}. {finger}")
        
        finger_choice = input("Selecciona el número del dedo: ").strip()
        try:
            finger_index = int(finger_choice) - 1
            if 0 <= finger_index < len(fingers):
                selected_finger = fingers[finger_index]
                users_and_fingers.append((username, selected_finger))
                print(f"✓ Agregado: {username} - {selected_finger}")
            else:
                print("Opción inválida")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    return users_and_fingers

def multiple_enrollment_with_labels():
    """Función para enrollar múltiples huellas con etiquetas personalizadas"""
    current_user = getpass.getuser()
    fingerprints = []
    
    print(f"\n=== ENROLLMENT MÚLTIPLE PARA {current_user} ===")
    
    while True:
        label = input("Ingresa una etiqueta para esta huella (ej: 'personal', 'trabajo') o 'fin': ").strip()
        if label.lower() == 'fin':
            break
            
        print("\nDedos disponibles:")
        fingers = [
            "left-thumb", "left-index-finger", "left-middle-finger", "left-ring-finger", "left-little-finger",
            "right-thumb", "right-index-finger", "right-middle-finger", "right-ring-finger", "right-little-finger"
        ]
        
        for i, finger in enumerate(fingers, 1):
            print(f"{i}. {finger}")
        
        finger_choice = input("Selecciona el número del dedo: ").strip()
        try:
            finger_index = int(finger_choice) - 1
            if 0 <= finger_index < len(fingers):
                selected_finger = fingers[finger_index]
                fingerprints.append((current_user, selected_finger, label))
                print(f"✓ Agregado: {label} - {selected_finger}")
            else:
                print("Opción inválida")
        except ValueError:
            print("Por favor ingresa un número válido")
    
    return fingerprints

def list_enrolled_fingers():
    """Función para listar todas las huellas enrolladas automáticamente"""
    global fingerprints_with_labels
    
    try:
        bus = SystemBus()
        fprintd_root = bus.get("net.reactivated.Fprint", "/net/reactivated/Fprint")
        managed_objects = fprintd_root.GetManagedObjects()
        
        devices = [path for path, interfaces in managed_objects.items() 
                  if 'net.reactivated.Fprint.Device' in interfaces]
        
        if not devices:
            print("No fingerprint devices found!")
            return
        
        device_path = devices[0]
        fprintd_device = bus.get("net.reactivated.Fprint", device_path)
        
        print("\n=== HUELLAS ENROLLADAS - TODOS LOS USUARIOS ===")
        
        # Obtener todos los usuarios del sistema
        import subprocess
        import pwd
        
        total_fingerprints = 0
        users_with_fingerprints = 0
        
        # Obtener lista de usuarios del sistema
        try:
            all_users = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]  # Usuarios normales
            all_users.append('root')  # Agregar root también
            all_users = list(set(all_users))  # Eliminar duplicados
            
            print(f"Verificando {len(all_users)} usuarios del sistema...\n")
            
            for username in sorted(all_users):
                try:
                    enrolled_fingers = fprintd_device.ListEnrolledFingers(username)
                    if enrolled_fingers:
                        users_with_fingerprints += 1
                        total_fingerprints += len(enrolled_fingers)
                        print(f"👤 Usuario: {username}")
                        print(f"   📱 Huellas ({len(enrolled_fingers)}):")
                        
                        for i, finger in enumerate(enrolled_fingers, 1):
                            # Buscar etiqueta en archivo
                            label = get_fingerprint_label(username, finger)
                            
                            if label != "Sin etiqueta":
                                print(f"      {i}. {finger} (Etiqueta: {label})")
                            else:
                                print(f"      {i}. {finger}")
                        print()
                except Exception as e:
                    # Silenciar errores para usuarios sin permisos
                    pass
            
            # Mostrar huellas con etiquetas desde archivo
            if fingerprints_with_labels:
                print("🏷️  HUELLAS CON ETIQUETAS (Archivo):")
                for username, finger, label in fingerprints_with_labels:
                    print(f"   • {username}: {finger} -> {label}")
                print()
            
            # Mostrar información del archivo
            if os.path.exists(FINGERPRINTS_FILE):
                full_path = os.path.abspath(FINGERPRINTS_FILE)
                file_size = os.path.getsize(FINGERPRINTS_FILE)
                print(f"📁 Archivo de etiquetas: {full_path}")
                print(f"📊 Tamaño del archivo: {file_size} bytes")
                print()
            
            # Resumen
            print("=" * 50)
            print(f"📊 RESUMEN:")
            print(f"   • Total usuarios con huellas: {users_with_fingerprints}")
            print(f"   • Total huellas enrolladas: {total_fingerprints}")
            print(f"   • Usuarios verificados: {len(all_users)}")
            print(f"   • Huellas con etiquetas (archivo): {len(fingerprints_with_labels)}")
            
            if users_with_fingerprints == 0:
                print("\n⚠️  No se encontraron huellas enrolladas en el sistema")
                
        except Exception as e:
            print(f"Error al obtener usuarios del sistema: {e}")
                
    except Exception as e:
        print(f"Error general: {e}")
        import traceback
        traceback.print_exc()

def on_verify_status_for_identification(result, done):
    """Callback especializado para identificación con una sola huella"""
    global loop, verification_result
    
    if result == "verify-match":
        verification_result = True
        loop.quit()
    elif result == "verify-no-match":
        verification_result = False
        loop.quit()
    elif result == "verify-unknown-error":
        print("⚠️  Error desconocido en verificación")
        verification_result = False
        loop.quit()
    elif result == "verify-retry-scan":
        print("🔄 Vuelve a colocar tu dedo")
    elif result == "verify-swipe-too-short":
        print("⚠️  Deslizamiento muy corto, inténtalo de nuevo")
    elif result == "verify-finger-not-centered":
        print("⚠️  Centra tu dedo en el lector")
    elif result == "verify-remove-and-retry":
        print("🔄 Quita y vuelve a colocar tu dedo")
    else:
        print(f"⚠️  Estado no reconocido: {result}")
        verification_result = False
        loop.quit()

def smart_fingerprint_identification():
    """Identificación inteligente: UN escaneo, identifica usuario y huella específica"""
    global fingerprints_with_labels, verification_result, loop
    
    try:
        bus = SystemBus()
        fprintd_root = bus.get("net.reactivated.Fprint", "/net/reactivated/Fprint")
        managed_objects = fprintd_root.GetManagedObjects()
        
        devices = [path for path, interfaces in managed_objects.items() 
                  if 'net.reactivated.Fprint.Device' in interfaces]
        
        if not devices:
            print("❌ No se encontraron dispositivos de huella")
            return None
        
        device_path = devices[0]
        fprintd_device = bus.get("net.reactivated.Fprint", device_path)
        
        print("\n🎯 IDENTIFICACIÓN INTELIGENTE - UN SOLO ESCANEO")
        print("=" * 55)
        
        # Recopilar usuarios con huellas
        import pwd
        all_users = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]
        all_users.append('root')
        all_users = list(set(all_users))
        
        users_with_fingerprints = []
        total_fingerprints = 0
        
        for username in sorted(all_users):
            try:
                enrolled_fingers = fprintd_device.ListEnrolledFingers(username)
                if enrolled_fingers:
                    users_with_fingerprints.append((username, enrolled_fingers))
                    total_fingerprints += len(enrolled_fingers)
            except:
                pass
        
        if not users_with_fingerprints:
            print("❌ No hay huellas enrolladas en el sistema")
            return None
        
        print(f"📊 Sistema preparado para identificar entre {total_fingerprints} huellas")
        print(f"👥 {len(users_with_fingerprints)} usuarios con huellas registradas")
        
        # Mostrar huellas disponibles
        print(f"\n📋 HUELLAS REGISTRADAS:")
        for username, fingers in users_with_fingerprints:
            print(f"\n👤 {username}:")
            for finger in fingers:
                label = get_fingerprint_label(username, finger)
                print(f"   • {finger} ({label})")
        
        print(f"\n" + "🔥"*50)
        print("👆 COLOCA TU DEDO EN EL LECTOR UNA SOLA VEZ")
        print("⚡ Se identificará automáticamente contra TODAS las huellas")
        print("🔥"*50)
        
        input("\n➤ Presiona Enter cuando estés listo...")
        
        # Probar con cada usuario usando "any" para verificar todas sus huellas de una vez
        for username, fingers in users_with_fingerprints:
            print(f"\n🔍 Verificando contra usuario: {username}")
            print(f"   📱 Comparando con {len(fingers)} huellas simultáneamente...")
            print("   👆 Mantén tu dedo en el lector...")
            
            timeout_id = None
            timeout_triggered = False
            
            def timeout_callback():
                nonlocal timeout_triggered
                timeout_triggered = True
                loop.quit()
                return False  # Remove timeout
            
            try:
                verification_result = False
                
                # Claim device para este usuario
                fprintd_device.Claim(username)
                
                # Usar "any" para verificar contra TODAS las huellas del usuario de una vez
                fprintd_device.VerifyStart("any")
                
                # Crear bucle de eventos LIMPIO
                loop = GLib.MainLoop()
                
                # Timeout de 10 segundos (más tiempo)
                timeout_id = GLib.timeout_add_seconds(10, timeout_callback)
                
                # USAR UN NUEVO BUS PARA EVITAR CALLBACKS ACUMULADOS
                fresh_bus = SystemBus()
                fresh_device = fresh_bus.get("net.reactivated.Fprint", device_path)
                fresh_device.VerifyStatus.connect(on_verify_status_for_identification)
                
                loop.run()
                
                # Limpiar timeout de forma segura
                if timeout_id and not timeout_triggered:
                    try:
                        GLib.source_remove(timeout_id)
                    except:
                        pass  # Timeout ya fue removido
                timeout_id = None
                
                # Parar verificación
                try:
                    fprintd_device.VerifyStop()
                    fprintd_device.Release()
                except:
                    pass
                
                if timeout_triggered:
                    print("   ⏰ Tiempo agotado - no se detectó huella")
                elif verification_result:
                    # ¡Encontramos al usuario! Ahora identificar la huella específica
                    print(f"   ✅ ¡Usuario identificado: {username}!")
                    print(f"   🔍 Identificando huella específica...")
                    
                    # Ahora verificar cada huella individual para saber cuál es
                    for finger in fingers:
                        print(f"      🔄 Verificando si es: {finger}")
                        
                        finger_timeout_id = None
                        finger_timeout_triggered = False
                        
                        def finger_timeout_callback():
                            nonlocal finger_timeout_triggered
                            finger_timeout_triggered = True
                            loop.quit()
                            return False
                        
                        try:
                            fprintd_device.Claim(username)
                            fprintd_device.VerifyStart(finger)
                            
                            loop = GLib.MainLoop()
                            finger_timeout_id = GLib.timeout_add_seconds(5, finger_timeout_callback)
                            
                            # Nuevo bus para esta verificación específica
                            finger_bus = SystemBus()
                            finger_device = finger_bus.get("net.reactivated.Fprint", device_path)
                            finger_device.VerifyStatus.connect(on_verify_status_for_identification)
                            
                            loop.run()
                            
                            # Limpiar timeout de forma segura
                            if finger_timeout_id and not finger_timeout_triggered:
                                try:
                                    GLib.source_remove(finger_timeout_id)
                                except:
                                    pass
                            finger_timeout_id = None
                            
                            try:
                                fprintd_device.VerifyStop()
                                fprintd_device.Release()
                            except:
                                pass
                            
                            if finger_timeout_triggered:
                                print("      ⏰ Timeout - continuando...")
                                continue
                            elif verification_result:
                                label = get_fingerprint_label(username, finger)
                                
                                print(f"\n" + "🎯"*30)
                                print(f"🎉 ¡HUELLA COMPLETAMENTE IDENTIFICADA!")
                                print(f"👤 Usuario: {username}")
                                print(f"👆 Dedo: {finger}")
                                print(f"🏷️  Etiqueta: {label}")
                                print(f"⏱️  Proceso completado exitosamente")
                                print(f"🎯"*30)
                                
                                return {
                                    'username': username,
                                    'finger': finger,
                                    'label': label,
                                    'success': True,
                                    'method': 'smart_identification'
                                }
                            
                        except Exception as e:
                            print(f"         ⚠️ Error: {e}")
                            try:
                                if finger_timeout_id:
                                    GLib.source_remove(finger_timeout_id)
                                fprintd_device.VerifyStop()
                                fprintd_device.Release()
                            except:
                                pass
                            continue
                    
                    # Si llegamos aquí, el usuario coincidió pero no pudimos identificar la huella específica
                    print(f"   ⚠️ Se identificó el usuario {username} pero no la huella específica")
                    return {
                        'username': username,
                        'finger': 'unknown',
                        'label': 'Identificación parcial',
                        'success': True,
                        'method': 'partial_identification'
                    }
                else:
                    print(f"   ❌ No coincide con {username}")
                
            except Exception as e:
                print(f"   ⚠️ Error verificando {username}: {e}")
                try:
                    if timeout_id:
                        GLib.source_remove(timeout_id)
                    fprintd_device.VerifyStop()
                    fprintd_device.Release()
                except:
                    pass
                continue
        
        print(f"\n" + "❌"*30)
        print(f"❌ Tu huella no está registrada en el sistema")
        print(f"📊 Se verificó contra {len(users_with_fingerprints)} usuarios")
        print(f"❌"*30)
        
        return {
            'username': None,
            'finger': None,
            'label': None,
            'success': False,
            'method': 'no_match'
        }
        
    except Exception as e:
        print(f"Error en identificación inteligente: {e}")
        import traceback
        traceback.print_exc()
        return None

# También agregar la función que falta verify_with_label_identification
def verify_with_label_identification(device, username):
    """Función para verificar huella con identificación de etiqueta"""
    global fingerprints_with_labels, verification_result, loop
    
    try:
        enrolled_fingers = device.ListEnrolledFingers(username)
        if not enrolled_fingers:
            print(f"❌ No hay huellas enrolladas para {username}")
            return None
        
        print(f"\n🔍 IDENTIFICACIÓN CON ETIQUETA - {username}")
        print("=" * 50)
        print(f"Huellas disponibles para {username}:")
        
        for i, finger in enumerate(enrolled_fingers, 1):
            label = get_fingerprint_label(username, finger)
            print(f"{i}. {finger} - {label}")
        
        print(f"\n👆 Coloca tu dedo en el lector...")
        print("🔄 Se identificará automáticamente...")
        
        device.Claim(username)
        
        for finger in enrolled_fingers:
            try:
                verification_result = False
                
                device.VerifyStart(finger)
                
                loop = GLib.MainLoop()
                timeout_id = GLib.timeout_add_seconds(8, lambda: loop.quit())
                
                device.VerifyStatus.connect(on_verify_status_with_identification)
                
                loop.run()
                
                GLib.source_remove(timeout_id)
                device.VerifyStop()
                
                if verification_result:
                    label = get_fingerprint_label(username, finger)
                    print(f"\n✅ ¡Huella identificada!")
                    print(f"👤 Usuario: {username}")
                    print(f"👆 Dedo: {finger}")
                    print(f"🏷️  Etiqueta: {label}")
                    
                    device.Release()
                    return {
                        'username': username,
                        'finger': finger,
                        'label': label,
                        'success': True
                    }
                
            except Exception as e:
                print(f"Error verificando {finger}: {e}")
                continue
        
        device.Release()
        print(f"❌ No se pudo identificar la huella de {username}")
        return {'success': False}
        
    except Exception as e:
        print(f"Error en verificación: {e}")
        return None

def main_menu():
    """Función principal del menú"""
    while True:
        print("\n" + "="*50)
        print("🔒 SISTEMA DE GESTIÓN DE HUELLAS DACTILARES")
        print("="*50)
        print("¿Qué acción deseas realizar?")
        print("1. Enrollar nueva huella (usuario actual)")
        print("2. Enrollar múltiples huellas (múltiples usuarios)")
        print("3. Enrollar múltiples huellas con etiquetas (usuario actual)")
        print("4. Verificar huella existente")
        print("5. Ver huellas guardadas")
        print("6. Identificar huella con etiqueta (usuario específico)")
        print("7. Identificar huella entre todos los usuarios")
        print("8. Identificación inteligente (UN escaneo) ⭐")
        print("9. Identificación ultra rápida ⚡")
        print("10. Gestionar etiquetas")
        print("0. Salir")
        
        choice = input("Selecciona una opción (0-10): ").strip()
        
        if choice == "0":
            print("¡Hasta luego!")
            break
        elif choice in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
            return choice
        else:
            print("⚠️  Opción no válida. Por favor selecciona un número del 0 al 10.")

try:
    # Cargar etiquetas al inicio
    load_fingerprints_labels()
    
    bus = SystemBus()
    
    # Use ObjectManager to get all managed objects
    fprintd_root = bus.get("net.reactivated.Fprint", "/net/reactivated/Fprint")
    managed_objects = fprintd_root.GetManagedObjects()
    
    print("Available objects:")
    for obj_path, interfaces in managed_objects.items():
        print(f"  {obj_path}: {list(interfaces.keys())}")
    
    # Find device objects
    devices = [path for path, interfaces in managed_objects.items() 
              if 'net.reactivated.Fprint.Device' in interfaces]
    
    if not devices:
        print("No fingerprint devices found!")
        sys.exit(1)
    
    print(f"Found devices: {devices}")
    
    # Use the first device
    device_path = devices[0]
    fprintd_device = bus.get("net.reactivated.Fprint", device_path)
    
    # Conectar señales
    fprintd_device.EnrollStatus.connect(on_enroll_status)
    fprintd_device.VerifyStatus.connect(on_verify_status)
    
    # Bucle principal del menú
    while True:
        choice = main_menu()
        
        if choice == "1":
            print("Claiming device...")
            fprintd_device.Claim('')  # Empty string for current user
            
            print("\nIniciando enrollment...")
            print("Coloca tu dedo en el lector varias veces cuando se te indique...")
            fprintd_device.EnrollStart("right-index-finger")
            
            # Crear bucle de eventos para escuchar señales
            loop = GLib.MainLoop()
            GLib.timeout_add_seconds(60, lambda: loop.quit())
            
            print("Esperando enrollment... (60 segundos máximo)")
            loop.run()
            print("Finalizando enrollment...")
            fprintd_device.EnrollStop()
            fprintd_device.Release()
            
        elif choice == "2":
            # Multiple enrollment
            enrollments = multiple_enrollment()
            
            if not enrollments:
                print("No se seleccionaron enrollments")
                continue
            
            for username, finger in enrollments:
                try:
                    enroll_fingerprint(fprintd_device, username, finger)
                    print(f"✓ Completado: {username} - {finger}")
                except Exception as e:
                    print(f"✗ Error con {username} - {finger}: {e}")
            
            print("\n¡Todos los enrollments completados!")
            
        elif choice == "3":
            # Multiple enrollment with labels
            enrollments = multiple_enrollment_with_labels()
            
            if not enrollments:
                print("No se seleccionaron enrollments")
                continue
            
            for username, finger, label in enrollments:
                try:
                    enroll_fingerprint_with_label(fprintd_device, username, finger, label)
                    print(f"✓ Completado: {label} - {finger}")
                except Exception as e:
                    print(f"✗ Error con {label} - {finger}: {e}")
            
            print("\n¡Todos los enrollments con etiquetas completados!")
            
        elif choice == "4":
            print("Claiming device...")
            fprintd_device.Claim('')  # Empty string for current user
            
            print("\nIniciando verificación...")
            print("Coloca tu dedo en el lector...")
            fprintd_device.VerifyStart("any")
            
            # Crear bucle de eventos para escuchar señales
            loop = GLib.MainLoop()
            GLib.timeout_add_seconds(60, lambda: loop.quit())
            
            print("Esperando verificación... (60 segundos máximo)")
            loop.run()
            print("Finalizando verificación...")
            fprintd_device.VerifyStop()
            fprintd_device.Release()
            
        elif choice == "5":
            list_enrolled_fingers()
        
        elif choice == "6":
            # Identificar huella con etiqueta (usuario específico)
            username = input("Ingresa el nombre de usuario (vacío para usuario actual): ").strip()
            if not username:
                username = getpass.getuser()
            
            result = verify_with_label_identification(fprintd_device, username)
            
        elif choice == "7":
            # Identificar huella entre todos los usuarios (versión mejorada)
            identify_fingerprint_from_all_users()
            
        elif choice == "8":
            # Identificación inteligente
            result = smart_fingerprint_identification()
            
        elif choice == "9":
            # Identificación ultra rápida
            result = ultra_fast_identification()
            
        elif choice == "10":
            # Gestionar etiquetas
            manage_labels_menu()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Guardar etiquetas al salir
    save_fingerprints_labels()
