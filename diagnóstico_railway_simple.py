#!/usr/bin/env python3
"""
Diagnóstico básico para Railway - Sin imports complejos
Verifica la configuración esencial y el estado de archivos
"""

import os
import json
import subprocess
import sys
from datetime import datetime

def log(message):
    """Log con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)

def check_environment():
    """Verificar entorno y variables"""
    log("🔍 === VERIFICACIÓN ENTORNO RAILWAY ===")
    
    # Detectar Railway
    railway_vars = ['RAILWAY_STATIC_URL', 'RAILWAY_ENVIRONMENT', 'RAILWAY_SERVICE_NAME']
    is_railway = any(os.environ.get(var) for var in railway_vars)
    
    if is_railway:
        log("🚂 Entorno: Railway")
        for var in railway_vars:
            value = os.environ.get(var)
            if value:
                log(f"   {var}: {value}")
    else:
        log("💻 Entorno: Local")
    
    # Variables críticas
    log("\n📱 Variables de WhatsApp:")
    whatsapp_vars = [
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_PHONE_NUMBER_ID',
        'WHATSAPP_VERIFY_TOKEN',
        'ADMIN_PHONE_NUMBER'
    ]
    
    whatsapp_configured = True
    for var in whatsapp_vars:
        value = os.environ.get(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            log(f"   ✅ {var}: {masked}")
        else:
            log(f"   ❌ {var}: NO CONFIGURADA")
            whatsapp_configured = False
    
    # Configuración del daemon
    log("\n⚙️ Configuración daemon:")
    interval = os.environ.get('NOTIFICATION_INTERVAL', '300')
    log(f"   NOTIFICATION_INTERVAL: {interval}s ({int(interval)//60} min)")
    
    return is_railway, whatsapp_configured

def check_files():
    """Verificar archivos críticos"""
    log("\n📁 === VERIFICACIÓN ARCHIVOS ===")
    
    critical_files = [
        'main.py',
        'src/admin/panel.py',
        'src/services/notifications.py',
        'src/services/daemon.py',
        'src/bots/senders/bot_sender.py',
        'src/core/config.py',
        'turnos.db'
    ]
    
    files_ok = True
    for file_path in critical_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            log(f"   ✅ {file_path} ({size} bytes)")
        else:
            log(f"   ❌ {file_path} NO EXISTE")
            files_ok = False
    
    return files_ok

def check_notifications():
    """Verificar estado de notificaciones"""
    log("\n📧 === ESTADO NOTIFICACIONES ===")
    
    notifications_file = 'data/notifications_log.json'
    
    if not os.path.exists(notifications_file):
        log("   ❌ data/notifications_log.json no existe")
        # Crear estructura básica
        os.makedirs('data', exist_ok=True)
        with open(notifications_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        log("   ✅ Archivo creado")
        return True
    
    try:
        with open(notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        total = len(notifications)
        pending = [n for n in notifications if not n.get('enviado', False)]
        sent = [n for n in notifications if n.get('enviado', False)]
        cancellations = [n for n in notifications if n.get('tipo') == 'cancelacion_turno']
        pending_cancellations = [n for n in cancellations if not n.get('enviado', False)]
        
        log(f"   📊 Total: {total}")
        log(f"   📤 Enviadas: {len(sent)}")
        log(f"   📭 Pendientes: {len(pending)}")
        log(f"   🚨 Cancelaciones: {len(cancellations)}")
        log(f"   ⏳ Cancelaciones pendientes: {len(pending_cancellations)}")
        
        if pending_cancellations:
            log("   🚨 CANCELACIONES PENDIENTES:")
            for i, notif in enumerate(pending_cancellations[-3:], 1):
                created = notif.get('fecha_creacion', 'N/A')
                phone = notif.get('telefono', 'N/A')
                turno_id = notif.get('turno_id', 'N/A')
                log(f"      {i}. {created}: Turno {turno_id} → {phone}")
        
        return True
        
    except Exception as e:
        log(f"   ❌ Error leyendo notificaciones: {e}")
        return False

def test_bot_sender():
    """Test del bot sender"""
    log("\n🤖 === TEST BOT SENDER ===")
    
    try:
        log("   🚀 Ejecutando src/bots/senders/bot_sender.py...")
        
        result = subprocess.run(
            [sys.executable, 'src/bots/senders/bot_sender.py'],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        
        log(f"   📊 Código de salida: {result.returncode}")
        
        if result.stdout:
            log("   📤 OUTPUT:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    log(f"      {line}")
        
        if result.stderr:
            log("   ⚠️ ERRORES:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    log(f"      {line}")
        
        success = result.returncode == 0
        if success:
            log("   ✅ Bot sender ejecutado exitosamente")
        else:
            log("   ❌ Error ejecutando bot sender")
        
        return success
        
    except subprocess.TimeoutExpired:
        log("   ⏰ Timeout ejecutando bot sender")
        return False
    except Exception as e:
        log(f"   ❌ Error ejecutando bot sender: {e}")
        return False

def create_test_notification():
    """Crear notificación de prueba directamente en el archivo"""
    log("\n🧪 === CREAR NOTIFICACIÓN PRUEBA ===")
    
    try:
        notifications_file = 'data/notifications_log.json'
        
        # Leer notificaciones existentes
        if os.path.exists(notifications_file):
            with open(notifications_file, 'r', encoding='utf-8') as f:
                notifications = json.load(f)
        else:
            notifications = []
        
        # Crear notificación de prueba
        test_notification = {
            "id": f"test_{int(datetime.now().timestamp())}",
            "turno_id": 9999,
            "telefono": "+5491123456789",
            "mensaje": "🚨 CANCELACIÓN: Tu turno del 2024-12-20 a las 15:00 ha sido cancelado. Disculpa las molestias.",
            "tipo": "cancelacion_turno",
            "fecha_creacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "enviado": False
        }
        
        notifications.append(test_notification)
        
        # Guardar
        with open(notifications_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, indent=2, ensure_ascii=False)
        
        log("   ✅ Notificación de prueba creada")
        log(f"      ID: {test_notification['id']}")
        log(f"      Teléfono: {test_notification['telefono']}")
        log(f"      Tipo: {test_notification['tipo']}")
        
        return True
        
    except Exception as e:
        log(f"   ❌ Error creando notificación: {e}")
        return False

def check_whatsapp_api():
    """Verificar conectividad con WhatsApp API"""
    log("\n📱 === TEST WHATSAPP API ===")
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
    
    if not access_token or not phone_number_id:
        log("   ❌ Variables de WhatsApp no configuradas")
        return False
    
    try:
        import requests
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        log("   🔍 Verificando conexión...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            log("   ✅ WhatsApp API responde correctamente")
            data = response.json()
            log(f"      Phone Number ID: {data.get('id', 'N/A')}")
            return True
        else:
            log(f"   ❌ Error API: {response.status_code}")
            log(f"      Respuesta: {response.text[:200]}")
            return False
            
    except Exception as e:
        log(f"   ❌ Error verificando API: {e}")
        return False

def main():
    """Función principal"""
    log("🏥 === DIAGNÓSTICO RAILWAY - CANCELACIÓN TURNOS ===")
    log("Diagnóstico básico sin imports complejos\n")
    
    # 1. Verificar entorno
    is_railway, whatsapp_ok = check_environment()
    
    # 2. Verificar archivos
    files_ok = check_files()
    
    # 3. Verificar notificaciones
    notifications_ok = check_notifications()
    
    # 4. Crear notificación de prueba
    if notifications_ok:
        create_test_notification()
    
    # 5. Test bot sender
    bot_sender_ok = test_bot_sender()
    
    # 6. Test WhatsApp API (si está configurado)
    if whatsapp_ok:
        api_ok = check_whatsapp_api()
    else:
        api_ok = False
    
    # Resumen final
    log("\n📋 === RESUMEN DIAGNÓSTICO ===")
    
    log(f"🚂 Railway: {'✅' if is_railway else '❌'}")
    log(f"📱 WhatsApp: {'✅' if whatsapp_ok else '❌'}")
    log(f"📁 Archivos: {'✅' if files_ok else '❌'}")
    log(f"📧 Notificaciones: {'✅' if notifications_ok else '❌'}")
    log(f"🤖 Bot Sender: {'✅' if bot_sender_ok else '❌'}")
    log(f"📡 API WhatsApp: {'✅' if api_ok else '❌'}")
    
    # Diagnóstico del problema
    log("\n🔧 === DIAGNÓSTICO DEL PROBLEMA ===")
    
    if not whatsapp_ok:
        log("❌ PROBLEMA: WhatsApp no configurado")
        log("   Solución: Configurar variables de entorno en Railway")
    elif not bot_sender_ok:
        log("❌ PROBLEMA: Bot sender no funciona")
        log("   Solución: Revisar logs y dependencias")
    elif not api_ok:
        log("❌ PROBLEMA: API de WhatsApp no responde")
        log("   Solución: Verificar tokens y conectividad")
    else:
        log("✅ CONFIGURACIÓN OK: El problema puede estar en:")
        log("   1. El daemon no está ejecutándose automáticamente")
        log("   2. Los números de teléfono no están en formato correcto")
        log("   3. Problemas de timing (daemon cada 5 min)")
        
    log("\n💡 PRÓXIMOS PASOS:")
    log("1. Ejecutar este script en Railway")
    log("2. Cancelar un turno real desde el panel")
    log("3. Verificar que la notificación aparezca como pendiente")
    log("4. Esperar 5 minutos y verificar si se procesa")
    log("5. Revisar logs de Railway para errores del daemon")

if __name__ == '__main__':
    main()
