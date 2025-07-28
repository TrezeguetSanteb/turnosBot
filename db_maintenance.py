#!/usr/bin/env python3
"""
Utilidades de mantenimiento de la base de datos
"""
import sqlite3
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def limpiar_turnos_antiguos(dias_conservar=30):
    """
    Elimina turnos anteriores a X días para mantener la performance

    Args:
        dias_conservar (int): Días hacia atrás que conservar (default: 30)
    """
    try:
        # Calcular fecha límite
        fecha_limite = (datetime.now() - timedelta(days=dias_conservar)).date()
        fecha_limite_str = fecha_limite.strftime('%Y-%m-%d')

        logger.info(
            f"Iniciando limpieza de turnos anteriores a {fecha_limite_str}")

        # Conectar a la base de datos
        conn = sqlite3.connect('turnos.db')
        cursor = conn.cursor()

        # Contar turnos que se van a eliminar
        cursor.execute("""
            SELECT COUNT(*) FROM turnos 
            WHERE fecha < ?
        """, (fecha_limite_str,))

        count_antes = cursor.fetchone()[0]

        if count_antes == 0:
            logger.info("No hay turnos antiguos para eliminar")
            conn.close()
            return 0

        # Eliminar turnos antiguos
        cursor.execute("""
            DELETE FROM turnos 
            WHERE fecha < ?
        """, (fecha_limite_str,))

        turnos_eliminados = cursor.rowcount

        # Limpiar configuraciones de días bloqueados antiguos también
        cursor.execute("""
            DELETE FROM dias_bloqueados 
            WHERE fecha < ?
        """, (fecha_limite_str,))

        dias_bloqueados_limpiados = cursor.rowcount

        # Optimizar la base de datos después de la limpieza
        cursor.execute("VACUUM")

        conn.commit()
        conn.close()

        logger.info(f"✅ Limpieza completada:")
        logger.info(f"   - {turnos_eliminados} turnos eliminados")
        logger.info(
            f"   - {dias_bloqueados_limpiados} días bloqueados limpiados")
        logger.info(f"   - Base de datos optimizada con VACUUM")

        return turnos_eliminados

    except Exception as e:
        logger.error(f"Error en limpieza de turnos: {e}")
        return -1


def obtener_estadisticas_db():
    """
    Obtiene estadísticas de la base de datos
    """
    try:
        conn = sqlite3.connect('turnos.db')
        cursor = conn.cursor()

        # Contar turnos totales
        cursor.execute("SELECT COUNT(*) FROM turnos")
        total_turnos = cursor.fetchone()[0]

        # Contar turnos por mes
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', fecha) as mes,
                COUNT(*) as cantidad
            FROM turnos 
            GROUP BY strftime('%Y-%m', fecha)
            ORDER BY mes DESC
            LIMIT 6
        """)

        turnos_por_mes = cursor.fetchall()

        # Obtener tamaño de la base de datos
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]

        db_size_bytes = page_count * page_size
        db_size_mb = db_size_bytes / 1024 / 1024

        conn.close()

        stats = {
            'total_turnos': total_turnos,
            'turnos_por_mes': turnos_por_mes,
            'tamaño_db_mb': round(db_size_mb, 2)
        }

        logger.info(
            f"📊 Estadísticas de BD: {total_turnos} turnos, {db_size_mb:.2f} MB")

        return stats

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return None


def crear_tabla_dias_bloqueados_si_no_existe():
    """
    Crea la tabla de días bloqueados si no existe
    (Para compatibilidad con versiones anteriores)
    """
    try:
        conn = sqlite3.connect('turnos.db')
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dias_bloqueados (
                fecha TEXT PRIMARY KEY,
                motivo TEXT,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

        logger.info("✅ Tabla dias_bloqueados verificada/creada")

    except Exception as e:
        logger.error(f"Error creando tabla dias_bloqueados: {e}")


def mantenimiento_completo():
    """
    Ejecuta todas las tareas de mantenimiento
    """
    logger.info("🔧 Iniciando mantenimiento de base de datos...")

    # Crear tablas faltantes si es necesario
    crear_tabla_dias_bloqueados_si_no_existe()

    # Obtener estadísticas antes
    stats_antes = obtener_estadisticas_db()
    if stats_antes:
        logger.info(
            f"📊 Antes: {stats_antes['total_turnos']} turnos, {stats_antes['tamaño_db_mb']} MB")

    # Limpiar turnos antiguos (conservar últimos 30 días)
    turnos_eliminados = limpiar_turnos_antiguos(dias_conservar=30)

    # Obtener estadísticas después
    if turnos_eliminados > 0:
        stats_despues = obtener_estadisticas_db()
        if stats_despues:
            logger.info(
                f"📊 Después: {stats_despues['total_turnos']} turnos, {stats_despues['tamaño_db_mb']} MB")

    logger.info("✅ Mantenimiento completado")


if __name__ == '__main__':
    # Configurar logging para pruebas
    logging.basicConfig(level=logging.INFO)

    # Ejecutar mantenimiento
    mantenimiento_completo()
