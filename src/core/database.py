"""
Módulo de base de datos - Funciones principales para manejo de turnos
"""
import sqlite3
import os
from datetime import datetime, timedelta


def obtener_conexion_bd():
    """
    Obtener conexión a la base de datos
    """
    # Buscar la base de datos
    db_path = 'data/turnos.db'
    if not os.path.exists(db_path):
        db_path = 'turnos.db'
    
    conn = sqlite3.connect(db_path)
    return conn


def obtener_turnos_por_fecha(fecha_str):
    """
    Obtener todos los turnos para una fecha específica
    """
    try:
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        
        # Query que incluye información del profesional
        cursor.execute("""
            SELECT t.id, t.nombre, t.telefono, t.hora, t.telefono, t.es_nuevo,
                   p.nombre as profesional_nombre, p.color as profesional_color
            FROM turnos t
            LEFT JOIN profesionales p ON t.profesional_id = p.id
            WHERE t.fecha = ?
            ORDER BY t.hora
        """, (fecha_str,))
        
        turnos = cursor.fetchall()
        conn.close()
        
        return turnos
        
    except Exception as e:
        print(f"❌ Error obteniendo turnos por fecha: {e}")
        return []


def eliminar_turno_admin(turno_id):
    """
    Eliminar un turno por ID (desde admin)
    """
    try:
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        
        # Primero obtener datos del turno para notificación
        cursor.execute("""
            SELECT t.nombre, t.telefono, t.fecha, t.hora,
                   p.nombre as profesional_nombre
            FROM turnos t
            LEFT JOIN profesionales p ON t.profesional_id = p.id
            WHERE t.id = ?
        """, (turno_id,))
        
        turno_info = cursor.fetchone()
        
        if not turno_info:
            conn.close()
            return False, "Turno no encontrado"
            
        # Eliminar turno
        cursor.execute("DELETE FROM turnos WHERE id = ?", (turno_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return True, turno_info
        else:
            conn.close()
            return False, "No se pudo eliminar el turno"
            
    except Exception as e:
        print(f"❌ Error eliminando turno: {e}")
        return False, str(e)


def obtener_todos_los_turnos():
    """
    Obtener todos los turnos (para estadísticas o admin)
    """
    try:
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.nombre, t.telefono, t.fecha, t.hora, t.es_nuevo,
                   p.nombre as profesional_nombre, p.color as profesional_color
            FROM turnos t
            LEFT JOIN profesionales p ON t.profesional_id = p.id
            ORDER BY t.fecha DESC, t.hora
        """)
        
        turnos = cursor.fetchall()
        conn.close()
        
        return turnos
        
    except Exception as e:
        print(f"❌ Error obteniendo todos los turnos: {e}")
        return []


def crear_turno(nombre, telefono, fecha, hora, profesional_id=None):
    """
    Crear un nuevo turno
    """
    try:
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO turnos (nombre, telefono, fecha, hora, profesional_id, es_nuevo)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (nombre, telefono, fecha, hora, profesional_id))
        
        turno_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return turno_id
        
    except Exception as e:
        print(f"❌ Error creando turno: {e}")
        return None


def obtener_turnos_disponibles(fecha_str):
    """
    Obtener horarios disponibles para una fecha
    """
    try:
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        
        # Obtener turnos ocupados
        cursor.execute("SELECT hora FROM turnos WHERE fecha = ?", (fecha_str,))
        ocupados = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return ocupados
        
    except Exception as e:
        print(f"❌ Error obteniendo turnos disponibles: {e}")
        return []


def verificar_turno_disponible(fecha_str, hora_str, profesional_id=None):
    """
    Verificar si un turno específico está disponible
    """
    try:
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        
        if profesional_id:
            cursor.execute("""
                SELECT COUNT(*) FROM turnos 
                WHERE fecha = ? AND hora = ? AND profesional_id = ?
            """, (fecha_str, hora_str, profesional_id))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM turnos 
                WHERE fecha = ? AND hora = ?
            """, (fecha_str, hora_str))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count == 0
        
    except Exception as e:
        print(f"❌ Error verificando disponibilidad: {e}")
        return False


def marcar_turnos_como_vistos():
    """
    Marcar todos los turnos como vistos (es_nuevo = 0)
    """
    try:
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE turnos SET es_nuevo = 0 WHERE es_nuevo = 1")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error marcando turnos como vistos: {e}")
        return False
