import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from db import get_connection
from auth import hash_password, generate_salt, register_user

class AdminDashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title(f"Dashboard Administrador - {username}")
        self.root.geometry("1200x800")

        # Crear el menú principal
        self.create_menu()
        
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame para la barra superior
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botón de cerrar sesión
        ttk.Button(self.top_frame, text="Cerrar Sesión", command=self.logout).pack(side=tk.RIGHT, padx=5)
        
        # Mostrar información del usuario actual
        self.show_user_info()
        
        # Mostrar la vista de empleados por defecto
        self.show_empleados_view()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Menú Empleados
        empleados_menu = tk.Menu(menubar, tearoff=0)
        empleados_menu.add_command(label="Ver Empleados", command=self.show_empleados_view)
        empleados_menu.add_command(label="Agregar Empleado", command=self.show_add_empleado)
        menubar.add_cascade(label="Empleados", menu=empleados_menu)

        # Menú Mesas
        mesas_menu = tk.Menu(menubar, tearoff=0)
        mesas_menu.add_command(label="Ver Mesas", command=self.show_mesas_view)
        mesas_menu.add_command(label="Agregar Mesa", command=self.show_add_mesa)
        menubar.add_cascade(label="Mesas", menu=mesas_menu)

        # Menú Menú
        menu_menu = tk.Menu(menubar, tearoff=0)
        menu_menu.add_command(label="Ver Platos", command=self.show_platos_view)
        menu_menu.add_command(label="Agregar Plato", command=self.show_add_plato)
        menu_menu.add_command(label="Ver Recetas", command=self.show_recetas_view)
        menubar.add_cascade(label="Menú", menu=menu_menu)

        # Menú Inventario
        inventario_menu = tk.Menu(menubar, tearoff=0)
        inventario_menu.add_command(label="Ver Productos", command=self.show_productos_view)
        inventario_menu.add_command(label="Agregar Producto", command=self.show_add_producto)
        menubar.add_cascade(label="Inventario", menu=inventario_menu)

        # Menú Proveedores
        proveedores_menu = tk.Menu(menubar, tearoff=0)
        proveedores_menu.add_command(label="Ver Proveedores", command=self.show_proveedores_view)
        proveedores_menu.add_command(label="Agregar Proveedor", command=self.show_add_proveedor)
        menubar.add_cascade(label="Proveedores", menu=proveedores_menu)

        self.root.config(menu=menubar)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

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

    def show_empleados_view(self):
        self.clear_main_frame()
        
        # Crear Treeview para mostrar empleados
        columns = ("ID", "Nombre", "Rol", "Usuario")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Obtener datos de empleados
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, rol, usuario FROM empleados")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar empleados: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        # Agregar botones de acción
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Editar", command=lambda: self.edit_empleado(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cambiar Contraseña", command=lambda: self.change_password(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=lambda: self.delete_empleado(tree)).pack(side=tk.LEFT, padx=5)
        
        tree.pack(fill=tk.BOTH, expand=True)

    def change_password(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un empleado")
            return
        
        # Obtener datos del empleado seleccionado
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana para cambiar contraseña
        password_window = tk.Toplevel(self.root)
        password_window.title("Cambiar Contraseña")
        password_window.geometry("300x200")
        
        ttk.Label(password_window, text=f"Cambiar contraseña para {values[1]}").pack(pady=10)
        
        ttk.Label(password_window, text="Nueva Contraseña:").pack(pady=5)
        password_entry = ttk.Entry(password_window, show="*")
        password_entry.pack(pady=5)
        
        ttk.Label(password_window, text="Confirmar Contraseña:").pack(pady=5)
        confirm_entry = ttk.Entry(password_window, show="*")
        confirm_entry.pack(pady=5)
        
        def save_password():
            new_password = password_entry.get()
            confirm_password = confirm_entry.get()
            
            if not new_password or not confirm_password:
                messagebox.showerror("Error", "Por favor ingrese la nueva contraseña")
                return
                
            if new_password != confirm_password:
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Generar nueva sal y hash
                salt = generate_salt()
                hashed = hash_password(new_password, salt)
                
                cursor.execute(
                    "UPDATE empleados SET contrasena = %s, salt = %s WHERE id = %s",
                    (hashed.hex(), salt.hex(), values[0])
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
                password_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar contraseña: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(password_window, text="Guardar", command=save_password).pack(pady=20)

    def edit_empleado(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un empleado")
            return
        
        # Obtener datos del empleado seleccionado
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana de edición
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Empleado")
        edit_window.geometry("300x300")
        
        ttk.Label(edit_window, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(edit_window)
        nombre_entry.insert(0, values[1])
        nombre_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Usuario:").pack(pady=5)
        usuario_entry = ttk.Entry(edit_window)
        usuario_entry.insert(0, values[3])
        usuario_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Rol:").pack(pady=5)
        rol_var = tk.StringVar(value=values[2])
        roles = ["administrador", "mesero", "cocinero", "aseo", "domiciliario"]
        rol_combo = ttk.Combobox(edit_window, textvariable=rol_var, values=roles, state="readonly")
        rol_combo.pack(pady=5)
        
        def save_changes():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE empleados SET nombre = %s, usuario = %s, rol = %s WHERE id = %s",
                    (nombre_entry.get(), usuario_entry.get(), rol_var.get(), values[0])
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Empleado actualizado correctamente")
                edit_window.destroy()
                self.show_empleados_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar empleado: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(edit_window, text="Guardar Cambios", command=save_changes).pack(pady=20)

    def show_mesas_view(self):
        self.clear_main_frame()
        
        # Crear Treeview para mostrar mesas
        columns = ("ID", "Número", "Capacidad")
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
        
        ttk.Button(btn_frame, text="Editar", command=lambda: self.edit_mesa(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=lambda: self.delete_mesa(tree)).pack(side=tk.LEFT, padx=5)
        
        tree.pack(fill=tk.BOTH, expand=True)

    def show_add_mesa(self):
        self.clear_main_frame()
        
        # Formulario para agregar mesa
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Número:").grid(row=0, column=0, padx=5, pady=5)
        numero_entry = ttk.Entry(form_frame)
        numero_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Capacidad:").grid(row=1, column=0, padx=5, pady=5)
        capacidad_entry = ttk.Entry(form_frame)
        capacidad_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def save_mesa():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO mesas (numero, capacidad) VALUES (%s, %s)",
                    (numero_entry.get(), capacidad_entry.get())
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Mesa agregada correctamente")
                self.show_mesas_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar mesa: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(form_frame, text="Guardar", command=save_mesa).grid(row=2, column=0, columnspan=2, pady=20)

    def edit_mesa(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una mesa")
            return
        
        # Obtener datos de la mesa seleccionada
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana de edición
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Mesa")
        edit_window.geometry("300x200")
        
        ttk.Label(edit_window, text="Número:").pack(pady=5)
        numero_entry = ttk.Entry(edit_window)
        numero_entry.insert(0, values[1])
        numero_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Capacidad:").pack(pady=5)
        capacidad_entry = ttk.Entry(edit_window)
        capacidad_entry.insert(0, values[2])
        capacidad_entry.pack(pady=5)
        
        def save_changes():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE mesas SET numero = %s, capacidad = %s WHERE id = %s",
                    (numero_entry.get(), capacidad_entry.get(), values[0])
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Mesa actualizada correctamente")
                edit_window.destroy()
                self.show_mesas_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar mesa: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(edit_window, text="Guardar Cambios", command=save_changes).pack(pady=20)

    def delete_mesa(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una mesa")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta mesa?"):
            item = tree.item(selected[0])
            values = item['values']
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mesas WHERE id = %s", (values[0],))
                conn.commit()
                messagebox.showinfo("Éxito", "Mesa eliminada correctamente")
                self.show_mesas_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar mesa: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

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

        # Agregar botones de acción
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Editar", command=lambda: self.edit_plato(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=lambda: self.delete_plato(tree)).pack(side=tk.LEFT, padx=5)
        
        tree.pack(fill=tk.BOTH, expand=True)

    def show_add_plato(self):
        self.clear_main_frame()
        
        # Formulario para agregar plato
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = ttk.Entry(form_frame)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Precio:").grid(row=1, column=0, padx=5, pady=5)
        precio_entry = ttk.Entry(form_frame)
        precio_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def save_plato():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO platos (nombre, precio) VALUES (%s, %s)",
                    (nombre_entry.get(), precio_entry.get())
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Plato agregado correctamente")
                self.show_platos_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar plato: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(form_frame, text="Guardar", command=save_plato).grid(row=2, column=0, columnspan=2, pady=20)

    def edit_plato(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un plato")
            return
        
        # Obtener datos del plato seleccionado
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana de edición
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Plato")
        edit_window.geometry("300x200")
        
        ttk.Label(edit_window, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(edit_window)
        nombre_entry.insert(0, values[1])
        nombre_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Precio:").pack(pady=5)
        precio_entry = ttk.Entry(edit_window)
        precio_entry.insert(0, values[2])
        precio_entry.pack(pady=5)
        
        def save_changes():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE platos SET nombre = %s, precio = %s WHERE id = %s",
                    (nombre_entry.get(), precio_entry.get(), values[0])
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Plato actualizado correctamente")
                edit_window.destroy()
                self.show_platos_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar plato: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(edit_window, text="Guardar Cambios", command=save_changes).pack(pady=20)

    def delete_plato(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un plato")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este plato?"):
            item = tree.item(selected[0])
            values = item['values']
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM platos WHERE id = %s", (values[0],))
                conn.commit()
                messagebox.showinfo("Éxito", "Plato eliminado correctamente")
                self.show_platos_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar plato: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

    def show_productos_view(self):
        self.clear_main_frame()
        
        # Crear Treeview para mostrar productos
        columns = ("ID", "Nombre", "Unidad", "Stock", "Stock Mínimo", "Proveedor", "Estado")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Obtener datos de productos
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.nombre, p.unidad, p.stock, p.stock_minimo, pr.nombre,
                       CASE 
                           WHEN p.stock <= p.stock_minimo THEN 'Bajo Stock'
                           ELSE 'OK'
                       END as estado
                FROM productos p
                LEFT JOIN proveedores pr ON p.id_proveedor = pr.id
            """)
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
                
                # Notificar si el stock está bajo
                if row[3] <= row[4]:  # stock <= stock_minimo
                    messagebox.showwarning(
                        "Stock Bajo",
                        f"El producto '{row[1]}' tiene stock bajo ({row[3]} {row[2]}). "
                        f"Stock mínimo: {row[4]} {row[2]}"
                    )
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        # Agregar botones de acción
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Editar", command=lambda: self.edit_producto(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=lambda: self.delete_producto(tree)).pack(side=tk.LEFT, padx=5)
        
        tree.pack(fill=tk.BOTH, expand=True)

    def show_add_producto(self):
        self.clear_main_frame()
        
        # Formulario para agregar producto
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = ttk.Entry(form_frame)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Unidad:").grid(row=1, column=0, padx=5, pady=5)
        unidad_entry = ttk.Entry(form_frame)
        unidad_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Stock:").grid(row=2, column=0, padx=5, pady=5)
        stock_entry = ttk.Entry(form_frame)
        stock_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Stock Mínimo:").grid(row=3, column=0, padx=5, pady=5)
        stock_minimo_entry = ttk.Entry(form_frame)
        stock_minimo_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Proveedor:").grid(row=4, column=0, padx=5, pady=5)
        proveedor_var = tk.StringVar()
        proveedor_combo = ttk.Combobox(form_frame, textvariable=proveedor_var)
        
        # Cargar proveedores
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM proveedores")
            proveedores = cursor.fetchall()
            proveedor_combo['values'] = [f"{p[0]} - {p[1]}" for p in proveedores]
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar proveedores: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        
        proveedor_combo.grid(row=4, column=1, padx=5, pady=5)
        
        def save_producto():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Obtener ID del proveedor seleccionado
                proveedor_id = None
                if proveedor_var.get():
                    proveedor_id = int(proveedor_var.get().split(" - ")[0])
                
                cursor.execute(
                    "INSERT INTO productos (nombre, unidad, stock, stock_minimo, id_proveedor) VALUES (%s, %s, %s, %s, %s)",
                    (nombre_entry.get(), unidad_entry.get(), stock_entry.get(), stock_minimo_entry.get(), proveedor_id)
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Producto agregado correctamente")
                self.show_productos_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(form_frame, text="Guardar", command=save_producto).grid(row=5, column=0, columnspan=2, pady=20)

    def edit_producto(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return
        
        # Obtener datos del producto seleccionado
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana de edición
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Producto")
        edit_window.geometry("300x300")
        
        ttk.Label(edit_window, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(edit_window)
        nombre_entry.insert(0, values[1])
        nombre_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Unidad:").pack(pady=5)
        unidad_entry = ttk.Entry(edit_window)
        unidad_entry.insert(0, values[2])
        unidad_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Stock:").pack(pady=5)
        stock_entry = ttk.Entry(edit_window)
        stock_entry.insert(0, values[3])
        stock_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Stock Mínimo:").pack(pady=5)
        stock_minimo_entry = ttk.Entry(edit_window)
        stock_minimo_entry.insert(0, values[4])
        stock_minimo_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Proveedor:").pack(pady=5)
        proveedor_var = tk.StringVar()
        proveedor_combo = ttk.Combobox(edit_window, textvariable=proveedor_var)
        
        # Cargar proveedores
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM proveedores")
            proveedores = cursor.fetchall()
            proveedor_combo['values'] = [f"{p[0]} - {p[1]}" for p in proveedores]
            
            # Seleccionar el proveedor actual
            if values[5]:
                for p in proveedores:
                    if p[1] == values[5]:
                        proveedor_var.set(f"{p[0]} - {p[1]}")
                        break
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar proveedores: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        
        proveedor_combo.pack(pady=5)
        
        def save_changes():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Obtener ID del proveedor seleccionado
                proveedor_id = None
                if proveedor_var.get():
                    proveedor_id = int(proveedor_var.get().split(" - ")[0])
                
                cursor.execute(
                    "UPDATE productos SET nombre = %s, unidad = %s, stock = %s, stock_minimo = %s, id_proveedor = %s WHERE id = %s",
                    (nombre_entry.get(), unidad_entry.get(), stock_entry.get(), stock_minimo_entry.get(), proveedor_id, values[0])
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                edit_window.destroy()
                self.show_productos_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar producto: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(edit_window, text="Guardar Cambios", command=save_changes).pack(pady=20)

    def delete_producto(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?"):
            item = tree.item(selected[0])
            values = item['values']
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM productos WHERE id = %s", (values[0],))
                conn.commit()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                self.show_productos_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

    def show_proveedores_view(self):
        self.clear_main_frame()
        
        # Crear Treeview para mostrar proveedores
        columns = ("ID", "Nombre", "Contacto")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Obtener datos de proveedores
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, contacto FROM proveedores")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar proveedores: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        # Agregar botones de acción
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Editar", command=lambda: self.edit_proveedor(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=lambda: self.delete_proveedor(tree)).pack(side=tk.LEFT, padx=5)
        
        tree.pack(fill=tk.BOTH, expand=True)

    def show_add_proveedor(self):
        self.clear_main_frame()
        
        # Formulario para agregar proveedor
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = ttk.Entry(form_frame)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Contacto:").grid(row=1, column=0, padx=5, pady=5)
        contacto_entry = ttk.Entry(form_frame)
        contacto_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def save_proveedor():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO proveedores (nombre, contacto) VALUES (%s, %s)",
                    (nombre_entry.get(), contacto_entry.get())
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Proveedor agregado correctamente")
                self.show_proveedores_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar proveedor: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(form_frame, text="Guardar", command=save_proveedor).grid(row=2, column=0, columnspan=2, pady=20)

    def edit_proveedor(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un proveedor")
            return
        
        # Obtener datos del proveedor seleccionado
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana de edición
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Proveedor")
        edit_window.geometry("300x200")
        
        ttk.Label(edit_window, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(edit_window)
        nombre_entry.insert(0, values[1])
        nombre_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Contacto:").pack(pady=5)
        contacto_entry = ttk.Entry(edit_window)
        contacto_entry.insert(0, values[2])
        contacto_entry.pack(pady=5)
        
        def save_changes():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE proveedores SET nombre = %s, contacto = %s WHERE id = %s",
                    (nombre_entry.get(), contacto_entry.get(), values[0])
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Proveedor actualizado correctamente")
                edit_window.destroy()
                self.show_proveedores_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar proveedor: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(edit_window, text="Guardar Cambios", command=save_changes).pack(pady=20)

    def delete_proveedor(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione un proveedor")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este proveedor?"):
            item = tree.item(selected[0])
            values = item['values']
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM proveedores WHERE id = %s", (values[0],))
                conn.commit()
                messagebox.showinfo("Éxito", "Proveedor eliminado correctamente")
                self.show_proveedores_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar proveedor: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

    def show_add_empleado(self):
        self.clear_main_frame()
        
        # Formulario para agregar empleado
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = ttk.Entry(form_frame)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Usuario:").grid(row=1, column=0, padx=5, pady=5)
        usuario_entry = ttk.Entry(form_frame)
        usuario_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Contraseña:").grid(row=2, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(form_frame, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Rol:").grid(row=3, column=0, padx=5, pady=5)
        rol_var = tk.StringVar(value="mesero")
        roles = ["mesero", "cocinero", "aseo", "domiciliario"]
        rol_combo = ttk.Combobox(form_frame, textvariable=rol_var, values=roles, state="readonly")
        rol_combo.grid(row=3, column=1, padx=5, pady=5)
        
        def save_empleado():
            if register_user(
                usuario_entry.get(),
                password_entry.get(),
                nombre_entry.get(),
                rol_var.get()
            ):
                self.show_empleados_view()
        
        ttk.Button(form_frame, text="Guardar", command=save_empleado).grid(row=4, column=0, columnspan=2, pady=20)

    def show_recetas_view(self):
        self.clear_main_frame()
        
        # Crear Treeview para mostrar recetas
        columns = ("ID", "Plato", "Producto", "Cantidad", "Unidad")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Obtener datos de recetas
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

        # Agregar botones de acción
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Agregar Receta", command=self.show_add_receta).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Editar", command=lambda: self.edit_receta(tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=lambda: self.delete_receta(tree)).pack(side=tk.LEFT, padx=5)
        
        tree.pack(fill=tk.BOTH, expand=True)

    def show_add_receta(self):
        self.clear_main_frame()
        
        # Formulario para agregar receta
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        # Plato
        ttk.Label(form_frame, text="Plato:").grid(row=0, column=0, padx=5, pady=5)
        plato_var = tk.StringVar()
        plato_combo = ttk.Combobox(form_frame, textvariable=plato_var)
        
        # Producto
        ttk.Label(form_frame, text="Producto:").grid(row=1, column=0, padx=5, pady=5)
        producto_var = tk.StringVar()
        producto_combo = ttk.Combobox(form_frame, textvariable=producto_var)
        
        # Cantidad
        ttk.Label(form_frame, text="Cantidad:").grid(row=2, column=0, padx=5, pady=5)
        cantidad_entry = ttk.Entry(form_frame)
        cantidad_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Cargar platos y productos
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Cargar platos
            cursor.execute("SELECT id, nombre FROM platos")
            platos = cursor.fetchall()
            plato_combo['values'] = [f"{p[0]} - {p[1]}" for p in platos]
            
            # Cargar productos
            cursor.execute("SELECT id, nombre FROM productos")
            productos = cursor.fetchall()
            producto_combo['values'] = [f"{p[0]} - {p[1]}" for p in productos]
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            return
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        
        plato_combo.grid(row=0, column=1, padx=5, pady=5)
        producto_combo.grid(row=1, column=1, padx=5, pady=5)
        
        def save_receta():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Obtener IDs
                plato_id = int(plato_var.get().split(" - ")[0])
                producto_id = int(producto_var.get().split(" - ")[0])
                
                cursor.execute(
                    "INSERT INTO recetas (id_plato, id_producto, cantidad) VALUES (%s, %s, %s)",
                    (plato_id, producto_id, cantidad_entry.get())
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Receta agregada correctamente")
                self.show_recetas_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar receta: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(form_frame, text="Guardar", command=save_receta).grid(row=3, column=0, columnspan=2, pady=20)

    def edit_receta(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una receta")
            return
        
        # Obtener datos de la receta seleccionada
        item = tree.item(selected[0])
        values = item['values']
        
        # Crear ventana de edición
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Editar Receta")
        edit_window.geometry("300x200")
        
        # Plato
        ttk.Label(edit_window, text="Plato:").pack(pady=5)
        plato_var = tk.StringVar(value=values[1])
        plato_label = ttk.Label(edit_window, text=values[1])
        plato_label.pack(pady=5)
        
        # Producto
        ttk.Label(edit_window, text="Producto:").pack(pady=5)
        producto_var = tk.StringVar(value=values[2])
        producto_label = ttk.Label(edit_window, text=values[2])
        producto_label.pack(pady=5)
        
        # Cantidad
        ttk.Label(edit_window, text="Cantidad:").pack(pady=5)
        cantidad_entry = ttk.Entry(edit_window)
        cantidad_entry.insert(0, values[3])
        cantidad_entry.pack(pady=5)
        
        def save_changes():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE recetas SET cantidad = %s WHERE id = %s",
                    (cantidad_entry.get(), values[0])
                )
                conn.commit()
                messagebox.showinfo("Éxito", "Receta actualizada correctamente")
                edit_window.destroy()
                self.show_recetas_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar receta: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
        
        ttk.Button(edit_window, text="Guardar Cambios", command=save_changes).pack(pady=20)

    def delete_receta(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una receta")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta receta?"):
            item = tree.item(selected[0])
            values = item['values']
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM recetas WHERE id = %s", (values[0],))
                conn.commit()
                messagebox.showinfo("Éxito", "Receta eliminada correctamente")
                self.show_recetas_view()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar receta: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close() 