#!/usr/bin/env python3
"""
DIAGNÓSTICO ENVÍO WHATSAPP - Railway
Identifica por qué el bot sender no envía notificaciones aunque se ejecute
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def log(message):
    """Log con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)

def verificar_variables_whatsapp():
    """Verificar variables de WhatsApp detalladamente"""
    log("📱 === VERIFICAR VARIABLES WHATSAPP ===")
    
    variables = {
        'WHATSAPP_ACCESS_TOKEN': os.environ.get('WHATSAPP_ACCESS_TOKEN'),
        'WHATSAPP_PHONE_NUMBER_ID': os.environ.get('WHATSAPP_PHONE_NUMBER_ID'),
        'WHATSAPP_VERIFY_TOKEN': os.environ.get('WHATSAPP_VERIFY_TOKEN'),
        'ADMIN_PHONE_NUMBER': os.environ.get('ADMIN_PHONE_NUMBER')
    }
    
    todas_configuradas = True
    
    for var, value in variables.items():
        if value:
            # Mostrar formato para detectar problemas
            if var == 'WHATSAPP_ACCESS_TOKEN':
                if value.startswith('EAA'):
                    log(f"   ✅ {var}: EAA... ({len(value)} chars)")
                else:
                    log(f"   ⚠️ {var}: No empieza con EAA ({len(value)} chars)")
            elif var == 'WHATSAPP_PHONE_NUMBER_ID':
                if value.isdigit() and len(value) > 10:
                    log(f"   ✅ {var}: {value[:6]}... ({len(value)} chars)")
                else:
                    log(f"   ⚠️ {var}: Formato sospechoso ({len(value)} chars)")
            elif var == 'ADMIN_PHONE_NUMBER':
                if value.startswith('+'):
                    log(f"   ✅ {var}: {value}")
                else:
                    log(f"   ⚠️ {var}: Sin formato internacional ({value})")
            else:
                masked = value[:8] + "..." if len(value) > 8 else "***"
                log(f"   ✅ {var}: {masked}")
        else:
            log(f"   ❌ {var}: NO CONFIGURADA")
            todas_configuradas = False
    
    return todas_configuradas, variables

