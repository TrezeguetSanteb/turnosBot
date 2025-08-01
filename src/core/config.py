"""
Configuración centralizada para el sistema de turnos.
Soporta múltiples canales: Telegram y WhatsApp.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class BotConfig:
    """Configuración centralizada para múltiples canales"""

    def __init__(self):
        # Telegram Bot
        self.BOT_TOKEN = os.getenv('BOT_TOKEN')

        # WhatsApp Bot (Meta API)
        self.WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv(
            'WHATSAPP_BUSINESS_ACCOUNT_ID')

        # Configuración general
        self.NOTIFICATION_INTERVAL = int(
            os.getenv('NOTIFICATION_INTERVAL', '60'))
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    def get_telegram_token(self):
        """Obtiene el token de Telegram"""
        if not self.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN no está configurado en el archivo .env")
        return self.BOT_TOKEN

    def get_whatsapp_config(self):
        """Obtiene la configuración de WhatsApp"""
        if not all([self.WHATSAPP_ACCESS_TOKEN, self.WHATSAPP_PHONE_NUMBER_ID]):
            raise ValueError(
                "Configuración de WhatsApp incompleta en el archivo .env")
        return {
            'access_token': self.WHATSAPP_ACCESS_TOKEN,
            'phone_number_id': self.WHATSAPP_PHONE_NUMBER_ID,
            'business_account_id': self.WHATSAPP_BUSINESS_ACCOUNT_ID
        }

    def has_telegram(self):
        """Verifica si Telegram está configurado"""
        return bool(self.BOT_TOKEN)

    def has_whatsapp(self):
        """Verifica si WhatsApp está configurado"""
        return bool(self.WHATSAPP_ACCESS_TOKEN and self.WHATSAPP_PHONE_NUMBER_ID)

    def get_admin_phone_number(self):
        """Obtiene el número de teléfono del administrador"""
        return self.ADMIN_PHONE_NUMBER


# Instancia global de configuración
config = BotConfig()


# Funciones de compatibilidad (para mantener código existente)
def get_token():
    """Obtiene el token de Telegram (función legacy)"""
    return config.get_telegram_token()
