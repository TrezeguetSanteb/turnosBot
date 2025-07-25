"""
Módulo de gestión de base de datos para el sistema de turnos.
"""

import sqlite3
from typing import List, Tuple, Optional
import os

DB_PATH = 'turnos.db'


class DatabaseManager:
    """Gestor centralizado de operaciones de base de datos"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Inicializa la base de datos si no existe"""
        if not os.path.exists(self.db_path):
            self._create_tables()

    def _create_tables(self):
        """Crea las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS turno (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL, 
                fecha TEXT NOT NULL, 
                hora TEXT NOT NULL, 
                telefono TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_path)

    # ==================== OPERACIONES DE LECTURA ====================

    def obtener_turnos_por_telefono(self, telefono: str) -> List[Tuple]:
        """
        Obtiene todos los turnos de un número de teléfono específico
        Returns: Lista de tuplas (nombre, fecha, hora)
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                'SELECT nombre, fecha, hora FROM turno WHERE telefono = ? ORDER BY fecha, hora',
                (telefono,)
            )
            turnos = c.fetchall()
            conn.close()
            return turnos
        except Exception as e:
            print(f"Error al obtener turnos por teléfono: {e}")
            return []

    def obtener_turnos_con_id_por_telefono(self, telefono: str) -> List[Tuple]:
        """
        Obtiene todos los turnos con ID de un número de teléfono específico
        Returns: Lista de tuplas (id, nombre, fecha, hora)
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                'SELECT id, nombre, fecha, hora FROM turno WHERE telefono = ? ORDER BY fecha, hora',
                (telefono,)
            )
            turnos = c.fetchall()
            conn.close()
            return turnos
        except Exception as e:
            print(f"Error al obtener turnos con ID por teléfono: {e}")
            return []

    def obtener_horarios_ocupados(self, fecha: str) -> set:
        """
        Obtiene los horarios ocupados para una fecha específica
        Returns: Set de horarios ocupados
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('SELECT hora FROM turno WHERE fecha = ?', (fecha,))
            ocupados = set([h[0] for h in c.fetchall()])
            conn.close()
            return ocupados
        except Exception as e:
            print(f"Error al obtener horarios ocupados: {e}")
            return set()

    def verificar_horario_disponible(self, fecha: str, hora: str) -> bool:
        """
        Verifica si un horario específico está disponible
        Returns: True si está disponible, False si está ocupado
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                'SELECT COUNT(*) FROM turno WHERE fecha = ? AND hora = ?', (fecha, hora))
            existe = c.fetchone()[0]
            conn.close()
            return existe == 0
        except Exception as e:
            print(f"Error al verificar horario disponible: {e}")
            return False

    def obtener_todos_los_turnos(self) -> List[Tuple]:
        """
        Obtiene todos los turnos de la base de datos
        Returns: Lista de tuplas (id, nombre, fecha, hora, telefono)
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                'SELECT id, nombre, fecha, hora, telefono FROM turno ORDER BY fecha, hora')
            turnos = c.fetchall()
            conn.close()
            return turnos
        except Exception as e:
            print(f"Error al obtener todos los turnos: {e}")
            return []

    def obtener_turnos_por_fecha(self, fecha: str) -> List[Tuple]:
        """
        Obtiene todos los turnos para una fecha específica
        Returns: Lista de tuplas (id, nombre, fecha, hora, telefono)
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                'SELECT id, nombre, fecha, hora, telefono FROM turno WHERE fecha = ? ORDER BY hora',
                (fecha,)
            )
            turnos = c.fetchall()
            conn.close()
            return turnos
        except Exception as e:
            print(f"Error al obtener turnos por fecha: {e}")
            return []

    # ==================== OPERACIONES DE ESCRITURA ====================

    def crear_turno(self, nombre: str, fecha: str, hora: str, telefono: str) -> bool:
        """
        Crea un nuevo turno en la base de datos
        Returns: True si se creó exitosamente, False si hubo error
        """
        try:
            # Verificar que el horario esté disponible antes de insertar
            if not self.verificar_horario_disponible(fecha, hora):
                print(f"Horario {hora} en fecha {fecha} ya está ocupado")
                return False

            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                'INSERT INTO turno (nombre, fecha, hora, telefono) VALUES (?, ?, ?, ?)',
                (nombre, fecha, hora, telefono)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al crear turno: {e}")
            return False

    def cancelar_turno_por_usuario(self, turno_id: int, telefono: str) -> bool:
        """
        Cancela un turno específico (solo si pertenece al usuario)
        Returns: True si se canceló exitosamente, False si hubo error
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute(
                'DELETE FROM turno WHERE id = ? AND telefono = ?',
                (turno_id, telefono)
            )
            filas_afectadas = c.rowcount
            conn.commit()
            conn.close()
            return filas_afectadas > 0
        except Exception as e:
            print(f"Error al cancelar turno por usuario: {e}")
            return False

    def eliminar_turno_admin(self, turno_id: int) -> bool:
        """
        Elimina un turno (función administrativa)
        Returns: True si se eliminó exitosamente, False si hubo error
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('DELETE FROM turno WHERE id = ?', (turno_id,))
            filas_afectadas = c.rowcount
            conn.commit()
            conn.close()
            return filas_afectadas > 0
        except Exception as e:
            print(f"Error al eliminar turno (admin): {e}")
            return False

    # ==================== OPERACIONES DE MANTENIMIENTO ====================

    def limpiar_turnos_pasados(self, fecha_limite: str) -> int:
        """
        Elimina turnos anteriores a una fecha específica
        Returns: Número de turnos eliminados
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('DELETE FROM turno WHERE fecha < ?', (fecha_limite,))
            eliminados = c.rowcount
            conn.commit()
            conn.close()
            return eliminados
        except Exception as e:
            print(f"Error al limpiar turnos pasados: {e}")
            return 0

    def obtener_estadisticas(self) -> dict:
        """
        Obtiene estadísticas básicas de la base de datos
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()

            # Total de turnos
            c.execute('SELECT COUNT(*) FROM turno')
            total_turnos = c.fetchone()[0]

            # Turnos por fecha (próximos 7 días)
            c.execute('''
                SELECT fecha, COUNT(*) 
                FROM turno 
                WHERE fecha >= date('now') 
                GROUP BY fecha 
                ORDER BY fecha 
                LIMIT 7
            ''')
            turnos_por_fecha = c.fetchall()

            conn.close()

            return {
                'total_turnos': total_turnos,
                'turnos_por_fecha': turnos_por_fecha
            }
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {'total_turnos': 0, 'turnos_por_fecha': []}


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

# Funciones de conveniencia para mantener compatibilidad con el código existente


def obtener_turnos_por_telefono(telefono: str) -> List[Tuple]:
    return db_manager.obtener_turnos_por_telefono(telefono)


def obtener_turnos_con_id_por_telefono(telefono: str) -> List[Tuple]:
    return db_manager.obtener_turnos_con_id_por_telefono(telefono)


def obtener_horarios_ocupados(fecha: str) -> set:
    return db_manager.obtener_horarios_ocupados(fecha)


def verificar_horario_disponible(fecha: str, hora: str) -> bool:
    return db_manager.verificar_horario_disponible(fecha, hora)


def crear_turno(nombre: str, fecha: str, hora: str, telefono: str) -> bool:
    return db_manager.crear_turno(nombre, fecha, hora, telefono)


def cancelar_turno_por_usuario(turno_id: int, telefono: str) -> bool:
    return db_manager.cancelar_turno_por_usuario(turno_id, telefono)


def eliminar_turno_admin(turno_id: int) -> bool:
    return db_manager.eliminar_turno_admin(turno_id)


def obtener_turnos_por_fecha(fecha: str) -> List[Tuple]:
    return db_manager.obtener_turnos_por_fecha(fecha)


def obtener_todos_los_turnos() -> List[Tuple]:
    return db_manager.obtener_todos_los_turnos()
