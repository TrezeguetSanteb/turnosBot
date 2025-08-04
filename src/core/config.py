"""
Configuración centralizada para el sistema de turnos WhatsApp.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class BotConfig:
    """Configuración centralizada para WhatsApp Bot"""

    def __init__(self):
        # WhatsApp Bot (Meta API)
        self.WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv(
            'WHATSAPP_BUSINESS_ACCOUNT_ID')

        # Número del administrador
        self.ADMIN_PHONE_NUMBER = os.getenv('ADMIN_PHONE_NUMBER')

        # Configuración general
        self.NOTIFICATION_INTERVAL = int(
            # 5 minutos por defecto
            os.getenv('NOTIFICATION_INTERVAL', '300'))
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

        # Configuración específica para Railway Sleep/Idle
        self.RAILWAY_SLEEP_OPTIMIZED = os.getenv('RAILWAY_SLEEP_OPTIMIZED', 'true').lower() == 'true'
        self.IDLE_CHECK_INTERVAL = int(os.getenv('IDLE_CHECK_INTERVAL', '300'))  # 5 minutos cuando idle
        self.ACTIVE_CHECK_INTERVAL = int(os.getenv('ACTIVE_CHECK_INTERVAL', '60'))  # 1 minuto cuando activo

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

    def has_whatsapp(self):
        """Verifica si WhatsApp está configurado"""
        has_token = bool(self.WHATSAPP_ACCESS_TOKEN)
        has_phone_id = bool(self.WHATSAPP_PHONE_NUMBER_ID)
        
        if not has_token:
            print("❌ WHATSAPP_ACCESS_TOKEN no configurado")
        if not has_phone_id:
            print("❌ WHATSAPP_PHONE_NUMBER_ID no configurado")
            
        return has_token and has_phone_id

    def get_admin_phone_number(self):
        """Obtiene el número de teléfono del administrador"""
        return self.ADMIN_PHONE_NUMBER


# Instancia global de configuración
config = BotConfig()
