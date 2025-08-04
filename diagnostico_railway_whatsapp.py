#!/usr/bin/env python3
"""
Diagnóstico específico para Railway - Verificar variables de WhatsApp
y el flujo completo de notificaciones directas
"""

import os
import sys
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def mostrar_variables_whatsapp():
    """Mostrar todas las variables relacionadas con WhatsApp"""
    print("🔑 VARIABLES DE ENTORNO WHATSAPP")
    print("=" * 40)
    
    # Todas las posibles variables de WhatsApp
    vars_whatsapp = [
        'WHATSAPP_TOKEN',
        'WHATSAPP_PHONE_ID', 
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_PHONE_NUMBER_ID',
        'META_API_VERSION',
        'META_ACCESS_TOKEN',
        'META_PHONE_NUMBER_ID'
    ]
    
    print("📋 Variables encontradas:")
    found = 0
    for var in vars_whatsapp:
        value = os.getenv(var)
        if value:
            # Mostrar solo parte del valor por seguridad
            if len(value) > 8:
                display = f"{value[:4]}...{value[-4:]}"
            else:
                display = "***"
            print(f"   ✅ {var} = {display}")
            found += 1
        else:
            print(f"   ❌ {var} = NO CONFIGURADA")
    
    print(f"\n📊 Total configuradas: {found}/{len(vars_whatsapp)}")
    
    return found > 0

def verificar_config_object():
    """Verificar el objeto config y sus métodos"""
    print("\n🔧 OBJETO CONFIG")
    print("=" * 40)
    
    try:
        from core.config import config
        
        print("📋 Métodos del config:")
        
        # Verificar has_whatsapp
        has_whatsapp = config.has_whatsapp()
        print(f"   config.has_whatsapp(): {has_whatsapp}")
        
        # Verificar atributos específicos
        attrs = ['WHATSAPP_TOKEN', 'WHATSAPP_PHONE_ID', 'WHATSAPP_ACCESS_TOKEN', 'WHATSAPP_PHONE_NUMBER_ID']
        for attr in attrs:
            try:
                value = getattr(config, attr, None)
                if value:
                    display = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                    print(f"   config.{attr}: {display}")
                else:
                    print(f"   config.{attr}: None")
            except:
                print(f"   config.{attr}: ERROR")
        
        return has_whatsapp
        
    except Exception as e:
        print(f"❌ Error con config: {e}")
        return False

def test_whatsapp_sender_detallado():
    """Test detallado del WhatsAppSender con más información"""
    print("\n📱 WHATSAPP SENDER DETALLADO")
    print("=" * 40)
    
    try:
        # Intentar importar
        print("1. Importando WhatsAppSender...")
        from bots.senders.whatsapp_sender import WhatsAppSender
        print("   ✅ Import exitoso")
        
        # Intentar crear instancia con manejo de errores detallado
        print("2. Creando instancia...")
        try:
            sender = WhatsAppSender()
            print("   ✅ Instancia creada exitosamente")
            
            # Test de configuración
            print("3. Testing configuración interna...")
            # Verificar atributos internos si existen
            if hasattr(sender, 'access_token'):
                token_ok = sender.access_token is not None
                print(f"   access_token: {'✅' if token_ok else '❌'}")
            
            if hasattr(sender, 'phone_number_id'):
                phone_ok = sender.phone_number_id is not None
                print(f"   phone_number_id: {'✅' if phone_ok else '❌'}")
            
            return sender
            
        except ValueError as ve:
            print(f"   ❌ Error de configuración: {ve}")
            return None
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error importando: {e}")
        return None

def test_endpoint_cancelacion_simulado():
    """Simular exactamente lo que hace el endpoint de cancelación"""
    print("\n🎭 SIMULACIÓN EXACTA DEL ENDPOINT")
    print("=" * 40)
    
    try:
        print("1. Importando funciones del endpoint...")
        from core.database import obtener_todos_los_turnos, eliminar_turno_admin
        from admin.notifications import notificar_admin_cancelacion_directa
        print("   ✅ Imports exitosos")
        
        print("2. Simulando datos del turno...")
        # Simular un turno (ID, nombre, fecha, hora, telefono)
        turno_simulado = (9999, "Usuario Test", "2024-12-31", "15:00", "5491123456789")
        turno_id, nombre, fecha, hora, telefono = turno_simulado
        
        print(f"   Turno ID: {turno_id}")
        print(f"   Nombre: {nombre}")
        print(f"   Fecha: {fecha}")
        print(f"   Hora: {hora}")
        print(f"   Teléfono: {telefono}")
        
        print("3. Ejecutando notificar_admin_cancelacion_directa...")
        exito_envio = notificar_admin_cancelacion_directa(nombre, fecha, hora, telefono)
        
        if exito_envio:
            print("   ✅ Función ejecutada exitosamente")
            print("   🎯 El usuario debería haber recibido WhatsApp")
        else:
            print("   ⚠️ Función ejecutada con errores")
            print("   📝 Admin notificado pero falló WhatsApp al usuario")
        
        return exito_envio
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        import traceback
        traceback.print_exc()
        return False

