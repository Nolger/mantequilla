-- Crear base de datos (por si no existe)
CREATE DATABASE IF NOT EXISTS mantequilla;
USE mantequilla;

-- Tabla de empleados
CREATE TABLE empleados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    rol ENUM('administrador', 'mesero', 'cocinero', 'aseo', 'domiciliario') NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(128) NOT NULL,
    salt VARCHAR(32) NOT NULL
);

-- Tabla de clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20)
);

-- Tabla de mesas
CREATE TABLE mesas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero INT UNIQUE NOT NULL,
    capacidad INT NOT NULL
);

-- Tabla de proveedores
CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100)
);

-- Tabla de productos (ingredientes)
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    unidad VARCHAR(20) NOT NULL,
    stock DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock_minimo DECIMAL(10,2) NOT NULL DEFAULT 0,
    id_proveedor INT,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id)
);

-- Tabla de platos
CREATE TABLE platos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL
);

-- Tabla de recetas (ingredientes por plato)
CREATE TABLE recetas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_plato INT,
    id_producto INT,
    cantidad DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_plato) REFERENCES platos(id),
    FOREIGN KEY (id_producto) REFERENCES productos(id)
);

-- Tabla de ordenes de compra (para productos)
CREATE TABLE ordenes_compra (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_proveedor INT,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id)
);

-- Detalle de productos por orden de compra
CREATE TABLE detalle_orden (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT,
    id_producto INT,
    cantidad DECIMAL(10,2),
    FOREIGN KEY (id_orden) REFERENCES ordenes_compra(id),
    FOREIGN KEY (id_producto) REFERENCES productos(id)
);

-- Tabla de comandas (orden que va a cocina)
CREATE TABLE comandas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_empleado INT,
    id_mesa INT,
    estado ENUM('pendiente', 'en preparación', 'servido') DEFAULT 'pendiente',
    FOREIGN KEY (id_empleado) REFERENCES empleados(id),
    FOREIGN KEY (id_mesa) REFERENCES mesas(id)
);

-- Detalle de platos por comanda
CREATE TABLE detalle_comanda (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_comanda INT,
    id_plato INT,
    cantidad INT NOT NULL,
    FOREIGN KEY (id_comanda) REFERENCES comandas(id),
    FOREIGN KEY (id_plato) REFERENCES platos(id)
);

-- Tabla de facturas
CREATE TABLE facturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_cliente INT,
    id_comanda INT,
    total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    FOREIGN KEY (id_comanda) REFERENCES comandas(id)
);

-- Tabla de mermas (pérdidas de producto)
CREATE TABLE mermas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT,
    cantidad DECIMAL(10,2),
    motivo TEXT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id)
);
