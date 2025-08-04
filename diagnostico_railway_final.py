#!/usr/bin/env python3
"""
Diagnóstico específico para problemas en Railway
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def diagnostico_railway():
    """Diagnóstico específico para Railway"""
    print("🚂 === DIAGNÓSTICO PROBLEMAS RAILWAY ===")
    print(f"📅 Fecha: {datetime.now()}")
    print()
    
    print("🔍 POSIBLES CAUSAS SI NO LLEGAN NOTIFICACIONES EN RAILWAY:")
    print()
    
    print("1️⃣ **VARIABLES DE ENTORNO WHATSAPP**")
    print("   ❓ ¿Están configuradas en Railway?")
    print("   📋 Requeridas:")
    print("      - WHATSAPP_ACCESS_TOKEN")
    print("      - WHATSAPP_PHONE_NUMBER_ID") 
    print("      - WHATSAPP_VERIFY_TOKEN")
    print("   🔧 Verificar en: Railway Dashboard > Variables")
    print()
    
    print("2️⃣ **DAEMON EJECUTÁNDOSE**")
    print("   ❓ ¿El daemon está corriendo en Railway?")
    print("   📋 Debería ejecutarse cada 5 minutos")
    print("   🔧 Verificar en logs de Railway:")
    print("      - '🚀 Iniciando envío de notificaciones WhatsApp...'")
    print("      - '📊 Notificaciones pendientes: X'")
    print()
    
    print("3️⃣ **CONECTIVIDAD WHATSAPP**")
    print("   ❓ ¿Railway puede alcanzar la API de WhatsApp?")
    print("   📋 La API debe responder desde Railway")
    print("   🔧 Verificar en logs errores como:")
    print("      - 'Connection timeout'")
    print("      - 'Invalid access token'")
    print()
    
    print("4️⃣ **LOGS DE DAEMON**")
    print("   ❓ ¿Qué dicen los logs específicos?")
    print("   📋 Buscar en Railway logs:")
    print("      - '📨 Enviando WhatsApp a [telefono]: cancelacion_turno'")
    print("      - '✅ WhatsApp enviado a [telefono]'")
    print("      - '❌ Error WhatsApp a [telefono]'")
    print()
    
    print("5️⃣ **VERIFICACIÓN NÚMEROS DE TELÉFONO**")
    print("   ❓ ¿Los números están en formato correcto?")
    print("   📋 Formato requerido: +54911XXXXXXXX")
    print("   🔧 WhatsApp Business requiere formato internacional")
    print()
    
    # Mostrar estado actual del sistema
    print("📊 ESTADO ACTUAL DEL SISTEMA:")
    try:
        from services.notifications import obtener_notificaciones_pendientes
        notifs = obtener_notificaciones_pendientes()
        cancelaciones = [n for n in notifs if n.get('tipo') == 'cancelacion_turno']
        
        print(f"   📨 Notificaciones pendientes: {len(notifs)}")
        print(f"   🚫 Cancelaciones pendientes: {len(cancelaciones)}")
        
        if cancelaciones:
            print("   📋 Últimas cancelaciones:")
            for i, notif in enumerate(cancelaciones[-3:], 1):
                telefono = notif.get('telefono', 'N/A')
                timestamp = notif.get('timestamp', 'N/A')
                print(f"      {i}. {telefono} - {timestamp[:19]}")
        
    except Exception as e:
        print(f"   ❌ Error obteniendo estado: {e}")
    
    print()
    print("🎯 PASOS PARA DEBUGGEAR EN RAILWAY:")
    print("1. Abrir Railway logs en tiempo real")
    print("2. Cancelar un turno desde el panel")
    print("3. Esperar 5 minutos (ciclo del daemon)")
    print("4. Verificar logs para ver:")
    print("   - Si el daemon se ejecuta")
    print("   - Si procesa las notificaciones")
    print("   - Si hay errores de WhatsApp")
    print()
    
    print("📞 COMANDO PARA VERIFICAR EN RAILWAY:")
    print("railway logs --tail")

def crear_script_test_railway():
    """Crear script para probar en Railway"""
    script_content = '''#!/usr/bin/env python3
"""
Script de test para ejecutar en Railway
"""

import sys
import os
from datetime import datetime

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("🚂 === TEST RAILWAY ===")
    print(f"📅 {datetime.now()}")
    
    # 1. Verificar config WhatsApp
    try:
        from core.config import config
        print(f"✅ Config cargada")
        print(f"📱 WhatsApp configurado: {config.has_whatsapp()}")
        
        if config.has_whatsapp():
            print("✅ Variables WhatsApp OK")
        else:
            print("❌ Variables WhatsApp FALTANTES")
            
    except Exception as e:
        print(f"❌ Error config: {e}")
    
    # 2. Verificar notificaciones
    try:
        from services.notifications import obtener_notificaciones_pendientes
        notifs = obtener_notificaciones_pendientes()
        cancelaciones = [n for n in notifs if n.get('tipo') == 'cancelacion_turno']
        
        print(f"📊 Notificaciones: {len(notifs)}")
        print(f"🚫 Cancelaciones: {len(cancelaciones)}")
        
        if cancelaciones:
            print("📋 Sample cancelaciones:")
            for i, n in enumerate(cancelaciones[-2:], 1):
                print(f"  {i}. {n.get('telefono')} - {n.get('timestamp', '')[:19]}")
                
    except Exception as e:
        print(f"❌ Error notificaciones: {e}")
    
    # 3. Test bot_sender
    try:
        print("🤖 Probando bot_sender...")
        import subprocess
        result = subprocess.run([
            sys.executable, 
            'src/bots/senders/bot_sender.py'
        ], capture_output=True, text=True, timeout=30)
        
        print(f"📤 Return code: {result.returncode}")
        if result.stdout:
            lines = result.stdout.split('\\n')[:5]  # Primeras 5 líneas
            for line in lines:
                if line.strip():
                    print(f"📤 {line}")
        if result.stderr:
            print(f"⚠️ Stderr: {result.stderr[:200]}")
            
    except Exception as e:
        print(f"❌ Error bot_sender: {e}")

if __name__ == "__main__":
    main()
'''

    with open('/home/santi/Documents/personal/turnosBot/test_railway_debug.py', 'w') as f:
        f.write(script_content)
    
    print("📝 Script creado: test_railway_debug.py")
    print("🚂 Para usar en Railway:")
    print("   1. Subir el script")
    print("   2. Ejecutar: python test_railway_debug.py")

def main():
    diagnostico_railway()
    print()
    crear_script_test_railway()

if __name__ == "__main__":
    main()
