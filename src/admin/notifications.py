#!/usr/bin/env python3
"""
Sistema de notificaciones para el administrador
Envía notificaciones por WhatsApp cuando ocurren eventos importantes
"""

import json
import os
from datetime import datetime
from src.core.config import config

# Obtener ruta raíz del proyecto
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
ADMIN_NOTIFICATIONS_PATH = os.path.join(
    PROJECT_ROOT, 'data', 'admin_notifications.json')

# Asegurar que el directorio data existe
os.makedirs(os.path.join(PROJECT_ROOT, 'data'), exist_ok=True)


def log_notification(tipo, datos):
    """Guarda la notificación en el log para envío posterior"""
    try:
        notification = {
            'timestamp': datetime.now().isoformat(),
            'tipo': tipo,
            'datos': datos,
            'enviada': False
        }

        # Leer notificaciones existentes
        log_file = ADMIN_NOTIFICATIONS_PATH
        notifications = []

        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    notifications = json.load(f)
                except json.JSONDecodeError:
                    notifications = []

        # Agregar nueva notificación
        notifications.append(notification)

        # Guardar todas las notificaciones
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)

        print(f"📝 Notificación guardada: {tipo}")

    except Exception as e:
        print(f"❌ Error guardando notificación: {e}")


def notificar_nuevo_turno(nombre, telefono, fecha, hora, canal="WhatsApp"):
    """Notifica cuando se agenda un nuevo turno"""
    datos = {
        'nombre': nombre,
        'telefono': telefono,
        'fecha': fecha,
        'hora': hora,
        'canal': canal
    }
    log_notification('nuevo_turno', datos)


def notificar_cancelacion_turno(nombre, fecha, hora, canal="WhatsApp"):
    """Notifica cuando se cancela un turno"""
    datos = {
        'nombre': nombre,
        'fecha': fecha,
        'hora': hora,
        'canal': canal
    }
    log_notification('cancelacion_turno', datos)


def notificar_dia_bloqueado(fecha, motivo="Admin Panel"):
    """Notifica cuando se bloquea un día"""
    datos = {
        'fecha': fecha,
        'motivo': motivo,
        'accion': 'bloquear'
    }
    log_notification('dia_bloqueado', datos)


def notificar_dia_desbloqueado(fecha, motivo="Admin Panel"):
    """Notifica cuando se desbloquea un día"""
    datos = {
        'fecha': fecha,
        'motivo': motivo,
        'accion': 'desbloquear'
    }
    log_notification('dia_desbloqueado', datos)


def notificar_bloqueo_dia(fecha):
    """Notifica cuando se bloquea un día"""
    datos = {
        'fecha': fecha,
        'accion': 'bloqueado'
    }
    log_notification('bloqueo_dia', datos)


def notificar_desbloqueo_dia(fecha):
    """Notifica cuando se desbloquea un día"""
    datos = {
        'fecha': fecha,
        'accion': 'desbloqueado'
    }
    log_notification('desbloqueo_dia', datos)


def obtener_notificaciones_pendientes():
    """Obtiene todas las notificaciones pendientes de envío"""
    try:
        log_file = ADMIN_NOTIFICATIONS_PATH

        if not os.path.exists(log_file):
            return []

        with open(log_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)

        # Filtrar solo las no enviadas y recientes (últimas 24 horas)
        from datetime import datetime, timedelta
        ahora = datetime.now()
        limite_tiempo = ahora - timedelta(hours=24)

        pendientes = []
        for n in notifications:
            if not n.get('enviada', False):
                # Verificar si la notificación es reciente
                try:
                    timestamp_notif = datetime.fromisoformat(
                        n['timestamp'].replace('Z', '+00:00'))
                    if timestamp_notif >= limite_tiempo:
                        pendientes.append(n)
                    else:
                        # Marcar automáticamente como enviada si es muy vieja
                        n['enviada'] = True
                        n['enviada_timestamp'] = ahora.isoformat()
                        n['motivo_marcado'] = 'Notificación expirada (>24h)'
                except:
                    # Si hay error parseando fecha, incluir la notificación
                    pendientes.append(n)

        # Guardar cambios si se marcaron notificaciones como expiradas
        if any(n.get('motivo_marcado') for n in notifications):
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(notifications, f, ensure_ascii=False, indent=2)

        return pendientes

    except Exception as e:
        print(f"❌ Error obteniendo notificaciones: {e}")
        return []


def marcar_notificacion_enviada(index):
    """Marca una notificación como enviada"""
    try:
        log_file = ADMIN_NOTIFICATIONS_PATH

        if not os.path.exists(log_file):
            return False

        with open(log_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)

        if 0 <= index < len(notifications):
            notifications[index]['enviada'] = True
            notifications[index]['enviada_timestamp'] = datetime.now(
            ).isoformat()

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(notifications, f, ensure_ascii=False, indent=2)

            return True

        return False

    except Exception as e:
        print(f"❌ Error marcando notificación: {e}")
        return False


