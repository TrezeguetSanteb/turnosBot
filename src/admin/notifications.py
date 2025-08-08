"""
Módulo de notificaciones para el administrador
"""
import os
import json
import requests
from datetime import datetime


def notificar_admin_cancelacion_directa(nombre, fecha, hora, telefono):
    """
    Enviar notificación directa por WhatsApp sobre cancelación de turno
    """
    try:
        admin_phone = os.environ.get('ADMIN_PHONE_NUMBER')
        if not admin_phone:
            print("⚠️ ADMIN_PHONE_NUMBER no configurado")
            return False

        mensaje = f"""
🚨 *Turno Cancelado por Admin*

👤 Cliente: {nombre}
📅 Fecha: {fecha}
⏰ Hora: {hora}
📱 Teléfono: {telefono}

✅ El cliente ha sido notificado automáticamente.
        """.strip()

        return enviar_whatsapp_admin(admin_phone, mensaje)

    except Exception as e:
        print(f"❌ Error enviando notificación admin: {e}")
        return False


def notificar_admin_nuevo_turno(nombre, fecha, hora, telefono, profesional_nombre=None):
    """
    Notificar al admin sobre un nuevo turno
    """
    try:
        admin_phone = os.environ.get('ADMIN_PHONE_NUMBER')
        if not admin_phone:
            return False

        profesional_info = f"\n👨‍💼 Profesional: {profesional_nombre}" if profesional_nombre else ""
        
        mensaje = f"""
📅 *Nuevo Turno Reservado*

👤 Cliente: {nombre}
📅 Fecha: {fecha}
⏰ Hora: {hora}
📱 Teléfono: {telefono}{profesional_info}

🤖 Reservado vía bot automático.
        """.strip()

        return enviar_whatsapp_admin(admin_phone, mensaje)

    except Exception as e:
        print(f"❌ Error notificando nuevo turno: {e}")
        return False


def enviar_whatsapp_admin(phone_number, message):
    """
    Enviar mensaje de WhatsApp al administrador
    """
    try:
        access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
        phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')

        if not access_token or not phone_number_id:
            print("⚠️ Variables de WhatsApp no configuradas")
            return False

        # Limpiar número de teléfono
        clean_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')

        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": clean_number,
            "type": "text",
            "text": {
                "body": message
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            print(f"✅ Notificación admin enviada a {phone_number}")
            return True
        else:
            print(f"❌ Error enviando notificación admin: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error crítico enviando notificación admin: {e}")
        return False


def obtener_notificaciones_pendientes():
    """
    Obtener lista de notificaciones pendientes (placeholder)
    """
    # Esta función debería conectarse a una BD o archivo de notificaciones
    # Por ahora devolvemos lista vacía
    return []


def contar_notificaciones_pendientes():
    """
    Contar notificaciones pendientes
    """
    return len(obtener_notificaciones_pendientes())


def limpiar_notificaciones_viejas(horas=24):
    """
    Limpiar notificaciones más antiguas que X horas
    """
    # Placeholder - en implementación real limpiaría la BD/archivo
    return 0


def marcar_notificacion_enviada(notificacion):
    """
    Marcar una notificación como enviada
    """
    # Placeholder - en implementación real actualizaría la BD/archivo
    return True


def marcar_notificacion_enviada_por_timestamp(timestamp):
    """
    Marcar notificación como enviada por timestamp
    """
    # Placeholder - en implementación real buscaría y actualizaría la BD/archivo
    return True
