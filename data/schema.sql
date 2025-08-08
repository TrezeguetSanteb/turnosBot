-- Tabla de turnos (actualizada con profesional)
CREATE TABLE IF NOT EXISTS turnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL, 
    fecha TEXT NOT NULL, 
    hora TEXT NOT NULL, 
    telefono TEXT NOT NULL,
    profesional_id INTEGER DEFAULT 1,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profesional_id) REFERENCES profesionales(id)
);

-- Tabla de profesionales
CREATE TABLE IF NOT EXISTS profesionales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    color TEXT NOT NULL DEFAULT '#3498db',
    activo INTEGER DEFAULT 1,
    orden INTEGER DEFAULT 0
);

-- Tabla de configuración de capacidad por horario
CREATE TABLE IF NOT EXISTS capacidad_horarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dia_semana TEXT NOT NULL, -- Lunes, Martes, etc.
    periodo TEXT NOT NULL, -- 'manana' o 'tarde' 
    capacidad_total INTEGER DEFAULT 1,
    UNIQUE(dia_semana, periodo)
);

-- Datos iniciales de profesionales
INSERT OR IGNORE INTO profesionales (id, nombre, color, activo, orden) VALUES 
    (1, 'Martín', '#e74c3c', 1, 1),
    (2, 'Joaquín', '#2ecc71', 1, 2),
    (3, 'Felipe', '#9b59b6', 1, 3);

-- Configuración inicial de capacidad (3 profesionales por defecto)
INSERT OR IGNORE INTO capacidad_horarios (dia_semana, periodo, capacidad_total) VALUES
    ('Lunes', 'manana', 3), ('Lunes', 'tarde', 3),
    ('Martes', 'manana', 3), ('Martes', 'tarde', 3),
    ('Miércoles', 'manana', 3), ('Miércoles', 'tarde', 3),
    ('Jueves', 'manana', 3), ('Jueves', 'tarde', 3),
    ('Viernes', 'manana', 3), ('Viernes', 'tarde', 3),
    ('Sábado', 'manana', 3), ('Sábado', 'tarde', 3),
    ('Domingo', 'manana', 0), ('Domingo', 'tarde', 0);

-- Migración: tabla antigua 'turno' si existe
INSERT OR IGNORE INTO turnos (nombre, fecha, hora, telefono, profesional_id)
SELECT nombre, fecha, hora, telefono, 1 FROM turno WHERE EXISTS (SELECT name FROM sqlite_master WHERE type='table' AND name='turno');

