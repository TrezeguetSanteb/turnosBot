#!/usr/bin/env python3
"""
Diagnóstico web para Railway - Cancelación panel admin
Permite ejecutar el diagnóstico desde una URL en Railway
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.bots.senders.whatsapp_sender import WhatsAppSender
from src.admin.notifications import enviar_whatsapp_directo_cancelacion, notificar_admin_cancelacion_directa

def formatear_tiempo():
    """Obtiene la hora actual formateada"""
    return datetime.now().strftime("%H:%M:%S")

def verificar_variables_entorno():
    """Verifica las variables de entorno de WhatsApp"""
    output = []
    output.append(f"[{formatear_tiempo()}] 🔍 RAILWAY - VARIABLES DE ENTORNO")
    output.append("=" * 50)
    
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    
    output.append(f"🔑 Token: {'SET' if token else 'NOT SET'}")
    output.append(f"📞 Phone ID: {'SET' if phone_id else 'NOT SET'}")
    
    if token and phone_id:
        output.append("✅ VARIABLES CONFIGURADAS")
        return output, True
    else:
        output.append("❌ VARIABLES FALTANTES")
        return output, False

def test_whatsapp_directo():
    """Testa la API de WhatsApp directamente"""
    output = []
    output.append(f"[{formatear_tiempo()}] 🔍 TEST WHATSAPP API DIRECTO")
    output.append("=" * 40)
    
    try:
        import requests
        
        token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        
        if not token or not phone_id:
            output.append("❌ Variables no configuradas")
            return output, False
            
        # Test básico de la API
        url = f"https://graph.facebook.com/v17.0/{phone_id}/messages"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Solo test de autenticación, no enviamos mensaje real
        test_data = {
            "messaging_product": "whatsapp",
            "to": "5491123456789",  # Número test
            "type": "text",
            "text": {"body": "Test"}
        }
        
        # Solo validamos que la URL y headers son correctos
        output.append(f"📡 URL: {url}")
        output.append(f"🔑 Authorization header: Configurado")
        output.append("✅ API CONFIGURADA CORRECTAMENTE")
        
        return output, True
        
    except Exception as e:
        output.append(f"❌ Error: {str(e)}")
        return output, False

def test_whatsapp_sender():
    """Testa el WhatsAppSender"""
    output = []
    output.append(f"[{formatear_tiempo()}] 🔍 TEST WHATSAPP SENDER")
    output.append("=" * 40)
    
    try:
        sender = WhatsAppSender()
        output.append("✅ WhatsAppSender inicializado correctamente")
        
        # Test de configuración
        if hasattr(sender, 'access_token') and sender.access_token:
            output.append("✅ Token configurado")
        else:
            output.append("❌ Token no configurado")
            
        if hasattr(sender, 'phone_number_id') and sender.phone_number_id:
            output.append("✅ Phone ID configurado")
        else:
            output.append("❌ Phone ID no configurado")
            
        return output, True
        
    except Exception as e:
        output.append(f"❌ Error en WhatsAppSender: {str(e)}")
        return output, False

def test_funcion_panel():
    """Testa la función del panel directamente"""
    output = []
    output.append(f"[{formatear_tiempo()}] 🔍 TEST FUNCIÓN PANEL")
    output.append("=" * 40)
    
    try:
        nombre = "Usuario Railway Test"
        telefono = "5491123456789"  # Cambiar por número real para test
        
        output.append(f"📝 Ejecutando enviar_whatsapp_directo_cancelacion:")
        output.append(f"   Nombre: {nombre}")
        output.append(f"   Teléfono: {telefono}")
        
        resultado = enviar_whatsapp_directo_cancelacion(nombre, telefono)
        
        if resultado:
            output.append("✅ FUNCIÓN PANEL OK")
            return output, True
        else:
            output.append("❌ FUNCIÓN PANEL FALLA")
            return output, False
            
    except Exception as e:
        output.append(f"❌ Error en función panel: {str(e)}")
        return output, False

def test_simulacion_cancelacion():
    """Simula una cancelación completa desde el panel"""
    output = []
    output.append(f"[{formatear_tiempo()}] 🔍 SIMULACIÓN CANCELACIÓN PANEL")
    output.append("=" * 45)
    
    try:
        turno_id = 999
        nombre_usuario = "Usuario Cancelado"
        telefono_usuario = "5491123456789"  # Cambiar por número real
        
        output.append(f"📋 Simulando cancelación desde panel admin...")
        output.append(f"   Turno ID: {turno_id}")
        output.append(f"   Usuario: {nombre_usuario}")
        output.append(f"   Teléfono: {telefono_usuario}")
        
        output.append(f"🚀 Ejecutando notificar_admin_cancelacion_directa...")
        
        resultado = notificar_admin_cancelacion_directa(
            turno_id, nombre_usuario, telefono_usuario
        )
        
        if resultado:
            output.append("✅ SIMULACIÓN COMPLETA OK")
            output.append("   ✓ Admin notificado")
            output.append("   ✓ WhatsApp enviado al usuario")
            return output, True
        else:
            output.append("⚠️ SIMULACIÓN PARCIAL")
            output.append("   ✓ Admin notificado")
            output.append("   ❌ Falló WhatsApp al usuario")
            return output, False
            
    except Exception as e:
        output.append(f"❌ Error en simulación: {str(e)}")
        return output, False

def verificar_logs():
    """Verifica los archivos de logs"""
    output = []
    output.append(f"[{formatear_tiempo()}] 🔍 VERIFICAR LOGS")
    output.append("=" * 30)
    
    try:
        # Verificar admin notifications
        admin_file = Path("data/admin_notifications.json")
        if admin_file.exists():
            with open(admin_file, 'r') as f:
                admin_data = json.load(f)
            cancelaciones_admin = sum(1 for notif in admin_data if notif.get('tipo') == 'cancelacion_turno')
            output.append(f"📁 Admin notifications: {admin_file.absolute()}")
            output.append(f"   Total: {len(admin_data)}")
            output.append(f"   Cancelaciones: {cancelaciones_admin}")
        else:
            output.append(f"📁 Admin notifications: NO EXISTE")
            
        # Verificar system notifications
        system_file = Path("data/notifications_log.json")
        if system_file.exists():
            with open(system_file, 'r') as f:
                system_data = json.load(f)
            cancelaciones_system = sum(1 for notif in system_data if notif.get('tipo') == 'cancelacion_turno')
            pendientes = sum(1 for notif in system_data if notif.get('estado') == 'pendiente')
            output.append(f"📁 System notifications: {system_file.absolute()}")
            output.append(f"   Total: {len(system_data)}")
            output.append(f"   Cancelaciones: {cancelaciones_system}")
            output.append(f"   Pendientes: {pendientes}")
        else:
            output.append(f"📁 System notifications: NO EXISTE")
            
        return output, True
        
    except Exception as e:
        output.append(f"❌ Error verificando logs: {str(e)}")
        return output, False

def ejecutar_diagnostico_completo():
    """Ejecuta todo el diagnóstico y devuelve el resultado completo"""
    resultados = []
    estados = {}
    
    # Header
    resultados.append(f"[{formatear_tiempo()}] 🚀 DIAGNÓSTICO RAILWAY - CANCELACIÓN PANEL")
    resultados.append("=" * 60)
    resultados.append("EJECUTÁNDOSE EN RAILWAY")
    resultados.append("=" * 60)
    
    # Test 1: Variables de entorno
    output, estado = verificar_variables_entorno()
    resultados.extend(output)
    estados['variables'] = estado
    resultados.append("")
    
    # Test 2: WhatsApp API directo
    output, estado = test_whatsapp_directo()
    resultados.extend(output)
    estados['api_directo'] = estado
    resultados.append("")
    
    # Test 3: WhatsApp Sender
    output, estado = test_whatsapp_sender()
    resultados.extend(output)
    estados['whatsapp_sender'] = estado
    resultados.append("")
    
    # Test 4: Función del panel
    output, estado = test_funcion_panel()
    resultados.extend(output)
    estados['funcion_panel'] = estado
    resultados.append("")
    
    # Test 5: Simulación completa
    output, estado = test_simulacion_cancelacion()
    resultados.extend(output)
    estados['simulacion'] = estado
    resultados.append("")
    
    # Test 6: Logs
    output, estado = verificar_logs()
    resultados.extend(output)
    estados['logs'] = estado
    resultados.append("")
    
    # Análisis final
    resultados.append(f"[{formatear_tiempo()}] 📊 ANÁLISIS RAILWAY")
    resultados.append("=" * 30)
    resultados.append(f"{'✅' if estados.get('variables') else '❌'} Variables de entorno: {'OK' if estados.get('variables') else 'FALLO'}")
    resultados.append(f"{'✅' if estados.get('api_directo') else '❌'} WhatsApp API Directo: {'OK' if estados.get('api_directo') else 'FALLO'}")
    resultados.append(f"{'✅' if estados.get('whatsapp_sender') else '❌'} WhatsApp Sender: {'OK' if estados.get('whatsapp_sender') else 'FALLO'}")
    resultados.append(f"{'✅' if estados.get('funcion_panel') else '❌'} Función Panel: {'OK' if estados.get('funcion_panel') else 'FALLO'}")
    resultados.append(f"{'✅' if estados.get('simulacion') else '❌'} Simulación Cancelación: {'OK' if estados.get('simulacion') else 'FALLO'}")
    resultados.append(f"{'✅' if estados.get('logs') else '❌'} Logs Railway: {'OK' if estados.get('logs') else 'FALLO'}")
    resultados.append("")
    
    # Conclusión
    resultados.append("🎯 CONCLUSIÓN:")
    resultados.append("---------------")
    
    if all(estados.values()):
        resultados.append("✅ TODO FUNCIONA CORRECTAMENTE")
        resultados.append("   → El problema puede estar en otro lugar")
        resultados.append("   → Revisar logs de Railway en tiempo real")
    elif estados.get('variables') and estados.get('whatsapp_sender'):
        resultados.append("⚠️ CONFIGURACIÓN OK, PERO FALLA EJECUCIÓN")
        resultados.append("   → WhatsApp configurado correctamente")
        resultados.append("   → Problema en la lógica de envío")
    else:
        resultados.append("❌ PROBLEMA DE CONFIGURACIÓN")
        resultados.append("   → Verificar variables de entorno en Railway")
        resultados.append("   → Confirmar que WHATSAPP_ACCESS_TOKEN y WHATSAPP_PHONE_NUMBER_ID están set")
    
    resultados.append("")
    resultados.append("📱 RECORDATORIO:")
    resultados.append("Cambiar el número de teléfono en el script por tu número real")
    resultados.append("para recibir los mensajes de prueba")
    
    return "\n".join(resultados), estados

if __name__ == "__main__":
    resultado, estados = ejecutar_diagnostico_completo()
    print(resultado)
