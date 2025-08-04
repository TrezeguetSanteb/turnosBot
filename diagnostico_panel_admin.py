#!/usr/bin/env python3
"""
Diagnóstico específico para el problema de cancelación desde panel admin
Ya sabemos que WhatsApp funciona (bot conversacional OK), pero el envío directo falla
"""

import os
import sys
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_whatsapp_directo_simple():
    """Test directo usando WhatsAppSender igual que hace el panel"""
    print("🔍 TEST 1: WHATSAPP SENDER DIRECTO")
    print("=" * 40)
    
    try:
        from bots.senders.whatsapp_sender import WhatsAppSender
        
        # Crear sender exactamente como lo hace el panel
        sender = WhatsAppSender()
        
        # Mensaje de prueba igual al del panel
        mensaje = """❌ *Turno Cancelado*

Hola Test Usuario,

Tu turno ha sido cancelado por el administrador:

📅 **Fecha:** 2024-12-30
⏰ **Hora:** 15:00

Si necesitas reprogramar tu turno, por favor contactanos.

Disculpa las molestias."""
        
        # Número de prueba
        telefono = "5491123456789"  # ⚠️ CAMBIAR POR TU NÚMERO
        
        print(f"📱 Enviando a: {telefono}")
        print(f"💬 Mensaje: {mensaje[:50]}...")
        
        # Limpiar número igual que el panel
        telefono_limpio = sender.clean_phone_number(telefono)
        print(f"🧹 Número limpio: {telefono_limpio}")
        
        # Enviar mensaje
        resultado = sender.send_message(telefono_limpio, mensaje)
        
        if resultado:
            print("✅ ENVÍO DIRECTO EXITOSO")
            print("   El problema NO es WhatsAppSender")
        else:
            print("❌ ENVÍO DIRECTO FALLÓ")
            print("   El problema ES WhatsAppSender")
            
        return resultado
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_funcion_panel():
    """Test de la función exacta que usa el panel"""
    print("\n🔍 TEST 2: FUNCIÓN DEL PANEL")
    print("=" * 40)
    
    try:
        from admin.notifications import enviar_whatsapp_directo_cancelacion
        
        # Datos de prueba
        nombre = "Test Panel"
        fecha = "2024-12-30"
        hora = "15:30"
        telefono = "5491123456789"  # ⚠️ CAMBIAR POR TU NÚMERO
        
        print(f"📝 Datos:")
        print(f"   Nombre: {nombre}")
        print(f"   Fecha: {fecha}")
        print(f"   Hora: {hora}")
        print(f"   Teléfono: {telefono}")
        
        # Ejecutar función exacta del panel
        resultado = enviar_whatsapp_directo_cancelacion(nombre, fecha, hora, telefono)
        
        if resultado:
            print("✅ FUNCIÓN PANEL EXITOSA")
            print("   La función del panel funciona correctamente")
        else:
            print("❌ FUNCIÓN PANEL FALLÓ")
            print("   Hay problema en la función del panel")
            
        return resultado
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flujo_completo():
    """Test del flujo completo que debería ejecutar el panel"""
    print("\n🔍 TEST 3: FLUJO COMPLETO PANEL")
    print("=" * 40)
    
    try:
        from admin.notifications import notificar_admin_cancelacion_directa
        
        # Datos de prueba
        nombre = "Test Flujo"
        fecha = "2024-12-30"
        hora = "16:00"
        telefono = "5491123456789"  # ⚠️ CAMBIAR POR TU NÚMERO
        
        print(f"📝 Simulando cancelación desde panel:")
        print(f"   Nombre: {nombre}")
        print(f"   Fecha: {fecha}")
        print(f"   Hora: {hora}")
        print(f"   Teléfono: {telefono}")
        
        # Ejecutar función híbrida (igual que el panel)
        resultado = notificar_admin_cancelacion_directa(nombre, fecha, hora, telefono)
        
        if resultado:
            print("✅ FLUJO COMPLETO EXITOSO")
            print("   ✓ Admin notificado (diferido)")
            print("   ✓ Usuario notificado por WhatsApp (directo)")
        else:
            print("⚠️ FLUJO COMPLETO PARCIAL")
            print("   ✓ Admin notificado (diferido)")
            print("   ❌ Error en WhatsApp directo al usuario")
            
        return resultado
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_logs_admin():
    """Verificar si las notificaciones al admin se están registrando"""
    print("\n🔍 TEST 4: LOGS DE ADMIN")
    print("=" * 40)
    
    try:
        from core.paths import ADMIN_NOTIFICATIONS_PATH
        import json
        
        print(f"📁 Archivo admin: {ADMIN_NOTIFICATIONS_PATH}")
        
        if os.path.exists(ADMIN_NOTIFICATIONS_PATH):
            with open(ADMIN_NOTIFICATIONS_PATH, 'r', encoding='utf-8') as f:
                notifications = json.loads(f.read())
            
            # Buscar notificaciones recientes de cancelación
            cancelaciones = [n for n in notifications if n.get('tipo') == 'cancelacion_turno']
            
            print(f"📊 Notificaciones de cancelación: {len(cancelaciones)}")
            
            if cancelaciones:
                print("🔍 Últimas 3 cancelaciones:")
                for i, notif in enumerate(cancelaciones[-3:], 1):
                    timestamp = notif.get('timestamp', 'N/A')[:19]
                    datos = notif.get('datos', {})
                    nombre = datos.get('nombre', 'N/A')
                    print(f"   {i}. {nombre} - {timestamp}")
                
                return True
            else:
                print("⚠️ No hay notificaciones de cancelación registradas")
                return False
        else:
            print("❌ Archivo de notificaciones no existe")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verificar_config_whatsapp():
    """Verificar configuración específica de WhatsApp"""
    print("\n🔍 TEST 5: CONFIG WHATSAPP")
    print("=" * 40)
    
    try:
        from core.config import config
        
        # Verificar que config tiene WhatsApp
        has_whatsapp = config.has_whatsapp()
        print(f"📱 WhatsApp configurado: {'✅' if has_whatsapp else '❌'}")
        
        if has_whatsapp:
            # Verificar variables específicas
            token = getattr(config, 'WHATSAPP_ACCESS_TOKEN', None) or getattr(config, 'WHATSAPP_TOKEN', None)
            phone_id = getattr(config, 'WHATSAPP_PHONE_NUMBER_ID', None) or getattr(config, 'WHATSAPP_PHONE_ID', None)
            
            if token:
                print(f"🔑 Token: {token[:4]}***{token[-4:]}")
            else:
                print("❌ Token no encontrado")
                
            if phone_id:
                print(f"📞 Phone ID: {phone_id}")
            else:
                print("❌ Phone ID no encontrado")
                
        return has_whatsapp
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar diagnóstico completo"""
    print("🚀 DIAGNÓSTICO PANEL ADMIN - CANCELACIÓN")
    print("=" * 50)
    print("Problema: El panel registra la cancelación al admin")
    print("pero NO envía WhatsApp directo al usuario")
    print("=" * 50)
    
    # Ejecutar tests
    tests = [
        ("Config WhatsApp", verificar_config_whatsapp),
        ("WhatsApp Directo", test_whatsapp_directo_simple),
        ("Función Panel", test_funcion_panel),
        ("Flujo Completo", test_flujo_completo),
        ("Logs Admin", verificar_logs_admin)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            print(f"\n🧪 EJECUTANDO: {nombre}")
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"💥 ERROR: {e}")
            resultados.append((nombre, False))
    
    # Análisis de resultados
    print("\n📊 RESUMEN DIAGNÓSTICO")
    print("=" * 30)
    
    for nombre, ok in resultados:
        status = "✅" if ok else "❌"
        print(f"{status} {nombre}: {'OK' if ok else 'FALLO'}")
    
    # Diagnóstico específico
    config_ok, whatsapp_ok, funcion_ok, flujo_ok, logs_ok = [r[1] for r in resultados]
    
    print(f"\n🎯 DIAGNÓSTICO:")
    print("-" * 20)
    
    if not config_ok:
        print("❌ PROBLEMA: Configuración de WhatsApp")
        print("   → Revisar variables de entorno")
    elif not whatsapp_ok:
        print("❌ PROBLEMA: WhatsAppSender no funciona")
        print("   → Error en envío directo")
        print("   → Revisar credenciales o número de teléfono")
    elif not funcion_ok:
        print("❌ PROBLEMA: Función del panel tiene errores")
        print("   → Error en enviar_whatsapp_directo_cancelacion()")
    elif not flujo_ok:
        print("❌ PROBLEMA: Flujo híbrido falla")
        print("   → Error en notificar_admin_cancelacion_directa()")
    else:
        print("🤔 PROBLEMA MISTERIOSO:")
        print("   → Todas las funciones funcionan individualmente")
        print("   → Pero el panel no ejecuta el envío directo")
        print("   → Posibles causas:")
        print("     • El endpoint del panel no está llamando la función")
        print("     • Error silencioso en el contexto del panel")
        print("     • Problema de permisos o entorno en Railway")
    
    if logs_ok:
        print("\n✅ Las notificaciones al admin SÍ funcionan")
        print("   El problema es SOLO el envío directo al usuario")
    
    print(f"\n💡 SIGUIENTE PASO:")
    print("Ejecutar este script EN RAILWAY para ver qué falla específicamente")

if __name__ == "__main__":
    main()
