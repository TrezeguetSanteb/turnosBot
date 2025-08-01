"""
Módulo de notificaciones para el sistema de turnos.
Maneja el envío de mensajes automáticos a usuarios cuando sus turnos son afectados.
"""

import json
import os
from datetime import datetime

# Importar usando rutas relativas para compatibilidad
try:
    # Cuando se importa como módulo desde la aplicación principal
    from core.database import obtener_turnos_por_fecha, obtener_todos_los_turnos
except ImportError:
    # Cuando se ejecuta como script independiente
    import sys
    project_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, os.path.join(project_root, 'src'))
    from core.database import obtener_turnos_por_fecha, obtener_todos_los_turnos

# Obtener ruta raíz del proyecto
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
NOTIFICATIONS_LOG_PATH = os.path.join(
    PROJECT_ROOT, 'data', 'notifications_log.json')

# Asegurar que el directorio data existe
os.makedirs(os.path.join(PROJECT_ROOT, 'data'), exist_ok=True)


class NotificationManager:
    """Gestor de notificaciones del sistema"""

    def __init__(self):
        self.notifications_log = NOTIFICATIONS_LOG_PATH
        self.pending_notifications = []
        self._cargar_notificaciones_pendientes()

    def _cargar_notificaciones_pendientes(self):
        """Carga las notificaciones pendientes desde el archivo"""
        try:
            if os.path.exists(self.notifications_log):
                with open(self.notifications_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    # Cargar solo las notificaciones no enviadas
                    self.pending_notifications = [
                        n for n in log_data if not n.get('enviado', False)]
        except Exception as e:
            print(f"Error al cargar notificaciones pendientes: {e}")
            self.pending_notifications = []

    def formatear_fecha_legible(self, fecha_str, hora_str=None):
        """Convierte fecha YYYY-MM-DD a formato legible"""
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        dias = ['lunes', 'martes', 'miércoles',
                'jueves', 'viernes', 'sábado', 'domingo']

        try:
            dt = datetime.strptime(fecha_str, '%Y-%m-%d')
            dia_semana = dias[dt.weekday()]
            fecha_legible = f"{dia_semana} {dt.day} de {meses[dt.month-1]}"
            if hora_str:
                return f"{fecha_legible} a las {hora_str}"
            return fecha_legible
        except:
            return fecha_str

    def crear_mensaje_cancelacion_usuario(self, nombre, fecha, hora):
        """Crea mensaje de confirmación cuando el usuario cancela su propio turno"""
        fecha_legible = self.formatear_fecha_legible(fecha, hora)

        mensaje = f"""✅ *Confirmación de Cancelación* ✅

Hola {nombre},

Tu turno ha sido cancelado exitosamente:

📅 **Fecha y hora:** {fecha_legible}

¡Gracias por usar nuestro sistema! Si necesitas reservar un nuevo turno, escribe *hola*.

¡Que tengas un buen día! 😊"""

        return mensaje

    def crear_mensaje_cancelacion_admin(self, nombre, fecha, hora, motivo="administrativos"):
        """Crea mensaje de cancelación por motivos administrativos"""
        fecha_legible = self.formatear_fecha_legible(fecha, hora)

        mensaje = f"""🚫 *Turno Cancelado* 🚫

Hola {nombre},

Lamentamos informarte que tu turno ha sido cancelado por motivos {motivo}:

📅 **Fecha y hora:** {fecha_legible}

Te pedimos disculpas por las molestias ocasionadas. Puedes reservar un nuevo turno escribiendo *hola*.

¡Gracias por tu comprensión! 🙏"""

        return mensaje

    def crear_mensaje_dia_bloqueado(self, nombre, fecha, hora):
        """Crea mensaje cuando se bloquea un día completo"""
        fecha_legible = self.formatear_fecha_legible(fecha, hora)

        mensaje = f"""⚠️ *Día No Disponible* ⚠️

Hola {nombre},

Debido a circunstancias imprevistas, tu turno ha sido cancelado:

📅 **Fecha y hora:** {fecha_legible}

El día completo no estará disponible para atención. Te pedimos disculpas por las molestias.

Para reservar un nuevo turno, escribe *hola* cuando gustes.

¡Gracias por tu comprensión! 🙏"""

        return mensaje

    def registrar_notificacion(self, telefono, mensaje, tipo, turno_id=None):
        """Registra una notificación pendiente"""
        notificacion = {
            'timestamp': datetime.now().isoformat(),
            'telefono': telefono,
            'mensaje': mensaje,
            'tipo': tipo,
            'turno_id': turno_id,
            'enviado': False
        }

        self.pending_notifications.append(notificacion)
        self._guardar_log(notificacion)

        return notificacion

    def notificar_cancelacion_usuario(self, turno_id, nombre, fecha, hora, telefono):
        """Notifica la confirmación de cancelación de un turno por el usuario"""
        mensaje = self.crear_mensaje_cancelacion_usuario(nombre, fecha, hora)
        return self.registrar_notificacion(
            telefono=telefono,
            mensaje=mensaje,
            tipo='cancelacion_usuario',
            turno_id=turno_id
        )

    def notificar_cancelacion_turno(self, turno_id, nombre, fecha, hora, telefono):
        """Notifica la cancelación de un turno específico"""
        mensaje = self.crear_mensaje_cancelacion_admin(nombre, fecha, hora)
        return self.registrar_notificacion(
            telefono=telefono,
            mensaje=mensaje,
            tipo='cancelacion_turno',
            turno_id=turno_id
        )

    def notificar_dia_bloqueado(self, fecha):
        """Notifica a todos los usuarios con turnos en un día que fue bloqueado"""
        turnos_afectados = obtener_turnos_por_fecha(fecha)
        notificaciones = []

        for turno in turnos_afectados:
            turno_id, nombre, fecha_turno, hora, telefono = turno
            mensaje = self.crear_mensaje_dia_bloqueado(
                nombre, fecha_turno, hora)

            notificacion = self.registrar_notificacion(
                telefono=telefono,
                mensaje=mensaje,
                tipo='dia_bloqueado',
                turno_id=turno_id
            )
            notificaciones.append(notificacion)

        return notificaciones

    def obtener_notificaciones_pendientes(self):
        """Obtiene todas las notificaciones pendientes de envío"""
        return [n for n in self.pending_notifications if not n['enviado']]

    def marcar_como_enviada(self, notificacion):
        """Marca una notificación como enviada"""
        notificacion['enviado'] = True
        notificacion['fecha_envio'] = datetime.now().isoformat()

        # Actualizar en memoria
        for i, n in enumerate(self.pending_notifications):
            if (n.get('turno_id') == notificacion.get('turno_id') and
                n.get('telefono') == notificacion.get('telefono') and
                    n.get('timestamp') == notificacion.get('timestamp')):
                self.pending_notifications[i] = notificacion
                break

        # Actualizar en archivo
        self._actualizar_en_archivo(notificacion)

    def _actualizar_en_archivo(self, notificacion_actualizada):
        """Actualiza una notificación específica en el archivo"""
        try:
            if not os.path.exists(self.notifications_log):
                return

            with open(self.notifications_log, 'r', encoding='utf-8') as f:
                log_data = json.load(f)

            # Buscar y actualizar la notificación
            for i, notif in enumerate(log_data):
                if (notif.get('turno_id') == notificacion_actualizada.get('turno_id') and
                    notif.get('telefono') == notificacion_actualizada.get('telefono') and
                        notif.get('timestamp') == notificacion_actualizada.get('timestamp')):
                    log_data[i] = notificacion_actualizada
                    break

            # Guardar archivo actualizado
            with open(self.notifications_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error al actualizar notificación en archivo: {e}")

    def _guardar_log(self, notificacion):
        """Guarda el log de notificaciones"""
        try:
            # Leer log existente
            log_data = []
            if os.path.exists(self.notifications_log):
                with open(self.notifications_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)

            # Agregar nueva notificación
            log_data.append(notificacion)

            # Mantener solo los últimos 1000 registros
            if len(log_data) > 1000:
                log_data = log_data[-1000:]

            # Guardar
            with open(self.notifications_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error al guardar log de notificaciones: {e}")

    def limpiar_notificaciones_antiguas(self, dias=7):
        """Limpia notificaciones antigas del log"""
        try:
            if not os.path.exists(self.notifications_log):
                return

            with open(self.notifications_log, 'r', encoding='utf-8') as f:
                log_data = json.load(f)

            fecha_limite = datetime.now().timestamp() - (dias * 24 * 60 * 60)

            log_filtrado = []
            for notif in log_data:
                try:
                    timestamp = datetime.fromisoformat(
                        notif['timestamp']).timestamp()
                    if timestamp > fecha_limite:
                        log_filtrado.append(notif)
                except:
                    # Mantener notificaciones con formato de fecha inválido
                    log_filtrado.append(notif)

            with open(self.notifications_log, 'w', encoding='utf-8') as f:
                json.dump(log_filtrado, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error al limpiar notificaciones antigas: {e}")

    def limpiar_notificaciones_enviadas(self):
        """Elimina las notificaciones que ya fueron enviadas del log y memoria"""
        try:
            if not os.path.exists(self.notifications_log):
                return 0

            with open(self.notifications_log, 'r', encoding='utf-8') as f:
                log_data = json.load(f)

            # Contar notificaciones enviadas antes de limpiar
            enviadas_count = len(
                [n for n in log_data if n.get('enviado', False)])

            # Filtrar solo las no enviadas
            log_filtrado = [n for n in log_data if not n.get('enviado', False)]

            # Actualizar memoria
            self.pending_notifications = log_filtrado.copy()

            # Guardar archivo filtrado
            with open(self.notifications_log, 'w', encoding='utf-8') as f:
                json.dump(log_filtrado, f, indent=2, ensure_ascii=False)

            print(
                f"🧹 Limpieza completada: {enviadas_count} notificaciones enviadas eliminadas")
            return enviadas_count

        except Exception as e:
            print(f"Error al limpiar notificaciones enviadas: {e}")
            return 0


# Instancia global del gestor de notificaciones
notification_manager = NotificationManager()


# Funciones de conveniencia
def notificar_cancelacion_usuario(turno_id, nombre, fecha, hora, telefono):
    """Función de conveniencia para notificar cancelación por usuario"""
    return notification_manager.notificar_cancelacion_usuario(turno_id, nombre, fecha, hora, telefono)


def notificar_cancelacion_turno(turno_id, nombre, fecha, hora, telefono):
    """Función de conveniencia para notificar cancelación de turno"""
    return notification_manager.notificar_cancelacion_turno(turno_id, nombre, fecha, hora, telefono)


def notificar_dia_bloqueado(fecha):
    """Función de conveniencia para notificar día bloqueado"""
    return notification_manager.notificar_dia_bloqueado(fecha)


def obtener_notificaciones_pendientes():
    """Función de conveniencia para obtener notificaciones pendientes"""
    return notification_manager.obtener_notificaciones_pendientes()


def marcar_notificacion_enviada(notificacion):
    """Función de conveniencia para marcar notificación como enviada"""
    return notification_manager.marcar_como_enviada(notificacion)


def limpiar_notificaciones_enviadas():
    """Función de conveniencia para limpiar notificaciones enviadas"""
    return notification_manager.limpiar_notificaciones_enviadas()
