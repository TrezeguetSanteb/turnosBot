#!/usr/bin/env python3
"""
Módulo para enviar mensajes por WhatsApp usando la API de Meta.
"""

import requests
import json
import logging
from src.core.config import config

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
            
            print(f"📱 Enviando WhatsApp: {to_number} → {clean_number}")

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

            print(f"🚀 Request URL: {self.base_url}")
            print(f"📝 Payload: {json.dumps(payload, indent=2)}")

            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )

            print(f"📊 Response Status: {response.status_code}")
            print(f"📄 Response Body: {response.text}")

            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get('messages', [{}])[0].get('id', 'unknown')
                print(f"✅ Mensaje enviado exitosamente (ID: {message_id})")
                logger.info(f"Mensaje enviado exitosamente a {clean_number} (ID: {message_id})")
                return True
            else:
                print(f"❌ Error enviando mensaje: {response.status_code}")
                print(f"💬 Error details: {response.text}")
                logger.error(f"Error enviando mensaje a {clean_number}: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.Timeout:
            error_msg = f"Timeout enviando mensaje a {to_number}"
            print(f"⏰ {error_msg}")
            logger.error(error_msg)
            return False
        except requests.exceptions.ConnectionError:
            error_msg = f"Error de conexión enviando mensaje a {to_number}"
            print(f"🌐 {error_msg}")
            logger.error(error_msg)
            return False
        except Exception as e:
            error_msg = f"Excepción enviando mensaje por WhatsApp a {to_number}: {e}"
            print(f"💥 {error_msg}")
            logger.error(error_msg)
            return False

    def _clean_phone_number(self, phone_number):
        """
        Limpia el número de teléfono y lo convierte al formato que Meta espera

        Args:
            phone_number (str): Número de teléfono

        Returns:
            str: Número en formato que Meta acepta
        """
        # Remover todos los caracteres no numéricos y el símbolo +
        clean = ''.join(filter(str.isdigit, phone_number))
        
        # Manejar diferentes formatos de Argentina
        if clean.startswith('549'):
            # +549XXXXXXXXX -> usar tal como está (formato internacional completo)
            return clean
        elif clean.startswith('54'):
            # +54XXXXXXXXX -> agregar 9 para celulares
            if len(clean) == 12:  # 54 + 10 dígitos
                return '549' + clean[2:]
            else:
                return clean
        elif len(clean) == 10:
            # XXXXXXXXXX (solo número local) -> agregar 549
            return '549' + clean
        elif len(clean) == 11 and clean.startswith('15'):
            # 15XXXXXXXXX -> quitar 15 y agregar 549
            return '549' + clean[2:]
        else:
            # Si no empieza con código de país, asumir Argentina (549)
            if len(clean) >= 8:
                return '549' + clean
        
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
