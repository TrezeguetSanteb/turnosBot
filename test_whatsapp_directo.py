#!/usr/bin/env python3
"""
TEST ESPECÍFICO WHATSAPP SENDER
Prueba directamente el envío de WhatsApp para identificar el problema exacto
"""

import os
import sys
import json
from datetime import datetime

# Configurar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def log(message):
    """Log con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)

def test_configuracion_directa():
    """Test directo de configuración de WhatsApp"""
    log("📱 === TEST CONFIGURACIÓN DIRECTA ===")
    
    # Variables requeridas
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
    verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN')
    admin_phone = os.environ.get('ADMIN_PHONE_NUMBER')
    
    log("   Verificando variables:")
    
    if access_token:
        log(f"   ✅ WHATSAPP_ACCESS_TOKEN: {access_token[:20]}... ({len(access_token)} chars)")
        if not access_token.startswith('EAA'):
            log("   ⚠️ ADVERTENCIA: Token no empieza con 'EAA'")
    else:
        log("   ❌ WHATSAPP_ACCESS_TOKEN: NO CONFIGURADA")
        return False
    
    if phone_number_id:
        log(f"   ✅ WHATSAPP_PHONE_NUMBER_ID: {phone_number_id}")
        if not phone_number_id.isdigit():
            log("   ⚠️ ADVERTENCIA: Phone Number ID contiene caracteres no numéricos")
    else:
        log("   ❌ WHATSAPP_PHONE_NUMBER_ID: NO CONFIGURADA")
        return False
    
    if verify_token:
        log(f"   ✅ WHATSAPP_VERIFY_TOKEN: {verify_token}")
    else:
        log("   ❌ WHATSAPP_VERIFY_TOKEN: NO CONFIGURADA")
        return False
    
    if admin_phone:
        log(f"   ✅ ADMIN_PHONE_NUMBER: {admin_phone}")
        if not admin_phone.startswith('+'):
            log("   ⚠️ ADVERTENCIA: Número sin formato internacional")
    else:
        log("   ❌ ADMIN_PHONE_NUMBER: NO CONFIGURADA")
        return False
    
    return True

def test_import_whatsapp_sender():
    """Test de importación del WhatsApp sender"""
    log("\n🔌 === TEST IMPORT WHATSAPP SENDER ===")
    
    try:
        log("   🔄 Importando WhatsApp sender...")
        from bots.senders.whatsapp_sender import whatsapp_sender
        
        if whatsapp_sender is None:
            log("   ❌ whatsapp_sender es None - configuración inválida")
            return False, None
        
        log("   ✅ WhatsApp sender importado correctamente")
        return True, whatsapp_sender
        
    except ImportError as e:
        log(f"   ❌ Error de importación: {e}")
        return False, None
    except Exception as e:
        log(f"   ❌ Error inesperado: {e}")
        return False, None

def test_envio_directo(whatsapp_sender):
    """Test de envío directo con WhatsApp sender"""
    log("\n📨 === TEST ENVÍO DIRECTO ===")
    
    if not whatsapp_sender:
        log("   ❌ WhatsApp sender no disponible")
        return False
    
    # Número de prueba (usar admin)
    admin_phone = os.environ.get('ADMIN_PHONE_NUMBER', '+5491123456789')
    test_message = f"🧪 TEST DIRECTO RAILWAY: {datetime.now().strftime('%H:%M:%S')} - Prueba de envío directo"
    
    log(f"   📱 Enviando a: {admin_phone}")
    log(f"   💬 Mensaje: {test_message[:50]}...")
    
    try:
        # Intentar envío directo
        success = whatsapp_sender.send_message(admin_phone, test_message)
        
        if success:
            log("   ✅ ENVÍO EXITOSO - Revisar WhatsApp")
            return True
        else:
            log("   ❌ ENVÍO FALLÓ - Revisar logs arriba")
            return False
            
    except Exception as e:
        log(f"   ❌ Error en envío: {e}")
        return False

def test_limpieza_numero():
    """Test específico de limpieza de números"""
    log("\n🔢 === TEST LIMPIEZA NÚMEROS ===")
    
    try:
        from bots.senders.whatsapp_sender import WhatsAppSender
        
        # Crear instancia temporal
        sender = WhatsAppSender()
        
        # Probar diferentes formatos
        test_numbers = [
            '+5491123456789',
            '+549116755432',
            '5491123456789',
            '549116755432',
            '1123456789',
            '116755432'
        ]
        
        log("   🧪 Probando limpieza de números:")
        
        for number in test_numbers:
            try:
                cleaned = sender._clean_phone_number(number)
                log(f"      {number} → {cleaned}")
                
                # Verificar formato final
                if cleaned.startswith('54') and len(cleaned) >= 12:
                    status = "✅"
                else:
                    status = "⚠️"
                log(f"         {status} Formato: {'OK' if status == '✅' else 'Sospechoso'}")
                
            except Exception as e:
                log(f"      ❌ Error limpiando {number}: {e}")
        
        return True
        
    except Exception as e:
        log(f"   ❌ Error en test de limpieza: {e}")
        return False

def test_api_manual():
    """Test manual de la API de WhatsApp sin usar el sender"""
    log("\n🌐 === TEST API MANUAL ===")
    
    try:
        import requests
        
        access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
        phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
        admin_phone = os.environ.get('ADMIN_PHONE_NUMBER')
        
        if not all([access_token, phone_number_id, admin_phone]):
            log("   ❌ Variables faltantes para test manual")
            return False
        
        # Limpiar número manualmente
        clean_phone = ''.join(filter(str.isdigit, admin_phone))
        if not clean_phone.startswith('54'):
            clean_phone = '54' + clean_phone
        
        log(f"   📱 Número limpio: {clean_phone}")
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "text",
            "text": {
                "body": f"🧪 TEST API MANUAL: {datetime.now().strftime('%H:%M:%S')}"
            }
        }
        
        log("   🚀 Enviando request a WhatsApp API...")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        log(f"   📊 Status: {response.status_code}")
        log(f"   📄 Response: {response.text}")
        
        if response.status_code == 200:
            log("   ✅ API MANUAL EXITOSA")
            return True
        else:
            log("   ❌ API MANUAL FALLÓ")
            
            # Analizar errores comunes
            if response.status_code == 401:
                log("      🔍 Error 401: Token inválido o expirado")
            elif response.status_code == 404:
                log("      🔍 Error 404: Phone Number ID incorrecto")
            elif response.status_code == 400:
                log("      🔍 Error 400: Formato de request incorrecto")
            
            return False
            
    except Exception as e:
        log(f"   ❌ Error en test API manual: {e}")
        return False

def main():
    """Función principal"""
    log("🧪 === TEST ESPECÍFICO WHATSAPP SENDER ===")
    log("Probando envío directo de WhatsApp para identificar el problema\n")
    
    # 1. Test configuración
    config_ok = test_configuracion_directa()
    
    if not config_ok:
        log("\n❌ CONFIGURACIÓN INVÁLIDA - No se puede continuar")
        return
    
    # 2. Test import
    import_ok, sender = test_import_whatsapp_sender()
    
    # 3. Test limpieza números
    test_limpieza_numero()
    
    # 4. Test API manual (más directo)
    api_manual_ok = test_api_manual()
    
    # 5. Test envío con sender (si importó OK)
    envio_ok = False
    if import_ok and sender:
        envio_ok = test_envio_directo(sender)
    
    # RESUMEN FINAL
    log(f"\n📋 === RESUMEN TEST ===")
    log(f"📱 Configuración: {'✅' if config_ok else '❌'}")
    log(f"🔌 Import sender: {'✅' if import_ok else '❌'}")
    log(f"🌐 API manual: {'✅' if api_manual_ok else '❌'}")
    log(f"📨 Envío sender: {'✅' if envio_ok else '❌'}")
    
    if api_manual_ok and not envio_ok:
        log("\n🔍 DIAGNÓSTICO: API funciona pero sender falla")
        log("   Problema en la clase WhatsAppSender o en su configuración")
        
    elif not api_manual_ok:
        log("\n🔍 DIAGNÓSTICO: Problema en la API de WhatsApp")
        log("   Revisar token, phone_number_id o formato de número")
        
    elif envio_ok:
        log("\n✅ TODO FUNCIONA: El problema debe estar en el daemon o en el flujo")
        
    else:
        log("\n❌ MÚLTIPLES PROBLEMAS: Revisar configuración completa")
    
    log("\n💡 SIGUIENTE PASO:")
    if api_manual_ok or envio_ok:
        log("   El envío funciona - revisar por qué el daemon no llama al sender")
    else:
        log("   Arreglar la configuración de WhatsApp antes de continuar")

if __name__ == '__main__':
    main()
