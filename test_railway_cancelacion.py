#!/usr/bin/env python3
"""
SCRIPT PARA EJECUTAR EN RAILWAY
Diagnóstico específico para el problema de cancelación desde panel admin
"""

import os
import sys
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def log(msg):
    """Log con timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def test_railway_whatsapp():
    """Test específico de WhatsApp en Railway"""
    log("🔍 RAILWAY - TEST WHATSAPP DIRECTO")
    log("=" * 40)
    
    try:
        # Verificar variables de entorno directamente
        token = os.getenv('WHATSAPP_TOKEN') or os.getenv('WHATSAPP_ACCESS_TOKEN')
        phone_id = os.getenv('WHATSAPP_PHONE_ID') or os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        api_version = os.getenv('META_API_VERSION', 'v17.0')
        
        log(f"🔑 Token: {'SET' if token else 'NOT SET'}")
        log(f"📞 Phone ID: {'SET' if phone_id else 'NOT SET'}")
        log(f"📊 API Version: {api_version}")
        
        if not token or not phone_id:
            log("❌ VARIABLES DE ENTORNO FALTANTES")
            return False
        
        # Test directo con requests
        import requests
        
        url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": "5491123456789",  # ⚠️ CAMBIAR POR TU NÚMERO
            "type": "text",
            "text": {
                "body": f"🧪 TEST RAILWAY DIRECTO - {datetime.now().strftime('%H:%M')}\n\nSi recibes esto, WhatsApp funciona OK desde Railway."
            }
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        log("📱 Enviando test directo...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        log(f"📡 Status: {response.status_code}")
        log(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            log("✅ WHATSAPP DIRECTO FUNCIONA")
            return True
        else:
            log("❌ WHATSAPP DIRECTO FALLA")
            return False
            
    except Exception as e:
        log(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_railway_whatsapp_sender():
    """Test usando WhatsAppSender en Railway"""
    log("\n🔍 RAILWAY - TEST WHATSAPP SENDER")
    log("=" * 40)
    
    try:
        from bots.senders.whatsapp_sender import WhatsAppSender
        
        sender = WhatsAppSender()
        log("✅ WhatsAppSender creado exitosamente")
        
        # Test mensaje
        mensaje = """❌ *TEST RAILWAY*

Este es un test desde Railway del sistema de cancelación.

📅 **Fecha:** 2024-12-30
⏰ **Hora:** 15:00

