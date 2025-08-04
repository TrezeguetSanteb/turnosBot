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
        print("🔧 Revisar variables: WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID")
        return 0

    try:
        from bots.senders.whatsapp_sender import whatsapp_sender

        if whatsapp_sender is None:
            print("❌ WhatsApp sender no se pudo inicializar")
            print("🔧 Revisar configuración de WhatsApp")
            return 0

        print(f"📱 Notificaciones WhatsApp a procesar: {len(notificaciones)}")

        enviadas = 0
        for i, notificacion in enumerate(notificaciones, 1):
            try:
                telefono = notificacion['telefono']
                mensaje = notificacion['mensaje']
                tipo = notificacion.get('tipo', 'unknown')

                print(f"\n📨 [{i}/{len(notificaciones)}] Enviando WhatsApp:")
                print(f"    📱 Teléfono: {telefono}")
                print(f"    🏷️ Tipo: {tipo}")
                print(f"    💬 Mensaje: {mensaje[:100]}...")

                # Usar el método sincrónico del objeto whatsapp_sender
                success = whatsapp_sender.send_message(telefono, mensaje)

                if success:
                    marcar_notificacion_enviada(notificacion)
                    print(f"✅ WhatsApp enviado exitosamente a {telefono}")
                    enviadas += 1
                else:
                    print(f"❌ Error enviando WhatsApp a {telefono}")
                    print("🔍 Revisar logs arriba para detalles del error")

                # Rate limiting para evitar límites de API
                await asyncio.sleep(2)

            except Exception as e:
                print(f"💥 Excepción enviando WhatsApp a {notificacion.get('telefono', 'unknown')}: {e}")
                import traceback
                traceback.print_exc()

        print(f"\n📊 Resumen envío WhatsApp:")
        print(f"    Total procesadas: {len(notificaciones)}")
        print(f"    Enviadas exitosamente: {enviadas}")
        print(f"    Fallidas: {len(notificaciones) - enviadas}")

        return enviadas

    except ImportError:
        print("⚠️ WhatsApp sender no disponible (error de importación)")
        print("🔧 Verificar que el módulo whatsapp_sender existe y es válido")
        return 0
    except Exception as e:
        print(f"❌ Error general en envío WhatsApp: {e}")
        import traceback
        traceback.print_exc()
        return 0


async def main():
    """Función principal"""
    print("🚀 Iniciando envío de notificaciones WhatsApp...")
    print(f"⏰ Timestamp: {asyncio.get_event_loop().time()}")

    # Verificar notificaciones pendientes
    print("\n📋 Verificando notificaciones pendientes...")
    notificaciones = obtener_notificaciones_pendientes()
    
    if not notificaciones:
        print("📭 No hay notificaciones pendientes")
        print("💡 Para generar notificaciones:")
        print("   1. Cancelar un turno desde el panel admin")
        print("   2. Verificar que se guarde en data/notifications_log.json")
        return 0

    print(f"📊 Notificaciones pendientes encontradas: {len(notificaciones)}")
    
    # Mostrar tipos de notificaciones
    tipos = {}
    for notif in notificaciones:
        tipo = notif.get('tipo', 'unknown')
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    print("📈 Tipos de notificaciones:")
    for tipo, count in tipos.items():
        print(f"   {tipo}: {count}")

    # Verificar configuración de WhatsApp
    print("\n🔍 Verificando configuración WhatsApp...")
    if not config.has_whatsapp():
        print("❌ WhatsApp no está configurado")
        print("🔧 Variables requeridas:")
        print("   - WHATSAPP_ACCESS_TOKEN")
        print("   - WHATSAPP_PHONE_NUMBER_ID") 
        print("   - WHATSAPP_VERIFY_TOKEN")
        print("   - ADMIN_PHONE_NUMBER")
        return 0

    print("✅ WhatsApp configurado correctamente")
    print("🔗 Canal de envío: WhatsApp Business API")

    # Enviar notificaciones
    print("\n📨 Iniciando envío de notificaciones...")
    total_enviadas = await enviar_whatsapp(notificaciones)

    # Limpiar notificaciones enviadas
    print("\n🧹 Limpiando notificaciones enviadas...")
    eliminadas = limpiar_notificaciones_enviadas()

    print(f"\n📊 === RESUMEN FINAL ===")
    print(f"📋 Notificaciones procesadas: {len(notificaciones)}")
    print(f"✅ Enviadas exitosamente: {total_enviadas}")
    print(f"❌ Fallidas: {len(notificaciones) - total_enviadas}")
    print(f"🗑️ Notificaciones eliminadas: {eliminadas}")
    
    if total_enviadas > 0:
        print("🎉 ¡Proceso completado exitosamente!")
    else:
        print("⚠️ No se enviaron notificaciones - revisar configuración")
    
    return total_enviadas


if __name__ == '__main__':
    asyncio.run(main())
