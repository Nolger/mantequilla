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

        # Frame para la barra superior
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botón de cerrar sesión
        ttk.Button(self.top_frame, text="Cerrar Sesión", command=self.logout).pack(side=tk.RIGHT, padx=5)
        
        # Mostrar información del usuario actual
        self.show_user_info()

        # Crear el menú principal
        self.create_menu()
        
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Mostrar la vista de mesas por defecto
        self.show_mesas_view()

    def show_user_info(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, rol FROM empleados WHERE usuario = %s", (self.username,))
            result = cursor.fetchone()
            if result:
                nombre, rol = result
                info_label = ttk.Label(self.top_frame, text=f"Usuario: {nombre} | Rol: {rol}")
                info_label.pack(side=tk.LEFT, padx=5)
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

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Menú Mesas
        mesas_menu = tk.Menu(menubar, tearoff=0)
        mesas_menu.add_command(label="Ver Mesas", command=self.show_mesas_view)
        menubar.add_cascade(label="Mesas", menu=mesas_menu)

        # Menú Menú
        menu_menu = tk.Menu(menubar, tearoff=0)
        menu_menu.add_command(label="Ver Platos", command=self.show_platos_view)
        menubar.add_cascade(label="Menú", menu=menu_menu)

        self.root.config(menu=menubar)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_mesas_view(self):
        self.clear_main_frame()
        
        # Crear Treeview para mostrar mesas
        columns = ("ID", "Número", "Capacidad", "Estado")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Obtener datos de mesas
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

        # Agregar botones de acción
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Tomar Orden", command=lambda: self.tomar_orden(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Ver Comandas", command=lambda: self.ver_comandas(tree)).pack(side=tk.LEFT, padx=5)
        
        tree.pack(fill=tk.BOTH, expand=True)

    def tomar_orden(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una mesa")
            return
        
        # Obtener datos de la mesa seleccionada
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana para tomar orden
        order_window = tk.Toplevel(self.root)
        order_window.title(f"Tomar Orden - Mesa {values[1]}")
        order_window.geometry("800x600")
        
        # Frame para platos
        platos_frame = ttk.Frame(order_window)
        platos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Obtener lista de platos
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, precio FROM platos")
            platos = cursor.fetchall()
            
            # Crear lista de platos con checkboxes
            platos_vars = []
            for plato in platos:
                var = tk.BooleanVar()
                platos_vars.append((var, plato))
                ttk.Checkbutton(platos_frame, text=f"{plato[1]} - ${plato[2]}", variable=var).pack(anchor=tk.W)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar platos: {str(e)}")
            return
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        def guardar_orden():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Crear comanda
                cursor.execute(
                    "INSERT INTO comandas (id_mesa, estado) VALUES (%s, %s)",
                    (values[0], "pendiente")
                )
                comanda_id = cursor.lastrowid
                
                # Agregar platos a la comanda
                for var, plato in platos_vars:
                    if var.get():
                        cursor.execute(
                            "INSERT INTO detalle_comanda (id_comanda, id_plato, cantidad) VALUES (%s, %s, %s)",
                            (comanda_id, plato[0], 1)  # Por ahora cantidad fija a 1
                        )
                
                conn.commit()
                messagebox.showinfo("Éxito", "Orden registrada correctamente")
                order_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar orden: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

        ttk.Button(order_window, text="Guardar Orden", command=guardar_orden).pack(pady=20)

    def ver_comandas(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una mesa")
            return
        
        # Obtener datos de la mesa seleccionada
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana para ver comandas
        comandas_window = tk.Toplevel(self.root)
        comandas_window.title(f"Comandas - Mesa {values[1]}")
        comandas_window.geometry("800x600")
        
        # Crear Treeview para mostrar comandas
        columns = ("ID", "Fecha", "Estado", "Total")
        tree = ttk.Treeview(comandas_window, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Obtener comandas de la mesa
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.fecha, c.estado, SUM(p.precio * dc.cantidad) as total
                FROM comandas c
                JOIN detalle_comanda dc ON c.id = dc.id_comanda
                JOIN platos p ON dc.id_plato = p.id
                WHERE c.id_mesa = %s
                GROUP BY c.id
            """, (values[0],))
            
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