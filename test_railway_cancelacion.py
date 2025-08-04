#!/usr/bin/env python3
"""
Script para probar específicamente el flujo de cancelación en Railway
Simula el proceso completo: panel → notificación → daemon → WhatsApp
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# Configurar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def log_mensaje(mensaje):
    """Log con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {mensaje}", flush=True)

def test_cancelacion_flow():
    """Test completo del flujo de cancelación"""
    log_mensaje("🧪 === TEST FLUJO CANCELACIÓN COMPLETO ===")
    
    try:
        # Importar funciones necesarias
        from services.notifications import notificar_cancelacion_turno, obtener_notificaciones_pendientes
        
        # 1. Simular cancelación desde panel
        log_mensaje("1️⃣ Simulando cancelación desde panel admin...")
        
        turno_id = 9999
        nombre = "Test Railway"
        fecha = "2024-12-20"
        hora = "15:30"
        telefono = "+5491123456789"  # Número de prueba formato internacional
        
        # Registrar notificación (igual que hace el panel)
        resultado = notificar_cancelacion_turno(turno_id, nombre, fecha, hora, telefono)
        
        if resultado:
            log_mensaje("   ✅ Notificación registrada correctamente")
        else:
            log_mensaje("   ❌ Error registrando notificación")
            return False
        
        # 2. Verificar que la notificación quedó pendiente
        log_mensaje("2️⃣ Verificando notificaciones pendientes...")
        
        pendientes = obtener_notificaciones_pendientes()
        cancelaciones_pendientes = [n for n in pendientes if n.get('tipo') == 'cancelacion_turno']
        
        log_mensaje(f"   Total pendientes: {len(pendientes)}")
        log_mensaje(f"   Cancelaciones pendientes: {len(cancelaciones_pendientes)}")
        
        # Buscar nuestra notificación de prueba
        test_encontrada = False
        for notif in cancelaciones_pendientes:
            if (notif.get('turno_id') == turno_id and 
                notif.get('telefono') == telefono):
                test_encontrada = True
                log_mensaje("   ✅ Notificación de prueba encontrada:")
                log_mensaje(f"      ID: {notif.get('turno_id')}")
                log_mensaje(f"      Nombre: {notif.get('nombre', 'N/A')}")
                log_mensaje(f"      Fecha: {notif.get('fecha', 'N/A')} {notif.get('hora', 'N/A')}")
                log_mensaje(f"      Teléfono: {notif.get('telefono')}")
                log_mensaje(f"      Tipo: {notif.get('tipo')}")
                log_mensaje(f"      Enviado: {notif.get('enviado', False)}")
                break
        
        if not test_encontrada:
            log_mensaje("   ❌ Notificación de prueba NO encontrada")
            return False
        
        # 3. Ejecutar daemon (bot_sender)
        log_mensaje("3️⃣ Ejecutando daemon (bot_sender.py)...")
        
        try:
            resultado = subprocess.run(
                [sys.executable, 'src/bots/senders/bot_sender.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            log_mensaje(f"   Código de salida: {resultado.returncode}")
            
            if resultado.stdout:
                log_mensaje("   📤 OUTPUT del daemon:")
                for line in resultado.stdout.split('\n'):
                    if line.strip():
                        log_mensaje(f"      {line}")
            
            if resultado.stderr and resultado.stderr.strip():
                log_mensaje("   ⚠️ ERRORES del daemon:")
                for line in resultado.stderr.split('\n'):
                    if line.strip():
                        log_mensaje(f"      {line}")
            
            # 4. Verificar estado después del daemon
            log_mensaje("4️⃣ Verificando estado después del daemon...")
            
            pendientes_despues = obtener_notificaciones_pendientes()
            cancelaciones_despues = [n for n in pendientes_despues if n.get('tipo') == 'cancelacion_turno']
            
            log_mensaje(f"   Pendientes después: {len(pendientes_despues)}")
            log_mensaje(f"   Cancelaciones pendientes después: {len(cancelaciones_despues)}")
            
            # Verificar si nuestra notificación fue procesada
            test_procesada = True
            for notif in cancelaciones_despues:
                if (notif.get('turno_id') == turno_id and 
                    notif.get('telefono') == telefono):
                    test_procesada = False
                    break
            
            if test_procesada:
                log_mensaje("   ✅ Notificación de prueba fue procesada por el daemon")
            else:
                log_mensaje("   ⚠️ Notificación de prueba sigue pendiente")
                log_mensaje("      Esto puede ser normal si WhatsApp no está configurado")
            
            return True
            
        except subprocess.TimeoutExpired:
            log_mensaje("   ⏰ Timeout ejecutando daemon")
            return False
        except Exception as e:
            log_mensaje(f"   ❌ Error ejecutando daemon: {e}")
            return False
        
    except Exception as e:
        log_mensaje(f"❌ Error en test de flujo: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_configuracion_whatsapp():
    """Verificar configuración de WhatsApp"""
    log_mensaje("\n📱 === VERIFICACIÓN WHATSAPP ===")
    
    vars_whatsapp = [
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_PHONE_NUMBER_ID',
        'WHATSAPP_VERIFY_TOKEN',
        'ADMIN_PHONE_NUMBER'
    ]
    
    configurado = True
    for var in vars_whatsapp:
        value = os.environ.get(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            log_mensaje(f"   ✅ {var}: {masked}")
        else:
            log_mensaje(f"   ❌ {var}: NO CONFIGURADA")
            configurado = False
    
    if configurado:
        log_mensaje("   ✅ WhatsApp configurado correctamente")
    else:
        log_mensaje("   ❌ WhatsApp NO configurado - notificaciones no se enviarán")
    
    return configurado

def verificar_entorno_railway():
    """Verificar si estamos en Railway"""
    log_mensaje("\n🚂 === VERIFICACIÓN ENTORNO ===")
    
    railway_vars = ['RAILWAY_STATIC_URL', 'RAILWAY_ENVIRONMENT', 'RAILWAY_SERVICE_NAME']
    es_railway = any(os.environ.get(var) for var in railway_vars)
    
    if es_railway:
        log_mensaje("   🚂 Ejecutándose en Railway")
        for var in railway_vars:
            value = os.environ.get(var)
            if value:
                log_mensaje(f"      {var}: {value}")
    else:
        log_mensaje("   💻 Ejecutándose en entorno local")
    
    # Verificar intervalo de notificaciones
    interval = os.environ.get('NOTIFICATION_INTERVAL', '300')
    log_mensaje(f"   ⏰ NOTIFICATION_INTERVAL: {interval}s ({int(interval)//60} min)")
    
    return es_railway

def mostrar_estado_notificaciones():
    """Mostrar estado actual de las notificaciones"""
    log_mensaje("\n📧 === ESTADO NOTIFICACIONES ===")
    
    notifications_file = 'data/notifications_log.json'
    
    if not os.path.exists(notifications_file):
        log_mensaje("   ❌ Archivo de notificaciones no existe")
        return
    
    try:
        with open(notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        total = len(notifications)
        pendientes = [n for n in notifications if not n.get('enviado', False)]
        enviadas = [n for n in notifications if n.get('enviado', False)]
        cancelaciones = [n for n in notifications if n.get('tipo') == 'cancelacion_turno']
        cancel_pendientes = [n for n in cancelaciones if not n.get('enviado', False)]
        
        log_mensaje(f"   📊 Total: {total}")
        log_mensaje(f"   📤 Enviadas: {len(enviadas)}")
        log_mensaje(f"   📭 Pendientes: {len(pendientes)}")
        log_mensaje(f"   🚨 Cancelaciones totales: {len(cancelaciones)}")
        log_mensaje(f"   ⏳ Cancelaciones pendientes: {len(cancel_pendientes)}")
        
        if cancel_pendientes:
            log_mensaje("\n   🚨 CANCELACIONES PENDIENTES:")
            for i, notif in enumerate(cancel_pendientes[-5:], 1):  # Últimas 5
                fecha = notif.get('fecha_creacion', 'N/A')
                telefono = notif.get('telefono', 'N/A')
                turno_id = notif.get('turno_id', 'N/A')
                log_mensaje(f"      {i}. {fecha}: Turno {turno_id} → {telefono}")
        
    except Exception as e:
        log_mensaje(f"   ❌ Error leyendo notificaciones: {e}")

def main():
    """Función principal"""
    log_mensaje("🧪 === TEST FLUJO CANCELACIÓN RAILWAY ===")
    log_mensaje("Este script prueba el flujo completo de cancelación de turnos\n")
    
    # 1. Verificar entorno
    es_railway = verificar_entorno_railway()
    
    # 2. Verificar WhatsApp
    whatsapp_ok = verificar_configuracion_whatsapp()
    
    # 3. Mostrar estado actual
    mostrar_estado_notificaciones()
    
    # 4. Ejecutar test completo
    log_mensaje("\n🚀 Iniciando test del flujo de cancelación...")
    
    if test_cancelacion_flow():
        log_mensaje("\n✅ TEST EXITOSO - El flujo de cancelación funciona correctamente")
        
        if not whatsapp_ok:
            log_mensaje("⚠️ NOTA: WhatsApp no configurado, las notificaciones quedan pendientes")
    else:
        log_mensaje("\n❌ TEST FALLIDO - Hay problemas en el flujo de cancelación")
    
    # 5. Mostrar estado final
    log_mensaje("\n📊 Estado final de notificaciones:")
    mostrar_estado_notificaciones()
    
    # 6. Recomendaciones
    log_mensaje("\n🔧 === RECOMENDACIONES ===")
    
    if es_railway:
        log_mensaje("📋 Para Railway:")
        log_mensaje("1. Revisar logs del servicio en Railway Dashboard")
        log_mensaje("2. Verificar que el daemon esté ejecutándose cada 5 minutos")
        log_mensaje("3. Comprobar conectividad con WhatsApp API")
        log_mensaje("4. Verificar formato de números de teléfono (+54911...)")
    
    if not whatsapp_ok:
        log_mensaje("📱 Para WhatsApp:")
        log_mensaje("1. Configurar todas las variables de entorno de WhatsApp")
        log_mensaje("2. Verificar que el access token esté vigente")
        log_mensaje("3. Comprobar que el phone_number_id sea correcto")
    
    log_mensaje("\n💡 Si las cancelaciones quedan pendientes pero WhatsApp está OK,")
    log_mensaje("   el problema puede estar en la conectividad o en los números de teléfono")

if __name__ == '__main__':
    main()
