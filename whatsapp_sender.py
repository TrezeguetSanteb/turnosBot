#!/usr/bin/env python3
"""
Módulo para enviar mensajes por WhatsApp usando la API de Meta.
"""

import requests
import json
import logging
from bot_config import config

logger = logging.getLogger(__name__)


class WhatsAppSender:
    """Clase para enviar mensajes por WhatsApp"""

    def __init__(self):
        if not config.has_whatsapp():
            raise ValueError("WhatsApp no está configurado correctamente")

        self.whatsapp_config = config.get_whatsapp_config()
        self.access_token = self.whatsapp_config['access_token']
        self.phone_number_id = self.whatsapp_config['phone_number_id']
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"

    def send_message(self, to_number, message):
        """
        Envía un mensaje de texto por WhatsApp

        Args:
            to_number (str): Número de teléfono destino (formato: +1234567890)
            message (str): Mensaje a enviar

        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            # Limpiar el número de teléfono
            clean_number = self._clean_phone_number(to_number)

            headers = {
                'Authorization': f'Bearer {self.access_token}',
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

            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"Mensaje enviado exitosamente a {clean_number}")
                return True
            else:
                logger.error(
                    f"Error enviando mensaje a {clean_number}: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(
                f"Excepción enviando mensaje por WhatsApp a {to_number}: {e}")
            return False

    def _clean_phone_number(self, phone_number):
        """
        Limpia el número de teléfono y lo convierte al formato que Meta espera

        Args:
            phone_number (str): Número de teléfono

        Returns:
            str: Número en formato que Meta acepta
        """
        # Solo remover caracteres no numéricos
        clean = ''.join(filter(str.isdigit, phone_number))

        # Si no empieza con código de país, asumir Argentina (54)
        if not clean.startswith('54') and len(clean) >= 10:
            clean = '54' + clean

        # SOLUCIÓN: Convertir 549xxxxxxxx a 54xxxxxxxx (Meta lo prefiere así)
        if clean.startswith('549') and len(clean) == 13:
            # Remover el 9: 5492396511845 -> 542396511845
            clean = '54' + clean[3:]

        return clean


# Instancia global
try:
    whatsapp_sender = WhatsAppSender() if config.has_whatsapp() else None
    if whatsapp_sender:
        logger.info("WhatsApp sender inicializado correctamente")
    else:
        logger.warning(
            "WhatsApp sender no se inicializó (configuración faltante)")
except Exception as e:
    logger.error(f"Error inicializando WhatsApp sender: {e}")
    whatsapp_sender = None


async def send_whatsapp_message(phone_number, message):
    """
    Función async para enviar mensaje por WhatsApp (compatible con el sistema actual)

    Args:
        phone_number (str): Número de teléfono
        message (str): Mensaje a enviar

    Returns:
        bool: True si se envió correctamente
    """
    if not whatsapp_sender:
        logger.error("WhatsApp no está configurado")
        return False

    return whatsapp_sender.send_message(phone_number, message)
