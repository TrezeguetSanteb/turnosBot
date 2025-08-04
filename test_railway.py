#!/usr/bin/env python3
"""
Diagnóstico COMPLETO para Railway - Con solución de hibernación
Este script debe ejecutarse en Railway para identificar y solucionar problemas
"""

import sys
import os
import json
import traceback
import time
from datetime import datetime

# Configurar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def log_railway(mensaje, nivel="INFO"):
    """Log específico para Railway con timestamp"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] [{nivel}] TURNOSBOT: {mensaje}", flush=True)

def verificar_hibernacion_railway():
    """Verifica si el sistema anti-hibernación está funcionando"""
    log_railway("🔍 VERIFICANDO SISTEMA ANTI-HIBERNACIÓN")
    
    try:
        # Verificar variables de Railway
        railway_vars = ['RAILWAY_STATIC_URL', 'RAILWAY_ENVIRONMENT', 'RAILWAY_SERVICE_NAME']
        es_railway = any(os.environ.get(var) for var in railway_vars)
        
        log_railway(f"Es Railway: {es_railway}")
        
        if es_railway:
            railway_url = os.environ.get('RAILWAY_STATIC_URL')
            log_railway(f"URL Railway: {railway_url}")
            
            # Verificar daemon con keep-alive
            from services.daemon import is_railway, KEEP_ALIVE_INTERVAL
            log_railway(f"Daemon detecta Railway: {is_railway}")
            log_railway(f"Intervalo keep-alive: {KEEP_ALIVE_INTERVAL}s ({KEEP_ALIVE_INTERVAL/60:.1f} min)")
            
            # Test del endpoint keep-alive
            try:
                import requests
                if railway_url:
                    keep_alive_url = f"{railway_url}/api/keep-alive"
                    log_railway(f"Probando endpoint: {keep_alive_url}")
                    
                    response = requests.get(keep_alive_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        log_railway("✅ Endpoint keep-alive funciona")
                        log_railway(f"   Status: {data.get('status')}")
                    else:
                        log_railway(f"⚠️ Endpoint respondió {response.status_code}")
                else:
                    log_railway("⚠️ No hay URL Railway para probar endpoint")
                    
            except Exception as e:
                log_railway(f"❌ Error probando endpoint: {e}")
        else:
            log_railway("💻 Entorno local - sin anti-hibernación")
            
        return es_railway
        
    except Exception as e:
        log_railway(f"❌ Error verificando hibernación: {e}", "ERROR")
        return False

def test_cancelacion_completa():
    """Test completo de cancelación paso a paso"""
    log_railway("🎯 INICIANDO TEST COMPLETO DE CANCELACIÓN")
    
    try:
        # Paso 1: Verificar configuración
        log_railway("Paso 1: Verificando configuración...")
        from core.config import config
        log_railway(f"WhatsApp configurado: {config.has_whatsapp()}")
        log_railway(f"Intervalo daemon: {config.NOTIFICATION_INTERVAL} segundos")
        
        # Paso 2: Crear un turno de prueba
        log_railway("Paso 2: Creando turno de prueba...")
        from core.database import crear_turno, obtener_todos_los_turnos
        
        # Usar número de prueba específico
        test_phone = "+5491199998888"
        test_name = "Test Railway User"
        test_fecha = "2025-08-15"
        test_hora = "16:00"
        
        exito = crear_turno(test_name, test_fecha, test_hora, test_phone)
        log_railway(f"Turno creado: {exito}")
        
        if not exito:
            log_railway("❌ FALLO: No se pudo crear turno de prueba", "ERROR")
            return False
        
        # Paso 3: Verificar que el turno existe
        turnos = obtener_todos_los_turnos()
        turno_test = None
        for turno in turnos:
            if turno[4] == test_phone:  # telefono
                turno_test = turno
                break
        
        if not turno_test:
            log_railway("❌ FALLO: Turno de prueba no encontrado en BD", "ERROR")
            return False
            
        log_railway(f"Turno encontrado: ID {turno_test[0]} - {turno_test[1]}")
        
        # Paso 4: Simular cancelación desde panel
        log_railway("Paso 3: Simulando cancelación desde panel del admin...")
        from core.database import eliminar_turno_admin
        from services.notifications import notificar_cancelacion_turno
        
        turno_id, nombre, fecha, hora, telefono = turno_test
        
        # Eliminar turno
        eliminado = eliminar_turno_admin(turno_id)
        log_railway(f"Turno eliminado de BD: {eliminado}")
        
        if not eliminado:
            log_railway("❌ FALLO: No se pudo eliminar turno", "ERROR")
            return False
        
        # Crear notificación
        log_railway("Paso 4: Creando notificación de cancelación...")
        notificar_cancelacion_turno(turno_id, nombre, fecha, hora, telefono)
        log_railway(f"Notificación creada para {telefono}")
        
        # Paso 5: Verificar que la notificación se creó
        log_railway("Paso 5: Verificando notificación creada...")
        from services.notifications import obtener_notificaciones_pendientes
        
        notifs = obtener_notificaciones_pendientes()
        notif_test = None
        for notif in notifs:
            if notif.get('telefono') == test_phone:
                notif_test = notif
                break
        
        if not notif_test:
            log_railway("❌ FALLO: Notificación no se creó", "ERROR")
            return False
            
        log_railway(f"✅ Notificación encontrada: {notif_test['tipo']}")
        log_railway(f"   Teléfono: {notif_test['telefono']}")
        log_railway(f"   Timestamp: {notif_test['timestamp']}")
        log_railway(f"   Enviado: {notif_test.get('enviado', False)}")
        
        # Paso 6: Test del bot_sender
        log_railway("Paso 6: Probando bot_sender...")
        import subprocess
        
        result = subprocess.run(
            [sys.executable, 'src/bots/senders/bot_sender.py'],
            capture_output=True,
            text=True,
            timeout=60  # Más tiempo en Railway
        )
        
        log_railway(f"Bot sender return code: {result.returncode}")
        
        if result.stdout:
            log_railway("Bot sender output:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    log_railway(f"  {line}")
        
        if result.stderr:
            log_railway("Bot sender errors:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    log_railway(f"  ERROR: {line}")
        
        # Paso 7: Verificar estado final de la notificación
        log_railway("Paso 7: Verificando estado final...")
        notifs_final = obtener_notificaciones_pendientes()
        notif_final = None
        for notif in notifs_final:
            if notif.get('telefono') == test_phone:
                notif_final = notif
                break
        
        if notif_final:
            enviado = notif_final.get('enviado', False)
            log_railway(f"Estado final de la notificación: Enviado = {enviado}")
            
            if not enviado and config.has_whatsapp():
                log_railway("⚠️ WARNING: WhatsApp configurado pero notificación no enviada", "WARN")
                return False
            elif not enviado and not config.has_whatsapp():
                log_railway("✅ OK: Notificación no enviada porque WhatsApp no está configurado")
                return True
            elif enviado:
                log_railway("✅ OK: Notificación marcada como enviada")
                return True
        
        log_railway("✅ TEST DE CANCELACIÓN COMPLETADO EXITOSAMENTE")
        return True
        
    except Exception as e:
        log_railway(f"❌ ERROR EN TEST DE CANCELACIÓN: {str(e)}", "ERROR")
        log_railway(f"Traceback: {traceback.format_exc()}", "ERROR")
        return False

def test_daemon_isolado():
    """Test del daemon en modo aislado"""
    log_railway("🤖 TEST DEL DAEMON EN RAILWAY")
    
    try:
        # Test import del daemon
        from services.daemon import main as daemon_main
        log_railway("✅ Daemon importado correctamente")
        
        # Test de configuración del daemon
        from core.config import config
        log_railway(f"Intervalo configurado: {config.NOTIFICATION_INTERVAL}")
        
        # Test de ejecución del bot_sender directamente
        log_railway("Ejecutando bot_sender directamente...")
        import subprocess
        
        env = os.environ.copy()
        result = subprocess.run(
            [sys.executable, 'src/bots/senders/bot_sender.py'],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
            cwd=os.getcwd()
        )
        
        log_railway(f"Resultado bot_sender: código {result.returncode}")
        
        if result.stdout:
            for line in result.stdout.split('\n'):
                if line.strip():
                    log_railway(f"STDOUT: {line}")
        
        if result.stderr:
            for line in result.stderr.split('\n'):
                if line.strip():
                    log_railway(f"STDERR: {line}")
        
        return result.returncode == 0
        
    except Exception as e:
        log_railway(f"❌ ERROR EN TEST DAEMON: {str(e)}", "ERROR")
        log_railway(f"Traceback: {traceback.format_exc()}", "ERROR")
        return False

def verificar_entorno_railway():
    """Verificar entorno específico de Railway"""
    log_railway("🚂 VERIFICANDO ENTORNO RAILWAY")
    
    # Variables de Railway
    railway_vars = [
        'RAILWAY_STATIC_URL',
        'RAILWAY_ENVIRONMENT', 
        'RAILWAY_SERVICE_NAME',
        'RAILWAY_PROJECT_NAME',
        'PORT'
    ]
    
    es_railway = False
    for var in railway_vars:
        valor = os.getenv(var)
        if valor:
            es_railway = True
            log_railway(f"{var}: {valor}")
        else:
            log_railway(f"{var}: No configurada")
    
    log_railway(f"Ejecutándose en Railway: {'✅ SÍ' if es_railway else '❌ NO'}")
    
    # Variables críticas de WhatsApp
    whatsapp_vars = [
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_PHONE_NUMBER_ID', 
        'WHATSAPP_VERIFY_TOKEN',
        'ADMIN_PHONE_NUMBER'
    ]
    
    log_railway("Variables de WhatsApp:")
    todas_configuradas = True
    for var in whatsapp_vars:
        valor = os.getenv(var)
        if valor:
            masked = valor[:10] + "..." if len(valor) > 10 else "***"
            log_railway(f"  {var}: {masked}")
        else:
            log_railway(f"  {var}: ❌ NO CONFIGURADA")
            todas_configuradas = False
    
    return es_railway, todas_configuradas

def main():
    log_railway("=" * 60)
    log_railway("🔍 DIAGNÓSTICO RAILWAY - SISTEMA DE NOTIFICACIONES")
    log_railway("=" * 60)
    
    # Información básica
    log_railway(f"Python version: {sys.version}")
    log_railway(f"Working directory: {os.getcwd()}")
    log_railway(f"Args: {sys.argv}")
    
    # *** NUEVO: Verificar sistema anti-hibernación ***
    hibernacion_ok = verificar_hibernacion_railway()
    
    # Verificar entorno
    es_railway, whatsapp_ok = verificar_entorno_railway()
    
    # Test del daemon
    daemon_ok = test_daemon_isolado()
    log_railway(f"Daemon test: {'✅ OK' if daemon_ok else '❌ FALLO'}")
    
    # Test completo de cancelación
    cancelacion_ok = test_cancelacion_completa()
    log_railway(f"Test cancelación: {'✅ OK' if cancelacion_ok else '❌ FALLO'}")
    
    # Resumen final
    log_railway("=" * 60)
    log_railway("📊 RESUMEN DEL DIAGNÓSTICO")
    log_railway(f"🚂 Railway: {'✅ Detectado' if es_railway else '❌ No detectado'}")
    log_railway(f"🛌 Anti-hibernación: {'✅ Activo' if hibernacion_ok else '❌ Inactivo'}")
    log_railway(f"📱 WhatsApp: {'✅ Configurado' if whatsapp_ok else '❌ No configurado'}")
    log_railway(f"🤖 Daemon: {'✅ Funcional' if daemon_ok else '❌ Con problemas'}")
    log_railway(f"🎯 Cancelación: {'✅ Funcional' if cancelacion_ok else '❌ Con problemas'}")
    
    # Análisis del problema
    if es_railway and whatsapp_ok and not hibernacion_ok:
        log_railway("🔍 PROBLEMA IDENTIFICADO: HIBERNACIÓN DE RAILWAY", "WARNING")
        log_railway("💡 SOLUCIÓN: El daemon ahora incluye sistema anti-hibernación", "WARNING")
        log_railway("🔧 ACCIÓN REQUERIDA: Reiniciar la aplicación en Railway", "WARNING")
    
    if es_railway and whatsapp_ok and daemon_ok and cancelacion_ok and hibernacion_ok:
        log_railway("🎉 SISTEMA FUNCIONANDO CORRECTAMENTE")
        return 0
    else:
        log_railway("⚠️ SISTEMA CON PROBLEMAS - Ver logs arriba")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        log_railway(f"💥 ERROR CRÍTICO: {str(e)}", "ERROR")
        log_railway(f"Traceback: {traceback.format_exc()}", "ERROR")
        sys.exit(1)
