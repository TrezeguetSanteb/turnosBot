import os
import logging
import asyncio
import sys
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Agregar la raíz del proyecto al path cuando se ejecuta como script independiente
if __name__ == '__main__':
    # Obtener ruta raíz del proyecto (2 niveles arriba desde src/bots/)
    project_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, os.path.join(project_root, 'src'))

# Imports usando rutas relativas para compatibilidad
try:
    # Cuando se importa como módulo desde la aplicación principal
    from core.bot_core import handle_message, user_states, user_data, cargar_config
    from services.notifications import obtener_notificaciones_pendientes, marcar_notificacion_enviada
    from core.config import get_token, config
except ImportError:
    # Cuando se ejecuta como script independiente
    project_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, os.path.join(project_root, 'src'))
    from core.bot_core import handle_message, user_states, user_data, cargar_config
    from services.notifications import obtener_notificaciones_pendientes, marcar_notificacion_enviada
    from core.config import get_token, config

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)

# Variable global para la instancia del bot
bot_instance = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    incoming_msg = "/start"
    from_number = str(update.message.from_user.id)
    print(f"🤖 Telegram Bot - Usuario: {from_number}, Mensaje: {incoming_msg}")
    respuesta = handle_message(
        incoming_msg, from_number, user_states, user_data)
    await update.message.reply_text(respuesta, parse_mode='Markdown')


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    incoming_msg = update.message.text.strip()
    from_number = str(update.message.from_user.id)
    print(f"🤖 Telegram Bot - Usuario: {from_number}, Mensaje: {incoming_msg}")
    respuesta = handle_message(
        incoming_msg, from_number, user_states, user_data)
    await update.message.reply_text(respuesta, parse_mode='Markdown')


async def enviar_notificaciones_pendientes():
    """Envía todas las notificaciones pendientes automáticamente"""
    global bot_instance
    if not bot_instance:
        return

    try:
        notificaciones = obtener_notificaciones_pendientes()
        print(
            f"🔍 Verificando notificaciones pendientes: {len(notificaciones)}")

        for notificacion in notificaciones:
            try:
                chat_id = notificacion['telefono']
                mensaje = notificacion['mensaje']

                print(
                    f"📨 Enviando notificación a {chat_id}: {notificacion['tipo']}")

                # Enviar mensaje
                await bot_instance.send_message(
                    chat_id=chat_id,
                    text=mensaje,
                    parse_mode='Markdown'
                )

                # Marcar como enviada
                marcar_notificacion_enviada(notificacion)
                print(f"✅ Notificación enviada exitosamente a {chat_id}")

                # Pausa para evitar rate limiting
                await asyncio.sleep(0.5)

            except Exception as e:
                print(
                    f"❌ Error al enviar notificación a {notificacion['telefono']}: {e}")

    except Exception as e:
        print(f"❌ Error al verificar notificaciones: {e}")


async def verificador_notificaciones():
    """Tarea en background para verificar notificaciones periódicamente"""
    while True:
        try:
            await enviar_notificaciones_pendientes()
            # Verificar cada 30 segundos
            await asyncio.sleep(30)
        except Exception as e:
            print(f"❌ Error en verificador de notificaciones: {e}")
            await asyncio.sleep(60)  # Esperar más tiempo en caso de error


def main():
    global bot_instance

    # Obtener token desde la configuración
    token = get_token()
    application = Application.builder().token(token).build()
    bot_instance = application.bot

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot de Telegram iniciado")
    application.run_polling()


if __name__ == '__main__':
    main()