def formatear_mensaje_turno(datos):
    """Formatea el mensaje para un nuevo turno"""
    return f"""🆕 *Nuevo turno agendado*

👤 Cliente: {datos['nombre']}
📅 Fecha: {datos['fecha']}
⏰ Hora: {datos['hora']}
📞 Teléfono: {datos['telefono']}
💬 Canal: {datos['canal']}

Panel: {obtener_url_panel()}"""


def formatear_mensaje_cancelacion(datos):
    """Formatea el mensaje para una cancelación"""
    return f"""🗑️ *Turno cancelado*

👤 Cliente: {datos['nombre']}
📅 Fecha: {datos['fecha']}
⏰ Hora: {datos['hora']}
💬 Cancelado desde: {datos['canal']}

Panel: {obtener_url_panel()}"""


def formatear_mensaje_dia_bloqueado(datos):
    """Formatea el mensaje para bloqueo/desbloqueo de día"""
    fecha = datos['fecha']
    accion = datos['accion']

    if accion == 'bloqueado':
        emoji = "🚫"
        titulo = "Día bloqueado"
        texto = "El día ha sido bloqueado para nuevos turnos"
    else:
        emoji = "✅"
        titulo = "Día desbloqueado"
        texto = "El día ha sido habilitado para nuevos turnos"

    return f"""{emoji} *{titulo}*

📅 Fecha: {fecha}
📝 {texto}

Panel: {obtener_url_panel()}"""


def obtener_url_panel():
    """Obtiene la URL del panel admin"""
    try:
        # En producción, intentar obtener desde variables de entorno
        base_url = os.environ.get(
            'RAILWAY_STATIC_URL') or os.environ.get('RENDER_EXTERNAL_URL')
        if base_url:
            return f"{base_url}/mobile"

        # Si hay puerto configurado pero no URL específica
        if os.environ.get('PORT'):
            return f"Panel en puerto {os.environ['PORT']}"

        # En desarrollo local
        return "http://localhost:9000/mobile"
    except:
        return "Panel de administración"


def generar_mensaje_notificacion(notificacion):
    """Genera el mensaje formateado según el tipo de notificación"""
    tipo = notificacion['tipo']
    datos = notificacion['datos']

    if tipo == 'nuevo_turno':
        return formatear_mensaje_turno(datos)
    elif tipo == 'cancelacion_turno':
        return formatear_mensaje_cancelacion(datos)
    elif tipo == 'bloqueo_dia' or tipo == 'desbloqueo_dia':
        return formatear_mensaje_dia_bloqueado(datos)
    else:
        return f"Notificación: {tipo} - {datos}"


def enviar_notificaciones_pendientes():
    """Envía todas las notificaciones pendientes al admin"""
    if not config.has_whatsapp():
        print("⚠️ WhatsApp no configurado, no se pueden enviar notificaciones")
        return 0

    admin_number = config.get_admin_phone_number()
    if not admin_number:
        print("⚠️ Número de admin no configurado")
        return 0

    try:
        from src.bots.senders.whatsapp_sender import whatsapp_sender

        notificaciones = obtener_notificaciones_pendientes()
        enviadas = 0

        for i, notif in enumerate(notificaciones):
            try:
                mensaje = generar_mensaje_notificacion(notif)

                if whatsapp_sender.send_message(admin_number, mensaje):
                    # Marcar como enviada (buscar el índice real en el archivo)
                    if marcar_notificacion_enviada_por_timestamp(notif['timestamp']):
                        enviadas += 1
                        print(f"✅ Notificación enviada: {notif['tipo']}")
                    else:
                        print(
                            f"⚠️ Mensaje enviado pero no marcado: {notif['tipo']}")
                else:
                    print(f"❌ Error enviando notificación: {notif['tipo']}")

            except Exception as e:
                print(f"❌ Error procesando notificación {i}: {e}")

        print(f"📤 {enviadas} notificaciones enviadas al admin")
        return enviadas

    except Exception as e:
        print(f"❌ Error enviando notificaciones: {e}")
        return 0


def marcar_notificacion_enviada_por_timestamp(timestamp):
    """Marca una notificación como enviada usando su timestamp"""
    try:
        log_file = ADMIN_NOTIFICATIONS_PATH

        if not os.path.exists(log_file):
            return False

        with open(log_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)

        for notif in notifications:
            if notif['timestamp'] == timestamp:
                notif['enviada'] = True
                notif['enviada_timestamp'] = datetime.now().isoformat()
                break

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(f"❌ Error marcando notificación: {e}")
        return False


def notificar_admin(tipo_evento, *args, **kwargs):
    """Función general para notificar al admin sobre eventos"""
    try:
        if tipo_evento == 'nuevo_turno':
            nombre = args[0]
            telefono = args[1]
            fecha = args[2]
            hora = args[3]
            canal = kwargs.get('canal', 'WhatsApp')
            notificar_nuevo_turno(nombre, telefono, fecha, hora, canal)

        elif tipo_evento == 'cancelacion_turno':
            nombre = args[0]
            fecha = args[1]
            hora = args[2]
            canal = kwargs.get('canal', 'WhatsApp')
            notificar_cancelacion_turno(nombre, fecha, hora, canal)

        elif tipo_evento == 'bloqueo_dia':
            fecha = args[0]
            notificar_bloqueo_dia(fecha)

        elif tipo_evento == 'desbloqueo_dia':
            fecha = args[0]
            notificar_desbloqueo_dia(fecha)

        else:
            print(f"⚠️ Tipo de evento no reconocido: {tipo_evento}")

    except Exception as e:
        print(f"❌ Error en notificar_admin: {e}")


