import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from db import get_connection

class CocineroDashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title(f"Dashboard Cocinero - {username}")
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

        # Mostrar la vista de comandas por defecto
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

        # Botón Recetas
        recetas_btn = ttk.Button(nav_frame, text="Recetas", 
                                 command=self.show_recetas_view, 
                                 style="Nav.TButton")
        recetas_btn.pack(side=tk.LEFT, padx=2)

        # Botón Stock
        stock_btn = ttk.Button(nav_frame, text="Stock", 
                               command=self.show_stock_view, 
                               style="Nav.TButton")
        stock_btn.pack(side=tk.LEFT, padx=2)

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
                info_label.pack(pady=5)
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
        
        # Obtener datos de comandas
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, m.numero, c.fecha, c.estado, SUM(p.precio * dc.cantidad) as total
                FROM comandas c
                JOIN mesas m ON c.id_mesa = m.id
                JOIN detalle_comanda dc ON c.id = dc.id_comanda
                JOIN platos p ON dc.id_plato = p.id
                GROUP BY c.id
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

        # Agregar botones de acción
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Ver Detalles", command=lambda: self.ver_detalles(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cambiar Estado", command=lambda: self.cambiar_estado(tree)).pack(side=tk.LEFT, padx=5)
        
        tree.pack(fill=tk.BOTH, expand=True)

    def ver_detalles(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una comanda")
            return
        
        # Obtener datos de la comanda seleccionada
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana para ver detalles
        detalles_window = tk.Toplevel(self.root)
        detalles_window.title(f"Detalles Comanda - Mesa {values[1]}")
        detalles_window.geometry("600x400")
        
        # Crear Treeview para mostrar detalles
        columns = ("Plato", "Cantidad", "Precio", "Subtotal")
        tree = ttk.Treeview(detalles_window, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Obtener detalles de la comanda
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.nombre, dc.cantidad, p.precio, (p.precio * dc.cantidad) as subtotal
                FROM detalle_comanda dc
                JOIN platos p ON dc.id_plato = p.id
                WHERE dc.id_comanda = %s
            """, (values[0],))
            
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def cambiar_estado(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una comanda")
            return
        
        # Obtener datos de la comanda seleccionada
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana para cambiar estado
        estado_window = tk.Toplevel(self.root)
        estado_window.title("Cambiar Estado de Comanda")
        estado_window.geometry("300x200")
        
        ttk.Label(estado_window, text="Nuevo Estado:").pack(pady=5)
        estado_var = tk.StringVar(value=values[3])
        estados = ["pendiente", "en preparación", "servido"]
        estado_combo = ttk.Combobox(estado_window, textvariable=estado_var, values=estados, state="readonly")
        estado_combo.pack(pady=5)
        
        def guardar_estado():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE comandas SET estado = %s WHERE id = %s",
                    (estado_var.get(), values[0])
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Estado actualizado correctamente")
                estado_window.destroy()
                self.show_comandas_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar estado: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(estado_window, text="Guardar", command=guardar_estado).pack(pady=20)

    def show_recetas_view(self):
        self.clear_main_frame()
        columns = ("ID", "Plato", "Producto", "Cantidad", "Unidad")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, p.nombre, pr.nombre, r.cantidad, pr.unidad
                FROM recetas r
                JOIN platos p ON r.id_plato = p.id
                JOIN productos pr ON r.id_producto = pr.id
                ORDER BY p.nombre, pr.nombre
            """)
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar recetas: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def show_stock_view(self):
        self.clear_main_frame()
        columns = ("ID", "Nombre", "Unidad", "Stock", "Stock Mínimo")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, unidad, stock, stock_minimo FROM productos")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10) 