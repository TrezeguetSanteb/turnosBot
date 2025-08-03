#!/usr/bin/env python3
"""
Script para enviar notificaciones por WhatsApp.
Sistema optimizado exclusivamente para WhatsApp Business API.
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


async def enviar_whatsapp(notificaciones):
    """Envía notificaciones por WhatsApp"""
    if not config.has_whatsapp():
        print("⚠️ WhatsApp no está configurado")
        return 0

    try:
        from bots.senders.whatsapp_sender import whatsapp_sender

        print(f"📱 Notificaciones WhatsApp: {len(notificaciones)}")

        enviadas = 0
        for notificacion in notificaciones:
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

                await asyncio.sleep(1)  # Rate limiting

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
    print("🚀 Iniciando envío de notificaciones WhatsApp...")

    # Verificar notificaciones pendientes
    notificaciones = obtener_notificaciones_pendientes()
    if not notificaciones:
        print("📭 No hay notificaciones pendientes")
        return

    print(f"📊 Notificaciones pendientes: {len(notificaciones)}")

    # Verificar configuración de WhatsApp
    if not config.has_whatsapp():
        print("❌ WhatsApp no está configurado")
        return 0

    print("🔗 Canal: WhatsApp Business API")

    # Enviar notificaciones
    total_enviadas = await enviar_whatsapp(notificaciones)

    # Limpiar notificaciones enviadas
    print("🧹 Limpiando notificaciones enviadas...")
    eliminadas = limpiar_notificaciones_enviadas()

    print(
        f"✅ Proceso completado - Enviadas: {total_enviadas}, Eliminadas: {eliminadas}")
    return total_enviadas


if __name__ == '__main__':
    asyncio.run(main())
