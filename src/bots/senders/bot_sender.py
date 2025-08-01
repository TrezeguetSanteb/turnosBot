#!/usr/bin/env python3
"""
Script universal para enviar notificaciones por múltiples canales.
Soporta Telegram y WhatsApp automáticamente según la configuración en .env
"""

import asyncio
import logging
import sys
import os

# Agregar la raíz del proyecto al path cuando se ejecuta como script independiente
if __name__ == '__main__':
    # Obtener ruta raíz del proyecto (3 niveles arriba desde src/bots/senders/)
    project_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', '..'))
    sys.path.insert(0, os.path.join(project_root, 'src'))

from services.notifications import obtener_notificaciones_pendientes, marcar_notificacion_enviada, limpiar_notificaciones_enviadas
from core.config import config

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)


async def enviar_telegram(notificaciones):
    """Envía notificaciones por Telegram"""
    if not config.has_telegram():
        print("⚠️ Telegram no está configurado")
        return 0

    try:
        from telegram import Bot
        token = config.get_telegram_token()
        bot = Bot(token=token)

        telegram_notifications = [
            n for n in notificaciones
            # Excluir números de WhatsApp
            if not n['telefono'].startswith('549')
        ]

        print(f"📱 Notificaciones Telegram: {len(telegram_notifications)}")

        enviadas = 0
        for notificacion in telegram_notifications:
            try:
                chat_id = notificacion['telefono']
                mensaje = notificacion['mensaje']

                print(f"📨 Enviando a {chat_id}: {notificacion['tipo']}")

                await bot.send_message(
                    chat_id=chat_id,
                    text=mensaje,
                    parse_mode='Markdown'
                )

                marcar_notificacion_enviada(notificacion)
                print(f"✅ Telegram enviado a {chat_id}")
                enviadas += 1

                await asyncio.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"❌ Error Telegram a {notificacion['telefono']}: {e}")

        return enviadas

    except ImportError:
        print("⚠️ python-telegram-bot no disponible")
        return 0
    except Exception as e:
        print(f"❌ Error general Telegram: {e}")
        return 0


async def enviar_whatsapp(notificaciones):
    """Envía notificaciones por WhatsApp"""
    if not config.has_whatsapp():
        print("⚠️ WhatsApp no está configurado")
        return 0

    try:
        from bots.senders.whatsapp_sender import whatsapp_sender

        # WhatsApp maneja números de teléfono argentinos (que empiecen con 549)
        whatsapp_notifications = [
            n for n in notificaciones
            if n['telefono'].startswith('549')
        ]

        print(f"📱 Notificaciones WhatsApp: {len(whatsapp_notifications)}")

        enviadas = 0
        for notificacion in whatsapp_notifications:
            try:
                telefono = notificacion['telefono']
                mensaje = notificacion['mensaje']

                print(
                    f"📨 Enviando WhatsApp a {telefono}: {notificacion['tipo']}")

                # Usar el método sincrónico del objeto whatsapp_sender
                success = whatsapp_sender.send_message(telefono, mensaje)

                if success:
                    marcar_notificacion_enviada(notificacion)
                    print(f"✅ WhatsApp enviado a {telefono}")
                    enviadas += 1
                else:
                    print(f"❌ Error WhatsApp a {telefono}")

                await asyncio.sleep(1)  # Rate limiting más conservador

            except Exception as e:
                print(f"❌ Error WhatsApp a {notificacion['telefono']}: {e}")

        return enviadas

    except ImportError:
        print("⚠️ WhatsApp sender no disponible")
        return 0
    except Exception as e:
        print(f"❌ Error general WhatsApp: {e}")
        return 0


async def main():
    """Función principal"""
    print("🚀 Iniciando envío universal de notificaciones...")

    # Verificar notificaciones pendientes
    notificaciones = obtener_notificaciones_pendientes()
    if not notificaciones:
        print("📭 No hay notificaciones pendientes")
        return

    print(f"📊 Notificaciones pendientes: {len(notificaciones)}")

    # Mostrar canales disponibles
    canales = []
    if config.has_telegram():
        canales.append("Telegram")
    if config.has_whatsapp():
        canales.append("WhatsApp")

    print(f"🔗 Canales disponibles: {', '.join(canales)}")

    # Enviar por todos los canales disponibles
    total_enviadas = 0

    if config.has_telegram():
        enviadas_telegram = await enviar_telegram(notificaciones)
        total_enviadas += enviadas_telegram

    if config.has_whatsapp():
        enviadas_whatsapp = await enviar_whatsapp(notificaciones)
        total_enviadas += enviadas_whatsapp

    # Limpiar notificaciones enviadas
    print("🧹 Limpiando notificaciones enviadas...")
    eliminadas = limpiar_notificaciones_enviadas()

    print(
        f"✅ Proceso completado - Enviadas: {total_enviadas}, Eliminadas: {eliminadas}")
    return total_enviadas


if __name__ == '__main__':
    asyncio.run(main())
