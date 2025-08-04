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


async def enviar_whatsapp_admin(notificaciones):
    """Envía notificaciones al administrador por WhatsApp"""
    if not config.has_whatsapp():
        print("⚠️ WhatsApp no está configurado")
        return 0

    try:
        from bots.senders.whatsapp_sender import whatsapp_sender

        print(f"📱 Notificaciones WhatsApp al admin: {len(notificaciones)}")

        enviadas = 0
        for notificacion in notificaciones:
            try:
                telefono = notificacion['telefono']
                mensaje = notificacion['mensaje']

                print(f"📨 Enviando WhatsApp al admin: {notificacion['tipo']}")

                # Usar el método sincrónico del objeto whatsapp_sender
                success = whatsapp_sender.send_message(telefono, mensaje)

                if success:
                    # Marcar como enviada en el sistema de admin
                    marcar_notificacion_enviada_por_timestamp(notificacion['timestamp'])
                    print(f"✅ WhatsApp enviado al admin")
                    enviadas += 1
                else:
                    print(f"❌ Error WhatsApp al admin")

                await asyncio.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"❌ Error WhatsApp al admin: {e}")

        return enviadas

    except ImportError:
        print("⚠️ WhatsApp sender no disponible")
        return 0
    except Exception as e:
        print(f"❌ Error general WhatsApp admin: {e}")
        return 0


async def main():
    """Función principal"""
    print("🚀 Iniciando envío de notificaciones WhatsApp...")

    # Verificar configuración de WhatsApp primero
    if not config.has_whatsapp():
        print("❌ WhatsApp no está configurado")
        return 0

    total_enviadas = 0

    # 1. Procesar notificaciones de usuarios
    notificaciones_usuarios = obtener_notificaciones_pendientes()
    if notificaciones_usuarios:
        print(f"� Notificaciones a usuarios: {len(notificaciones_usuarios)}")
        print("🔗 Canal: WhatsApp Business API")
        enviadas_usuarios = await enviar_whatsapp(notificaciones_usuarios)
        total_enviadas += enviadas_usuarios
        print(f"✅ Usuarios notificados: {enviadas_usuarios}")
    else:
        print("� No hay notificaciones a usuarios")

    # 2. Procesar notificaciones del admin
    notificaciones_admin = obtener_notificaciones_admin()
    if notificaciones_admin and config.get_admin_phone_number():
        print(f"📊 Notificaciones al admin: {len(notificaciones_admin)}")
        # Convertir notificaciones de admin al formato esperado
        notificaciones_admin_formatted = []
        for notif in notificaciones_admin:
            if not notif.get('enviada', False):
                from admin.notifications import generar_mensaje_notificacion
                mensaje = generar_mensaje_notificacion(notif)
                notificaciones_admin_formatted.append({
                    'telefono': config.get_admin_phone_number(),
                    'mensaje': mensaje,
                    'tipo': notif['tipo'],
                    'timestamp': notif['timestamp']
                })
        
        if notificaciones_admin_formatted:
            print("🔗 Canal: WhatsApp Business API (Admin)")
            enviadas_admin = await enviar_whatsapp_admin(notificaciones_admin_formatted)
            total_enviadas += enviadas_admin
            print(f"✅ Admin notificado: {enviadas_admin}")
    else:
        if not config.get_admin_phone_number():
            print("⚠️ Número de admin no configurado")
        else:
            print("📭 No hay notificaciones al admin")

    # Limpiar notificaciones enviadas
    if total_enviadas > 0:
        print("🧹 Limpiando notificaciones enviadas...")
        eliminadas = limpiar_notificaciones_enviadas()
        print(f"✅ Proceso completado - Enviadas: {total_enviadas}, Eliminadas: {eliminadas}")
    else:
        print("📭 No hay notificaciones pendientes")

    return total_enviadas


if __name__ == '__main__':
    asyncio.run(main())