def limpiar_notificaciones_viejas(dias_antiguedad=7):
    """Limpia notificaciones más viejas que X días"""
    try:
        log_file = ADMIN_NOTIFICATIONS_PATH

        if not os.path.exists(log_file):
            return 0

        with open(log_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)

        from datetime import datetime, timedelta
        ahora = datetime.now()
        limite_tiempo = ahora - timedelta(days=dias_antiguedad)

        notificaciones_limpias = []
        eliminadas = 0

        for notif in notifications:
            try:
                timestamp_notif = datetime.fromisoformat(
                    notif['timestamp'].replace('Z', '+00:00'))
                if timestamp_notif >= limite_tiempo:
                    notificaciones_limpias.append(notif)
                else:
                    eliminadas += 1
            except:
                # Si hay error parseando fecha, conservar la notificación
                notificaciones_limpias.append(notif)

        if eliminadas > 0:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(notificaciones_limpias, f,
                          ensure_ascii=False, indent=2)
            print(f"🧹 Limpiadas {eliminadas} notificaciones viejas")

        return eliminadas

    except Exception as e:
        print(f"❌ Error limpiando notificaciones viejas: {e}")
        return 0


def contar_notificaciones_pendientes():
    """Cuenta las notificaciones pendientes sin procesarlas"""
    try:
        log_file = ADMIN_NOTIFICATIONS_PATH

        if not os.path.exists(log_file):
            return 0

        with open(log_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)

        pendientes = len(
            [n for n in notifications if not n.get('enviada', False)])
        return pendientes

    except Exception as e:
        print(f"❌ Error contando notificaciones: {e}")
        return 0


def enviar_whatsapp_directo_cancelacion(nombre, fecha, hora, telefono):
    """
    Envía notificación directa por WhatsApp al usuario cuando el admin cancela su turno
    Similar a las notificaciones del panel móvil - envío inmediato sin daemon
    """
    try:
        from src.bots.senders.whatsapp_sender import WhatsAppSender

        # Crear instancia del sender
        sender = WhatsAppSender()

        # Crear mensaje de cancelación para el usuario
        mensaje = f"""❌ *Turno Cancelado*

Hola {nombre},

Tu turno ha sido cancelado por el administrador:

📅 **Fecha:** {fecha}
⏰ **Hora:** {hora}

Si necesitas reprogramar tu turno, por favor contactanos.

Disculpa las molestias."""

        # Limpiar número de teléfono
        telefono_limpio = sender.clean_phone_number(telefono)

        print(f"📱 Enviando notificación directa a {telefono_limpio}")
        print(f"💬 Mensaje: {mensaje[:50]}...")

        # Enviar mensaje directo
        resultado = sender.send_message(telefono_limpio, mensaje)

        if resultado:
            print(
                f"✅ Notificación enviada exitosamente a {nombre} ({telefono})")
            return True
        else:
            print(f"❌ Error enviando notificación a {nombre} ({telefono})")
            return False

    except Exception as e:
        print(f"❌ Error en envío directo WhatsApp: {e}")
        import traceback
        traceback.print_exc()
        return False


def notificar_admin_cancelacion_directa(nombre, fecha, hora, telefono):
    """
    Notifica al admin que se canceló un turno Y envía WhatsApp directo al usuario
    Función híbrida: notificación al admin (diferida) + WhatsApp al usuario (inmediato)
    """
    try:
        # 1. Notificar al admin (sistema existente - diferido)
        notificar_cancelacion_turno(nombre, fecha, hora, "Panel Móvil")

        # 2. Enviar WhatsApp directo al usuario (inmediato)
        envio_exitoso = enviar_whatsapp_directo_cancelacion(
            nombre, fecha, hora, telefono)

        if envio_exitoso:
            print(
                f"🎯 Cancelación completa: Admin notificado + Usuario notificado por WhatsApp")
        else:
            print(f"⚠️ Admin notificado pero falló envío WhatsApp al usuario")

        return envio_exitoso

    except Exception as e:
        print(f"❌ Error en notificación completa de cancelación: {e}")
        return False


if __name__ == '__main__':
    # Prueba del sistema
    print("🧪 Probando sistema de notificaciones...")

    # Crear notificación de prueba
    notificar_nuevo_turno(
        "Juan Pérez", "+54 9 11 1234-5678", "2025-07-29", "15:30")

    # Mostrar notificaciones pendientes
    pendientes = obtener_notificaciones_pendientes()
    print(f"📋 Notificaciones pendientes: {len(pendientes)}")

    for notif in pendientes:
        print(f"- {notif['tipo']}: {notif['datos']}")
        mensaje = generar_mensaje_notificacion(notif)
        print(f"  Mensaje: {mensaje[:100]}...")
