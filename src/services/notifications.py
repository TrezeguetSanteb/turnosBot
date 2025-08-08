"""
Módulo de servicios de notificaciones
"""
import os
import requests
from datetime import datetime


def notificar_cancelacion_turno(nombre, fecha, hora, telefono):
    """
    Notificar al cliente sobre la cancelación de su turno
    """
    try:
        mensaje = f"""
❌ *Turno Cancelado*

Hola {nombre}, 

Tu turno ha sido cancelado:
📅 Fecha: {fecha}
⏰ Hora: {hora}

Si tienes dudas, contáctanos.

¡Esperamos verte pronto! 🦷
        """.strip()

        return enviar_whatsapp(telefono, mensaje)

    except Exception as e:
        print(f"❌ Error notificando cancelación: {e}")
        return False


def notificar_dia_bloqueado(fecha):
    """
    Notificar a usuarios con turnos en un día que será bloqueado
    """
    try:
        # Esta función debería obtener turnos de la fecha y notificar a cada usuario
        # Por ahora devolvemos lista vacía como placeholder
        notificaciones_enviadas = []
        
        # TODO: Implementar lógica para:
        # 1. Obtener turnos de la fecha
        # 2. Notificar a cada cliente
        # 3. Retornar lista de notificaciones enviadas
        
        return notificaciones_enviadas

    except Exception as e:
        print(f"❌ Error notificando día bloqueado: {e}")
        return []


def enviar_whatsapp(phone_number, message):
    """
    Enviar mensaje de WhatsApp a un número específico
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
            print(f"✅ WhatsApp enviado a {phone_number}")
            return True
        else:
            print(f"❌ Error enviando WhatsApp: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error crítico enviando WhatsApp: {e}")
        return False


def obtener_notificaciones_pendientes():
    """
    Obtener notificaciones pendientes del sistema
    """
    # Placeholder - implementación futura con BD o archivo
    return []


def marcar_notificacion_enviada(notificacion):
    """
    Marcar una notificación como enviada
    """
    # Placeholder - implementación futura
    return True
