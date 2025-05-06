import tkinter as tk
from auth import attempt_login, register_user, is_admin, create_admin_user
from dashboard.admin_dashboard import AdminDashboard
from dashboard.mesero_dashboard import MeseroDashboard
from dashboard.cocinero_dashboard import CocineroDashboard

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Restaurante - Login")
        self.root.geometry("300x200")

        # Crear usuario administrador por defecto si no existe
        create_admin_user()

        # Widgets
        tk.Label(root, text="Usuario:").pack(pady=5)
        self.entry_username = tk.Entry(root, width=30)
        self.entry_username.pack()

        tk.Label(root, text="Contraseña:").pack(pady=5)
        self.entry_password = tk.Entry(root, show="*", width=30)
        self.entry_password.pack()

        btn_login = tk.Button(root, text="Iniciar Sesión", command=self.login)
        btn_login.pack(pady=20)

        # El botón de registro se mostrará solo después de iniciar sesión como admin
        self.btn_register = None

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        success, rol = attempt_login(username, password)
        if success:
            # Cerrar la ventana de login
            self.root.destroy()
            
            # Crear nueva ventana para el dashboard
            dashboard_root = tk.Tk()
            
            # Inicializar el dashboard correspondiente según el rol
            if rol == 'administrador':
                AdminDashboard(dashboard_root, username)
            elif rol == 'mesero':
                MeseroDashboard(dashboard_root, username)
            elif rol == 'cocinero':
                CocineroDashboard(dashboard_root, username)
            # Aquí se pueden agregar más dashboards para otros roles
            
            dashboard_root.mainloop()

    def open_registration(self):
        reg_window = tk.Toplevel(self.root)
        reg_window.title("Registrar Nuevo Empleado")
        reg_window.geometry("300x350")

        tk.Label(reg_window, text="Nombre del Empleado:").pack(pady=5)
        entry_nombre = tk.Entry(reg_window, width=30)
        entry_nombre.pack()

        tk.Label(reg_window, text="Usuario:").pack(pady=5)
        entry_username = tk.Entry(reg_window, width=30)
        entry_username.pack()

        tk.Label(reg_window, text="Contraseña:").pack(pady=5)
        entry_password = tk.Entry(reg_window, show="*", width=30)
        entry_password.pack()

        tk.Label(reg_window, text="Rol:").pack(pady=5)
        rol_var = tk.StringVar(value="mesero")
        rol_frame = tk.Frame(reg_window)
        rol_frame.pack()
        
        roles = [
            ("Mesero", "mesero"),
            ("Cocinero", "cocinero"),
            ("Personal de Aseo", "aseo"),
            ("Domiciliario", "domiciliario")
        ]
        
        for text, value in roles:
            tk.Radiobutton(rol_frame, text=text, variable=rol_var, value=value).pack(anchor=tk.W)

        def do_register():
            nombre = entry_nombre.get()
            username = entry_username.get()
            password = entry_password.get()
            rol = rol_var.get()
            if register_user(username, password, nombre, rol):
                reg_window.destroy()

        btn_register = tk.Button(reg_window, text="Registrar", command=do_register)
        btn_register.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()