Si recibes esto, el WhatsAppSender funciona."""
        
        telefono = "5491123456789"  # ⚠️ CAMBIAR POR TU NÚMERO
        telefono_limpio = sender.clean_phone_number(telefono)
        
        log(f"📱 Enviando a: {telefono_limpio}")
        log(f"💬 Mensaje: {mensaje[:50]}...")
        
        resultado = sender.send_message(telefono_limpio, mensaje)
        
        if resultado:
            log("✅ WHATSAPP SENDER FUNCIONA")
            return True
        else:
            log("❌ WHATSAPP SENDER FALLA")
            return False
            
    except Exception as e:
        log(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_railway_funcion_panel():
    """Test de la función específica del panel en Railway"""
    log("\n🔍 RAILWAY - TEST FUNCIÓN PANEL")
    log("=" * 40)
    
    try:
        from admin.notifications import enviar_whatsapp_directo_cancelacion
        
        nombre = "Usuario Railway Test"
        fecha = "2024-12-30"
        hora = "16:00"
        telefono = "5491123456789"  # ⚠️ CAMBIAR POR TU NÚMERO
        
        log(f"📝 Ejecutando enviar_whatsapp_directo_cancelacion:")
        log(f"   Nombre: {nombre}")
        log(f"   Teléfono: {telefono}")
        
        resultado = enviar_whatsapp_directo_cancelacion(nombre, fecha, hora, telefono)
        
        if resultado:
            log("✅ FUNCIÓN PANEL FUNCIONA")
            return True
        else:
            log("❌ FUNCIÓN PANEL FALLA")
            return False
            
    except Exception as e:
        log(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_railway_simulacion_cancelacion():
    """Simular exactamente lo que hace el panel cuando cancela"""
    log("\n🔍 RAILWAY - SIMULACIÓN CANCELACIÓN PANEL")
    log("=" * 40)
    
    try:
        # Simular datos de turno
        turno_id = 999
        nombre = "Usuario Cancelado"
        fecha = "2024-12-30"
        hora = "17:00"
        telefono = "5491123456789"  # ⚠️ CAMBIAR POR TU NÚMERO
        
        log("📋 Simulando cancelación desde panel admin...")
        log(f"   Turno ID: {turno_id}")
        log(f"   Usuario: {nombre}")
        log(f"   Teléfono: {telefono}")
        
        # Ejecutar exactamente lo que hace el panel
        from admin.notifications import notificar_admin_cancelacion_directa
        
        log("🚀 Ejecutando notificar_admin_cancelacion_directa...")
        exito_envio = notificar_admin_cancelacion_directa(nombre, fecha, hora, telefono)
        
        if exito_envio:
            log("✅ SIMULACIÓN EXITOSA")
            log("   ✓ Admin notificado")
            log("   ✓ Usuario notificado por WhatsApp")
        else:
            log("⚠️ SIMULACIÓN PARCIAL")
            log("   ✓ Admin notificado")
            log("   ❌ Falló WhatsApp al usuario")
            
        return exito_envio
        
    except Exception as e:
        log(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_logs_railway():
    """Verificar logs y archivos en Railway"""
    log("\n🔍 RAILWAY - VERIFICAR LOGS")
    log("=" * 40)
    
    try:
        from core.paths import ADMIN_NOTIFICATIONS_PATH, NOTIFICATIONS_LOG_PATH
        import json
        
        # Verificar archivo admin
        log(f"📁 Admin notifications: {ADMIN_NOTIFICATIONS_PATH}")
        if os.path.exists(ADMIN_NOTIFICATIONS_PATH):
            with open(ADMIN_NOTIFICATIONS_PATH, 'r', encoding='utf-8') as f:
                admin_notifs = json.loads(f.read())
            log(f"   Total: {len(admin_notifs)}")
            cancelaciones = [n for n in admin_notifs if n.get('tipo') == 'cancelacion_turno']
            log(f"   Cancelaciones: {len(cancelaciones)}")
        else:
            log("   ❌ No existe")
        
        # Verificar archivo sistema
        log(f"📁 System notifications: {NOTIFICATIONS_LOG_PATH}")
        if os.path.exists(NOTIFICATIONS_LOG_PATH):
            with open(NOTIFICATIONS_LOG_PATH, 'r', encoding='utf-8') as f:
                sys_notifs = json.loads(f.read())
            log(f"   Total: {len(sys_notifs)}")
            cancelaciones = [n for n in sys_notifs if n.get('tipo') == 'cancelacion_turno']
            log(f"   Cancelaciones: {len(cancelaciones)}")
            pendientes = [n for n in sys_notifs if not n.get('enviada', False)]
            log(f"   Pendientes: {len(pendientes)}")
        else:
            log("   ❌ No existe")
        
        return True
        
    except Exception as e:
        log(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar diagnóstico completo en Railway"""
    log("🚀 DIAGNÓSTICO RAILWAY - CANCELACIÓN PANEL")
    log("=" * 50)
    log("Este script debe ejecutarse EN RAILWAY")
    log("para diagnosticar el problema específico")
    log("=" * 50)
    
    # Tests específicos para Railway
    tests = [
        ("WhatsApp Directo", test_railway_whatsapp),
        ("WhatsApp Sender", test_railway_whatsapp_sender),
        ("Función Panel", test_railway_funcion_panel),
        ("Simulación Cancelación", test_railway_simulacion_cancelacion),
        ("Logs Railway", verificar_logs_railway)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            log(f"💥 ERROR en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Análisis específico
    log("\n📊 ANÁLISIS RAILWAY")
    log("=" * 25)
    
    whatsapp_directo, whatsapp_sender, funcion_panel, simulacion, logs = [r[1] for r in resultados]
    
    for nombre, ok in resultados:
        status = "✅" if ok else "❌"
        log(f"{status} {nombre}: {'OK' if ok else 'FALLO'}")
    
    log(f"\n🎯 CONCLUSIÓN:")
    log("-" * 15)
    
    if whatsapp_directo and whatsapp_sender and funcion_panel and simulacion:
        log("🎉 TODO FUNCIONA EN RAILWAY!")
        log("   El problema debe ser que el panel NO está ejecutando la función")
        log("   → Verificar que el endpoint realmente use la función correcta")
        log("   → Agregar logs al endpoint del panel")
    elif whatsapp_directo and not whatsapp_sender:
        log("⚠️ WhatsApp API funciona pero WhatsAppSender no")
        log("   → Problema en la clase WhatsAppSender")
        log("   → Revisar configuración o imports")
    elif not whatsapp_directo:
        log("❌ WhatsApp API no funciona")
        log("   → Problema con variables de entorno")
        log("   → Verificar WHATSAPP_TOKEN y WHATSAPP_PHONE_ID")
    else:
        log("🤔 Problema específico identificado")
        log("   → Revisar logs detallados arriba")
    
    log(f"\n📱 RECORDATORIO:")
    log("Cambiar el número de teléfono en el script por tu número real")
    log("para recibir los mensajes de prueba")

if __name__ == "__main__":
    main()
