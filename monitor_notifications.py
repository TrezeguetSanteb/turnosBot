#!/usr/bin/env python3
"""
Script de monitoreo de notificaciones para TurnosBot
Permite verificar y limpiar notificaciones pendientes
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    try:
        from admin.notifications import (
            contar_notificaciones_pendientes, 
            obtener_notificaciones_pendientes, 
            limpiar_notificaciones_viejas
        )
        from core.config import config
        
        print("🔍 === MONITOR DE NOTIFICACIONES ===")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Estado de configuración
        print("📊 Configuración:")
        print(f"   Intervalo daemon: {config.NOTIFICATION_INTERVAL} segundos ({config.NOTIFICATION_INTERVAL/60:.1f} min)")
        print(f"   WhatsApp: {'✅ Configurado' if config.has_whatsapp() else '❌ No configurado'}")
        print()
        
        # Estado de notificaciones
        print("📋 Notificaciones:")
        pendientes = contar_notificaciones_pendientes()
        print(f"   Pendientes: {pendientes}")
        
        if pendientes > 0:
            print("\n📋 Detalle de notificaciones pendientes:")
            notifs = obtener_notificaciones_pendientes()
            for i, notif in enumerate(notifs, 1):
                tipo = notif.get('tipo', 'N/A')
                timestamp = notif.get('timestamp', 'N/A')
                fecha_datos = notif.get('datos', {}).get('fecha', 'N/A')
                print(f"   {i}. {tipo} - {timestamp[:19]} - Fecha: {fecha_datos}")
        
        print()
        
        # Opción de limpieza
        if pendientes > 0:
            respuesta = input("¿Limpiar notificaciones viejas (>24h)? (s/N): ").lower()
            if respuesta == 's':
                eliminadas = limpiar_notificaciones_viejas(1)  # Más de 1 día
                print(f"🧹 Eliminadas {eliminadas} notificaciones viejas")
                nuevas_pendientes = contar_notificaciones_pendientes()
                print(f"📊 Notificaciones restantes: {nuevas_pendientes}")
        
        print("\n✅ Monitoreo completado")
        
    except Exception as e:
        print(f"❌ Error en monitoreo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
