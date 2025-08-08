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
    (1, 'profesional1', '#3498db', 1, 1);

-- Configuración inicial de capacidad (1 profesional por defecto)
INSERT OR IGNORE INTO capacidad_horarios (dia_semana, periodo, capacidad_total) VALUES
    ('Lunes', 'manana', 1), ('Lunes', 'tarde', 1),
    ('Martes', 'manana', 1), ('Martes', 'tarde', 1),
    ('Miércoles', 'manana', 1), ('Miércoles', 'tarde', 1),
    ('Jueves', 'manana', 1), ('Jueves', 'tarde', 1),
    ('Viernes', 'manana', 1), ('Viernes', 'tarde', 1),
    ('Sábado', 'manana', 1), ('Sábado', 'tarde', 1),
    ('Domingo', 'manana', 0), ('Domingo', 'tarde', 0);

-- Migración: tabla antigua 'turno' si existe (comentada para evitar errores)
-- INSERT OR IGNORE INTO turnos (nombre, fecha, hora, telefono, profesional_id)
-- SELECT nombre, fecha, hora, telefono, 1 FROM turno WHERE EXISTS (SELECT name FROM sqlite_master WHERE type='table' AND name='turno');

