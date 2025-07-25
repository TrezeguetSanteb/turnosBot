"""
Configuración centralizada para el sistema de turnos.
Solo cambias BOT_TOKEN en .env para usar diferentes bots.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class BotConfig:
    """Configuración centralizada para el bot"""

    def __init__(self):
        # Token del bot (único - esto es lo único que necesitas cambiar)
        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        if not self.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN no está configurado en el archivo .env")

        # Configuración general
        self.NOTIFICATION_INTERVAL = int(
            os.getenv('NOTIFICATION_INTERVAL', '60'))
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    def get_token(self):
        """Obtiene el token del bot"""
        return self.BOT_TOKEN


# Instancia global de configuración
config = BotConfig()


# Función principal para obtener el token
def get_token():
    """Obtiene el token del bot desde la configuración"""
    return config.get_token()
