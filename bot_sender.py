#!/usr/bin/env python3
"""
Script para enviar notificaciones por Telegram.
Usa el token configurado en .env - cambia solo BOT_TOKEN para usar diferentes bots.
"""

import asyncio
import logging
from notifications import obtener_notificaciones_pendientes, marcar_notificacion_enviada, limpiar_notificaciones_enviadas
from bot_config import get_token, config

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)


async def enviar_notificaciones():
    """Envía notificaciones por Telegram"""
    try:
        from telegram import Bot
        token = get_token()
        bot = Bot(token=token)

        notificaciones = obtener_notificaciones_pendientes()
        telegram_notifications = [
            n for n in notificaciones if n['telefono'].isdigit()]

        print(f"📱 Notificaciones encontradas: {len(telegram_notifications)}")

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
                print(f"✅ Enviado a {chat_id}")
                enviadas += 1

                await asyncio.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"❌ Error enviando a {notificacion['telefono']}: {e}")

        return enviadas

    except ImportError:
        print("⚠️ python-telegram-bot no disponible")
        return 0
    except Exception as e:
        print(f"❌ Error general: {e}")
        return 0


async def main():
    """Función principal"""
    print("🚀 Iniciando envío de notificaciones...")

    # Verificar notificaciones pendientes
    notificaciones = obtener_notificaciones_pendientes()
    if not notificaciones:
        print("📭 No hay notificaciones pendientes")
        return

    print(f"📊 Notificaciones pendientes: {len(notificaciones)}")

    # Enviar notificaciones
    enviadas = await enviar_notificaciones()

    # Limpiar notificaciones enviadas
    print("🧹 Limpiando notificaciones enviadas...")
    eliminadas = limpiar_notificaciones_enviadas()

    print(
        f"✅ Proceso completado - Enviadas: {enviadas}, Eliminadas: {eliminadas}")
    return enviadas


if __name__ == '__main__':
    asyncio.run(main())