def generar_solucion():
    """Generar pasos específicos para solucionar el problema"""
    print("\n🔧 SOLUCIÓN PARA RAILWAY")
    print("=" * 40)
    
    print("📋 PASOS PARA RESOLVER:")
    print()
    print("1. 🔑 VERIFICAR VARIABLES EN RAILWAY:")
    print("   Ve a Railway → Tu proyecto → Variables")
    print("   Asegúrate que estén configuradas:")
    print("   • WHATSAPP_TOKEN (o WHATSAPP_ACCESS_TOKEN)")
    print("   • WHATSAPP_PHONE_ID (o WHATSAPP_PHONE_NUMBER_ID)")
    print("   • META_API_VERSION")
    print()
    print("2. 📱 FORMATO CORRECTO:")
    print("   • WHATSAPP_TOKEN: EAAxxxxxxxxxx (del panel de Facebook)")
    print("   • WHATSAPP_PHONE_ID: 123456789 (ID numérico)")
    print("   • META_API_VERSION: v17.0")
    print()
    print("3. 🧪 TESTING EN RAILWAY:")
    print("   Ejecutar este script en Railway para verificar:")
    print("   python diagnostico_panel_mobile.py")
    print()
    print("4. 📞 TESTING CON NÚMERO REAL:")
    print("   Cambiar en el código:")
    print("   telefono = \"5491123456789\"  # Por tu número real")
    print()
    print("5. 🔍 REVISAR LOGS DE RAILWAY:")
    print("   Cuando canceles un turno, buscar en logs:")
    print("   • \"📱 Enviando notificación directa\"")
    print("   • \"✅ Notificación enviada exitosamente\"")
    print("   • \"❌ Error en envío directo WhatsApp\"")

def main():
    """Ejecutar diagnóstico completo específico para Railway"""
    print("🚀 DIAGNÓSTICO RAILWAY - NOTIFICACIONES DIRECTAS")
    print("=" * 60)
    print("Diagnóstico específico para resolver el problema de")
    print("notificaciones directas por WhatsApp en Railway")
    print("=" * 60)
    
    # Ejecutar diagnósticos
    has_vars = mostrar_variables_whatsapp()
    has_config = verificar_config_object()
    sender = test_whatsapp_sender_detallado()
    endpoint_ok = test_endpoint_cancelacion_simulado()
    
    # Resumen y solución
    print(f"\n{'='*20} RESUMEN {'='*20}")
    print(f"Variables encontradas: {'✅' if has_vars else '❌'}")
    print(f"Config funcionando: {'✅' if has_config else '❌'}")
    print(f"WhatsApp Sender: {'✅' if sender else '❌'}")
    print(f"Endpoint simulado: {'✅' if endpoint_ok else '❌'}")
    
    if not has_vars:
        print("\n🎯 PROBLEMA PRINCIPAL: VARIABLES DE ENTORNO")
        print("Las variables de WhatsApp no están configuradas en Railway")
    elif not sender:
        print("\n🎯 PROBLEMA PRINCIPAL: CONFIGURACIÓN WHATSAPP")
        print("Las variables existen pero WhatsAppSender no se inicializa")
    elif not endpoint_ok:
        print("\n🎯 PROBLEMA PRINCIPAL: FLUJO DE NOTIFICACIONES")
        print("WhatsApp funciona pero el flujo del endpoint falla")
    else:
        print("\n🎉 TODO DEBERÍA FUNCIONAR")
        print("Si aún no llegan las notificaciones, revisar logs de Railway")
    
    generar_solucion()

if __name__ == "__main__":
    main()
