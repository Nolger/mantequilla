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

        # Frame para la barra superior
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botón de cerrar sesión
        ttk.Button(self.top_frame, text="Cerrar Sesión", command=self.logout).pack(side=tk.RIGHT, padx=5)
        
        # Mostrar información del usuario actual
        self.show_user_info()

        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Mostrar la vista de comandas por defecto
        self.show_comandas_view()

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
        estados = ["pendiente", "en preparación", "listo", "entregado"]
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