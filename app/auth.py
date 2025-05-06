import hashlib
import os
from tkinter import messagebox
from db import get_connection

# --- Configuración de Seguridad ---
HASH_ALGORITHM = 'sha256'
ITERATIONS = 100000
SALT_LENGTH = 16

def generate_salt(length=SALT_LENGTH):
    """Genera una sal criptográficamente segura."""
    return os.urandom(length)

def hash_password(password, salt, iterations=ITERATIONS, hash_name=HASH_ALGORITHM):
    """Hashea la contraseña usando PBKDF2 con la sal proporcionada."""
    password_bytes = password.encode('utf-8')
    pwd_hash = hashlib.pbkdf2_hmac(
        hash_name,
        password_bytes,
        salt,
        iterations
    )
    return pwd_hash

def verify_password(stored_salt, stored_hash, provided_password, iterations=ITERATIONS, hash_name=HASH_ALGORITHM):
    """Verifica una contraseña proporcionada contra el hash y la sal almacenados."""
    provided_hash = hash_password(provided_password, stored_salt, iterations, hash_name)
    return stored_hash == provided_hash

def is_admin(username):
    """Verifica si un usuario es administrador."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rol FROM empleados WHERE usuario = %s",
            (username,)
        )
        result = cursor.fetchone()
        return result and result[0] == 'administrador'
    except Exception as e:
        print(f"Error al verificar rol de administrador: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def register_user(username, password, nombre, rol='mesero'):
    """Registra un nuevo empleado en la base de datos."""
    if not username or not password or not nombre:
        messagebox.showerror("Error de Registro", "Todos los campos son obligatorios.")
        return False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si el usuario ya existe
        cursor.execute("SELECT usuario FROM empleados WHERE usuario = %s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error de Registro", f"El usuario '{username}' ya existe.")
            return False

        # Generar salt y hash
        salt = generate_salt()
        hashed = hash_password(password, salt)

        # Insertar nuevo empleado
        cursor.execute(
            "INSERT INTO empleados (nombre, rol, usuario, contrasena, salt) VALUES (%s, %s, %s, %s, %s)",
            (nombre, rol, username, hashed.hex(), salt.hex())
        )
        conn.commit()
        messagebox.showinfo("Registro Exitoso", f"Empleado '{nombre}' registrado correctamente.")
        return True

    except Exception as e:
        messagebox.showerror("Error de Registro", f"Error al registrar empleado: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def attempt_login(username, password):
    """Intenta iniciar sesión con los datos proporcionados."""
    if not username or not password:
        messagebox.showerror("Error de Login", "Por favor, ingresa usuario y contraseña.")
        return False, None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT contrasena, salt, rol, nombre FROM empleados WHERE usuario = %s",
            (username,)
        )
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Login Fallido", f"Usuario '{username}' no encontrado.")
            return False, None

        stored_hash = bytes.fromhex(result[0])
        stored_salt = bytes.fromhex(result[1])
        rol = result[2]
        nombre = result[3]

        if verify_password(stored_salt, stored_hash, password):
            messagebox.showinfo("Login Exitoso", f"¡Bienvenido, {nombre}!")
            return True, rol
        else:
            messagebox.showerror("Login Fallido", "Contraseña incorrecta.")
            return False, None

    except Exception as e:
        messagebox.showerror("Error de Login", f"Error al iniciar sesión: {str(e)}")
        return False, None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def create_admin_user():
    """Crea el usuario administrador por defecto si no existe."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar si el admin ya existe
        cursor.execute("SELECT usuario FROM empleados WHERE usuario = 'admin'")
        if not cursor.fetchone():
            # Crear el usuario administrador
            salt = generate_salt()
            hashed = hash_password("123", salt)
            cursor.execute(
                "INSERT INTO empleados (nombre, rol, usuario, contrasena, salt) VALUES (%s, %s, %s, %s, %s)",
                ("Administrador Principal", "administrador", "admin", hashed.hex(), salt.hex())
            )
            conn.commit()
            print("✅ Usuario administrador creado correctamente")
    except Exception as e:
        print(f"❌ Error al crear usuario administrador: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close() 