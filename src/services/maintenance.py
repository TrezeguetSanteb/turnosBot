"""
Módulo de mantenimiento y estadísticas de la base de datos
"""
import sqlite3
import os
from datetime import datetime, timedelta


def obtener_estadisticas_db():
    """
    Obtener estadísticas de la base de datos
    """
    try:
        # Buscar la base de datos
        db_path = 'data/turnos.db'
        if not os.path.exists(db_path):
            db_path = 'turnos.db'
        if not os.path.exists(db_path):
            return {'error': 'Base de datos no encontrada'}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        stats = {}

        # Contar turnos totales
        cursor.execute("SELECT COUNT(*) FROM turnos")
        stats['total_turnos'] = cursor.fetchone()[0]

        # Contar turnos por fecha (últimos 30 días)
        fecha_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM turnos WHERE fecha >= ?", (fecha_limite,))
        stats['turnos_ultimo_mes'] = cursor.fetchone()[0]

        # Contar días bloqueados
        cursor.execute("SELECT COUNT(*) FROM dias_bloqueados")
        stats['dias_bloqueados'] = cursor.fetchone()[0]

        # Contar profesionales (si la tabla existe)
        try:
            cursor.execute("SELECT COUNT(*) FROM profesionales")
            stats['total_profesionales'] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            stats['total_profesionales'] = 0

        # Tamaño de la BD en KB
        file_size = os.path.getsize(db_path) / 1024
        stats['db_size_kb'] = round(file_size, 2)

        conn.close()

        # Agregar timestamp
        stats['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return stats

    except Exception as e:
        return {'error': f'Error obteniendo estadísticas: {str(e)}'}


def mantenimiento_completo():
    """
    Realizar mantenimiento completo de la base de datos
    """
    try:
        # Buscar la base de datos
        db_path = 'data/turnos.db'
        if not os.path.exists(db_path):
            db_path = 'turnos.db'
        if not os.path.exists(db_path):
            return {'success': False, 'message': 'Base de datos no encontrada'}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        acciones = []

        # Limpiar turnos muy antiguos (más de 6 meses)
        fecha_limite = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        cursor.execute("DELETE FROM turnos WHERE fecha < ?", (fecha_limite,))
        turnos_eliminados = cursor.rowcount
        if turnos_eliminados > 0:
            acciones.append(f"Eliminados {turnos_eliminados} turnos antiguos")

        # Limpiar días bloqueados pasados
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("DELETE FROM dias_bloqueados WHERE fecha < ?", (fecha_hoy,))
        dias_eliminados = cursor.rowcount
        if dias_eliminados > 0:
            acciones.append(f"Eliminados {dias_eliminados} días bloqueados pasados")

        # Ejecutar VACUUM para optimizar la BD
        cursor.execute("VACUUM")
        acciones.append("Base de datos optimizada (VACUUM)")

        conn.commit()
        conn.close()

        return {
            'success': True,
            'message': 'Mantenimiento completado',
            'acciones': acciones,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Error en mantenimiento: {str(e)}'
        }


def limpiar_turnos_antiguos(dias=180):
    """
    Limpiar solo turnos antiguos
    """
    try:
        db_path = 'data/turnos.db'
        if not os.path.exists(db_path):
            db_path = 'turnos.db'
        if not os.path.exists(db_path):
            return {'success': False, 'message': 'Base de datos no encontrada'}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
        cursor.execute("DELETE FROM turnos WHERE fecha < ?", (fecha_limite,))
        turnos_eliminados = cursor.rowcount

        conn.commit()
        conn.close()

        return {
            'success': True,
            'turnos_eliminados': turnos_eliminados,
            'fecha_limite': fecha_limite
        }

    except Exception as e:
        return {'success': False, 'message': f'Error: {str(e)}'}


def optimizar_base_datos():
    """
    Solo optimizar la base de datos con VACUUM
    """
    try:
        db_path = 'data/turnos.db'
        if not os.path.exists(db_path):
            db_path = 'turnos.db'
        if not os.path.exists(db_path):
            return {'success': False, 'message': 'Base de datos no encontrada'}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("VACUUM")
        conn.close()

        return {'success': True, 'message': 'Base de datos optimizada'}

    except Exception as e:
        return {'success': False, 'message': f'Error: {str(e)}'}