def test_whatsapp_api():
    """Probar conectividad con WhatsApp API"""
    log("\n📡 === TEST WHATSAPP API ===")
    
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
    
    if not access_token or not phone_number_id:
        log("   ❌ Variables faltantes para test API")
        return False
    
    try:
        import requests
        
        # Test 1: Verificar phone number ID
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        log("   🔍 Test 1: Verificando Phone Number ID...")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log(f"   ✅ Phone Number ID válido: {data.get('id')}")
            log(f"      Display name: {data.get('display_phone_number', 'N/A')}")
        elif response.status_code == 401:
            log("   ❌ Error 401: Token inválido o expirado")
            return False
        elif response.status_code == 404:
            log("   ❌ Error 404: Phone Number ID incorrecto")
            return False
        else:
            log(f"   ❌ Error {response.status_code}: {response.text}")
            return False
        
        # Test 2: Probar envío a número de prueba
        log("   📨 Test 2: Probando envío de mensaje...")
        
        test_phone = os.environ.get('ADMIN_PHONE_NUMBER', '+5491123456789')
        
        send_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        
        message_data = {
            "messaging_product": "whatsapp",
            "to": test_phone,
            "type": "text",
            "text": {
                "body": f"🧪 TEST RAILWAY: {datetime.now().strftime('%H:%M:%S')}"
            }
        }
        
        response = requests.post(
            send_url, 
            headers=headers, 
            json=message_data, 
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id', 'N/A')
            log(f"   ✅ Mensaje enviado exitosamente (ID: {message_id})")
            log(f"      Destinatario: {test_phone}")
            return True
        else:
            log(f"   ❌ Error enviando mensaje: {response.status_code}")
            log(f"      Respuesta: {response.text}")
            return False
            
    except ImportError:
        log("   ❌ requests no disponible")
        return False
    except Exception as e:
        log(f"   ❌ Error en test API: {e}")
        return False

def analizar_bot_sender():
    """Analizar la salida del bot sender detalladamente"""
    log("\n🤖 === ANALIZAR BOT SENDER ===")
    
    try:
        log("   🚀 Ejecutando bot_sender.py con análisis detallado...")
        
        # Ejecutar bot sender
        result = subprocess.run(
            [sys.executable, 'src/bots/senders/bot_sender.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        log(f"   📊 Código de salida: {result.returncode}")
        
        # Analizar stdout línea por línea
        if result.stdout:
            log("   📤 ANÁLISIS OUTPUT:")
            lines = result.stdout.split('\n')
            
            notificaciones_detectadas = False
            whatsapp_configurado = False
            intentos_envio = 0
            envios_exitosos = 0
            errores_envio = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                log(f"      📝 {line}")
                
                # Detectar estados específicos
                if "notificaciones pendientes:" in line.lower():
                    notificaciones_detectadas = True
                    num = ''.join(filter(str.isdigit, line))
                    if num and int(num) > 0:
                        log(f"      ✅ Hay {num} notificaciones pendientes")
                    else:
                        log(f"      📭 No hay notificaciones pendientes")
                        
                elif "whatsapp no está configurado" in line.lower():
                    log("      ❌ PROBLEMA: WhatsApp no configurado en bot_sender")
                    
                elif "enviando whatsapp" in line.lower():
                    intentos_envio += 1
                    whatsapp_configurado = True
                    
                elif "✅" in line and "enviado" in line.lower():
                    envios_exitosos += 1
                    
                elif "❌" in line and ("error" in line.lower() or "fallo" in line.lower()):
                    errores_envio += 1
            
            # Resumen del análisis
            log("\n   📋 RESUMEN ANÁLISIS:")
            log(f"      Notificaciones detectadas: {'✅' if notificaciones_detectadas else '❌'}")
            log(f"      WhatsApp configurado: {'✅' if whatsapp_configurado else '❌'}")
            log(f"      Intentos de envío: {intentos_envio}")
            log(f"      Envíos exitosos: {envios_exitosos}")
            log(f"      Errores de envío: {errores_envio}")
            
            # Diagnóstico específico
            if not notificaciones_detectadas:
                log("      🔍 DIAGNÓSTICO: No se detectaron notificaciones pendientes")
            elif not whatsapp_configurado:
                log("      🔍 DIAGNÓSTICO: WhatsApp no está configurado en el bot")
            elif intentos_envio == 0:
                log("      🔍 DIAGNÓSTICO: No se intentó enviar ningún mensaje")
            elif errores_envio > 0:
                log("      🔍 DIAGNÓSTICO: Hay errores en el envío de mensajes")
            elif envios_exitosos == 0:
                log("      🔍 DIAGNÓSTICO: Se intentó enviar pero falló silenciosamente")
        
        # Analizar stderr
        if result.stderr:
            log("   ⚠️ ERRORES:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    log(f"      {line}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        log("   ⏰ Timeout ejecutando bot_sender")
        return False
    except Exception as e:
        log(f"   ❌ Error ejecutando bot_sender: {e}")
        return False

def verificar_notificaciones_pendientes():
    """Verificar si realmente hay notificaciones pendientes"""
    log("\n📧 === VERIFICAR NOTIFICACIONES PENDIENTES ===")
    
    notifications_file = 'data/notifications_log.json'
    
    if not os.path.exists(notifications_file):
        log("   ❌ Archivo de notificaciones no existe")
        return False
    
    try:
        with open(notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        total = len(notifications)
        pendientes = [n for n in notifications if not n.get('enviado', False)]
        cancelaciones_pendientes = [n for n in pendientes if n.get('tipo') == 'cancelacion_turno']
        
        log(f"   📊 Total notificaciones: {total}")
        log(f"   📭 Pendientes: {len(pendientes)}")
        log(f"   🚨 Cancelaciones pendientes: {len(cancelaciones_pendientes)}")
        
        if cancelaciones_pendientes:
            log("   🔍 CANCELACIONES PENDIENTES:")
            for i, notif in enumerate(cancelaciones_pendientes[-3:], 1):
                telefono = notif.get('telefono', 'N/A')
                fecha_creacion = notif.get('fecha_creacion', 'N/A')
                turno_id = notif.get('turno_id', 'N/A')
                
                # Verificar formato del teléfono
                if telefono.startswith('+549'):
                    telefono_ok = "✅"
                elif telefono.startswith('+54'):
                    telefono_ok = "⚠️"
                else:
                    telefono_ok = "❌"
                
                log(f"      {i}. {telefono_ok} {telefono} - Turno {turno_id} - {fecha_creacion}")
        
        return len(cancelaciones_pendientes) > 0
        
    except Exception as e:
        log(f"   ❌ Error leyendo notificaciones: {e}")
        return False

def crear_notificacion_test():
    """Crear notificación de test para verificar envío"""
    log("\n🧪 === CREAR NOTIFICACIÓN TEST ===")
    
    try:
        notifications_file = 'data/notifications_log.json'
        os.makedirs('data', exist_ok=True)
        
        # Leer notificaciones existentes
        if os.path.exists(notifications_file):
            with open(notifications_file, 'r', encoding='utf-8') as f:
                notifications = json.load(f)
        else:
            notifications = []
        
        # Crear notificación de test con teléfono admin
        admin_phone = os.environ.get('ADMIN_PHONE_NUMBER', '+5491123456789')
        
        test_notification = {
            "id": f"test_envio_{int(datetime.now().timestamp())}",
            "turno_id": 8888,
            "telefono": admin_phone,
            "mensaje": f"🧪 TEST ENVÍO RAILWAY: {datetime.now().strftime('%H:%M:%S')} - Si recibes este mensaje, el envío funciona correctamente.",
            "tipo": "cancelacion_turno",
            "fecha_creacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "enviado": False,
            "nombre": "Test Usuario",
            "fecha": "2024-12-25",
            "hora": "15:00",
            "test": True
        }
        
        notifications.append(test_notification)
        
        # Guardar
        with open(notifications_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, indent=2, ensure_ascii=False)
        
        log(f"   ✅ Notificación de test creada")
        log(f"      ID: {test_notification['id']}")
        log(f"      Teléfono: {test_notification['telefono']}")
        log(f"      Mensaje: {test_notification['mensaje'][:50]}...")
        
        return True
        
    except Exception as e:
        log(f"   ❌ Error creando notificación test: {e}")
        return False

def main():
    """Función principal"""
    log("📱 === DIAGNÓSTICO ENVÍO WHATSAPP RAILWAY ===")
    log("Identificando por qué bot_sender no envía notificaciones\n")
    
    # 1. Verificar variables de WhatsApp
    whatsapp_ok, variables = verificar_variables_whatsapp()
    
    # 2. Test API de WhatsApp (si variables OK)
    api_ok = False
    if whatsapp_ok:
        api_ok = test_whatsapp_api()
    
    # 3. Verificar notificaciones pendientes
    hay_pendientes = verificar_notificaciones_pendientes()
    
    # 4. Crear notificación de test
    if whatsapp_ok:
        crear_notificacion_test()
    
    # 5. Analizar bot sender
    bot_sender_ok = analizar_bot_sender()
    
    # DIAGNÓSTICO FINAL
    log(f"\n🔧 === DIAGNÓSTICO FINAL ===")
    
    log(f"📱 Variables WhatsApp: {'✅' if whatsapp_ok else '❌'}")
    log(f"📡 API WhatsApp: {'✅' if api_ok else '❌'}")
    log(f"📧 Hay pendientes: {'✅' if hay_pendientes else '❌'}")
    log(f"🤖 Bot sender ejecuta: {'✅' if bot_sender_ok else '❌'}")
    
    if not whatsapp_ok:
        log("\n❌ PROBLEMA: Variables de WhatsApp mal configuradas")
        log("🔧 SOLUCIÓN: Configurar todas las variables en Railway")
        
    elif not api_ok:
        log("\n❌ PROBLEMA: API de WhatsApp no responde o token inválido")
        log("🔧 SOLUCIÓN:")
        log("   1. Verificar que el token no haya expirado")
        log("   2. Comprobar el Phone Number ID")
        log("   3. Revisar permisos de la app de WhatsApp")
        
    elif not hay_pendientes:
        log("\n⚠️ INFO: No hay notificaciones pendientes para enviar")
        log("💡 Cancelar un turno desde el panel para crear notificaciones")
        
    elif bot_sender_ok and api_ok:
        log("\n✅ TODO PARECE OK - Revisar logs detallados arriba")
        log("💡 El problema puede estar en:")
        log("   1. Formato de números de teléfono")
        log("   2. Rate limiting de WhatsApp")
        log("   3. Números no registrados en WhatsApp")
        
    else:
        log("\n❌ PROBLEMA: Bot sender no funciona correctamente")
        log("🔧 Revisar errores en la salida detallada arriba")
    
    log("\n📋 SIGUIENTE PASO:")
    log("1. Si creaste la notificación de test, ejecuta bot_sender manualmente:")
    log("   python src/bots/senders/bot_sender.py")
    log("2. Revisa si recibes el mensaje de test en WhatsApp")
    log("3. Si no llega, el problema está en la API o configuración")

if __name__ == '__main__':
    main()
