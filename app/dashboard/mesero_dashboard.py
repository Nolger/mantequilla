import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from db import get_connection

class MeseroDashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title(f"Dashboard Mesero - {username}")
        self.root.geometry("1200x800")

        # Configurar estilos base (tema claro)
        self.configure_styles()

        # Crear la barra de navegación
        self.create_menu()

        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Mostrar información del usuario actual
        self.show_user_info()

        # Mostrar la vista principal por defecto
        self.show_comandas_view()

    def configure_styles(self):
        style = ttk.Style()
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", foreground="#000000")
        style.configure("Nav.TFrame", background="#f0f0f0")
        style.configure("Nav.TButton", 
                        padding=10, 
                        font=('Helvetica', 10),
                        background="#f0f0f0",
                        foreground="#000000")
        style.map("Nav.TButton",
                  background=[('active', '#e0e0e0')],
                  foreground=[('active', '#000000')])
        style.configure("TLabelframe", 
                        background="#ffffff",
                        foreground="#000000",
                        bordercolor="#cccccc")
        style.configure("TLabelframe.Label", 
                        background="#ffffff",
                        foreground="#000000")
        style.configure("TFrame", bordercolor="#cccccc")
        style.configure("Treeview", 
                        background="#ffffff",
                        foreground="#000000",
                        fieldbackground="#ffffff",
                        bordercolor="#cccccc")
        style.configure("Treeview.Heading", 
                        background="#f0f0f0",
                        foreground="#000000")
        style.configure("TSeparator", background="#d3d3d3")

    def create_menu(self):
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill=tk.X, padx=10, pady=5)
        nav_frame.configure(style="Nav.TFrame")

        # Botón Comandas
        comandas_btn = ttk.Button(nav_frame, text="Comandas", 
                                  command=self.show_comandas_view, 
                                  style="Nav.TButton")
        comandas_btn.pack(side=tk.LEFT, padx=2)

        # Botón Platos
        platos_btn = ttk.Button(nav_frame, text="Platos", 
                                command=self.show_platos_view, 
                                style="Nav.TButton")
        platos_btn.pack(side=tk.LEFT, padx=2)

        # Botón Tomar Orden
        tomar_orden_btn = ttk.Button(nav_frame, text="Tomar Orden", 
                                     command=self.show_tomar_orden_view, 
                                     style="Nav.TButton")
        tomar_orden_btn.pack(side=tk.LEFT, padx=2)

        # Botón Mesas
        mesas_btn = ttk.Button(nav_frame, text="Mesas", 
                               command=self.show_mesas_view, 
                               style="Nav.TButton")
        mesas_btn.pack(side=tk.LEFT, padx=2)

        # Botón de cerrar sesión al final
        logout_btn = ttk.Button(nav_frame, text="Cerrar Sesión", 
                                command=self.logout, 
                                style="Nav.TButton")
        logout_btn.pack(side=tk.RIGHT, padx=2)

        # Separador visual
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill=tk.X, padx=10, pady=5)

    def show_user_info(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, rol FROM empleados WHERE usuario = %s", (self.username,))
            result = cursor.fetchone()
            if result:
                nombre, rol = result
                info_label = ttk.Label(self.main_frame, text=f"Usuario: {nombre} | Rol: {rol}")
                info_label.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar información del usuario: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def logout(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro que desea cerrar sesión?"):
            self.root.destroy()
            # Importar aquí para evitar importación circular
            from main import LoginApp
            login_window = tk.Tk()
            app = LoginApp(login_window)
            login_window.mainloop()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_comandas_view(self):
        self.clear_main_frame()
        
        # Crear Treeview para mostrar comandas
        columns = ("ID", "Mesa", "Fecha", "Estado", "Total")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Obtener todas las comandas de todas las mesas
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, m.numero, c.fecha, c.estado, SUM(p.precio * dc.cantidad) as total
                FROM comandas c
                JOIN mesas m ON c.id_mesa = m.id
                JOIN detalle_comanda dc ON c.id = dc.id_comanda
                JOIN platos p ON dc.id_plato = p.id
                GROUP BY c.id, m.numero, c.fecha, c.estado
                ORDER BY c.fecha DESC
            """)
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar comandas: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show_platos_view(self):
        self.clear_main_frame()
        
        # Crear Treeview para mostrar platos
        columns = ("ID", "Nombre", "Precio")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Obtener datos de platos
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, precio FROM platos")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar platos: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        
        tree.pack(fill=tk.BOTH, expand=True)

    def show_mesas_view(self):
        self.clear_main_frame()
        columns = ("ID", "Número", "Capacidad")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, numero, capacidad FROM mesas")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar mesas: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show_tomar_orden_view(self):
        self.clear_main_frame()
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        # Selección de mesa
        ttk.Label(form_frame, text="Mesa:").grid(row=0, column=0, padx=5, pady=5)
        mesa_var = tk.StringVar()
        mesa_combo = ttk.Combobox(form_frame, textvariable=mesa_var)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, numero FROM mesas")
            mesas = cursor.fetchall()
            mesa_combo['values'] = [f"{m[0]} - {m[1]}" for m in mesas]
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar mesas: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        mesa_combo.grid(row=0, column=1, padx=5, pady=5)
        # Selección de platos
        ttk.Label(form_frame, text="Platos:").grid(row=1, column=0, padx=5, pady=5)
        platos_frame = ttk.Frame(form_frame)
        platos_frame.grid(row=1, column=1, padx=5, pady=5)
        platos_vars = []
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, precio FROM platos")
            platos = cursor.fetchall()
            for i, plato in enumerate(platos):
                var = tk.IntVar()
                platos_vars.append((var, plato))
                ttk.Checkbutton(platos_frame, text=f"{plato[1]} - ${plato[2]}", variable=var).pack(anchor=tk.W)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar platos: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        def guardar_orden():
            if not mesa_var.get():
                messagebox.showwarning("Advertencia", "Seleccione una mesa")
                return
            mesa_id = int(mesa_var.get().split(" - ")[0])
            platos_seleccionados = [plato for var, plato in platos_vars if var.get()]
            if not platos_seleccionados:
                messagebox.showwarning("Advertencia", "Seleccione al menos un plato")
                return
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO comandas (id_mesa, estado, fecha) VALUES (%s, %s, NOW())",
                    (mesa_id, "pendiente")
                )
                comanda_id = cursor.lastrowid
                for var, plato in platos_vars:
                    if var.get():
                        cursor.execute(
                            "INSERT INTO detalle_comanda (id_comanda, id_plato, cantidad) VALUES (%s, %s, %s)",
                            (comanda_id, plato[0], 1)
                        )
                conn.commit()
                messagebox.showinfo("Éxito", "Orden registrada correctamente")
                self.show_comandas_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar orden: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        ttk.Button(form_frame, text="Guardar Orden", command=guardar_orden).grid(row=2, column=0, columnspan=2, pady=20) 