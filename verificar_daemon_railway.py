#!/usr/bin/env python3
"""
Script para verificar específicamente el daemon en Railway
Comprueba que el daemon esté ejecutándose y procesando notificaciones cada 5 minutos
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta

# Configurar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def log_mensaje(mensaje):
    """Log con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {mensaje}", flush=True)

def verificar_configuracion_daemon():
    """Verificar configuración del daemon"""
    log_mensaje("⚙️ === VERIFICACIÓN CONFIGURACIÓN DAEMON ===")
    
    try:
        from core.config import config
        
        interval = config.NOTIFICATION_INTERVAL
        log_mensaje(f"   📅 Intervalo configurado: {interval} segundos ({interval//60} minutos)")
        
        # Verificar configuración de WhatsApp
        has_whatsapp = config.has_whatsapp()
        log_mensaje(f"   📱 WhatsApp configurado: {'✅ Sí' if has_whatsapp else '❌ No'}")
        
        if has_whatsapp:
            log_mensaje("   📡 El daemon DEBERÍA estar ejecutándose")
        else:
            log_mensaje("   ⚠️ El daemon NO se ejecutará sin WhatsApp configurado")
        
        return has_whatsapp, interval
        
    except Exception as e:
        log_mensaje(f"   ❌ Error verificando configuración: {e}")
        return False, 300

def monitorear_notificaciones(duracion_minutos=10):
    """Monitorear cambios en notificaciones durante un tiempo"""
    log_mensaje(f"👀 === MONITOREO NOTIFICACIONES ({duracion_minutos} min) ===")
    
    notifications_file = 'data/notifications_log.json'
    
    if not os.path.exists(notifications_file):
        log_mensaje("   ❌ Archivo de notificaciones no existe")
        return
    
    def obtener_estado():
        try:
            with open(notifications_file, 'r', encoding='utf-8') as f:
                notifications = json.load(f)
            
            pendientes = [n for n in notifications if not n.get('enviado', False)]
            enviadas = [n for n in notifications if n.get('enviado', False)]
            cancelaciones_pendientes = [n for n in pendientes if n.get('tipo') == 'cancelacion_turno']
            
            return {
                'total': len(notifications),
                'pendientes': len(pendientes),
                'enviadas': len(enviadas),
                'cancelaciones_pendientes': len(cancelaciones_pendientes),
                'timestamp': datetime.now()
            }
        except:
            return None
    
    estados = []
    inicio = datetime.now()
    fin = inicio + timedelta(minutes=duracion_minutos)
    
    log_mensaje(f"   📊 Inicio del monitoreo: {inicio.strftime('%H:%M:%S')}")
    log_mensaje(f"   🎯 Fin del monitoreo: {fin.strftime('%H:%M:%S')}")
    
    # Capturar estado inicial
    estado_inicial = obtener_estado()
    if estado_inicial:
        estados.append(estado_inicial)
        log_mensaje(f"   📈 Estado inicial: {estado_inicial['pendientes']} pendientes, {estado_inicial['cancelaciones_pendientes']} cancelaciones")
    
    # Monitorear cada 30 segundos
    while datetime.now() < fin:
        time.sleep(30)
        
        estado_actual = obtener_estado()
        if estado_actual:
            estados.append(estado_actual)
            
            # Verificar cambios
            if len(estados) >= 2:
                anterior = estados[-2]
                actual = estados[-1]
                
                if (anterior['pendientes'] != actual['pendientes'] or 
                    anterior['enviadas'] != actual['enviadas']):
                    log_mensaje(f"   🔄 CAMBIO detectado: {actual['pendientes']} pendientes (+{actual['enviadas'] - anterior['enviadas']} enviadas)")
                else:
                    log_mensaje(f"   📊 Sin cambios: {actual['pendientes']} pendientes")
    
    # Resumen del monitoreo
    if len(estados) >= 2:
        inicial = estados[0]
        final = estados[-1]
        
        log_mensaje(f"\n   📋 RESUMEN MONITOREO:")
        log_mensaje(f"      Inicio: {inicial['pendientes']} pendientes, {inicial['enviadas']} enviadas")
        log_mensaje(f"      Final: {final['pendientes']} pendientes, {final['enviadas']} enviadas")
        log_mensaje(f"      Cambio: {final['enviadas'] - inicial['enviadas']} notificaciones procesadas")
        
        if final['enviadas'] > inicial['enviadas']:
            log_mensaje("   ✅ El daemon está procesando notificaciones")
        else:
            log_mensaje("   ⚠️ No se detectó actividad del daemon")

def simular_carga_notificaciones():
    """Simular varias notificaciones de cancelación para probar el daemon"""
    log_mensaje("\n🧪 === SIMULACIÓN CARGA NOTIFICACIONES ===")
    
    try:
        from services.notifications import notificar_cancelacion_turno
        
        # Crear 3 notificaciones de prueba
        notificaciones_test = [
            (1001, "Test User 1", "2024-12-20", "10:00", "+5491123456781"),
            (1002, "Test User 2", "2024-12-20", "11:00", "+5491123456782"),
            (1003, "Test User 3", "2024-12-20", "12:00", "+5491123456783"),
        ]
        
        log_mensaje(f"   📝 Creando {len(notificaciones_test)} notificaciones de prueba...")
        
        creadas = 0
        for turno_id, nombre, fecha, hora, telefono in notificaciones_test:
            try:
                resultado = notificar_cancelacion_turno(turno_id, nombre, fecha, hora, telefono)
                if resultado:
                    creadas += 1
                    log_mensaje(f"   ✅ Notificación {turno_id} creada para {telefono}")
                else:
                    log_mensaje(f"   ❌ Error creando notificación {turno_id}")
            except Exception as e:
                log_mensaje(f"   ❌ Error con notificación {turno_id}: {e}")
        
        log_mensaje(f"   📊 Total creadas: {creadas}/{len(notificaciones_test)}")
        
        if creadas > 0:
            log_mensaje("   💡 Ahora puedes monitorear si el daemon las procesa")
            return True
        
    except Exception as e:
        log_mensaje(f"   ❌ Error en simulación: {e}")
    
    return False

def verificar_proceso_daemon():
    """Verificar si el proceso del daemon está corriendo"""
    log_mensaje("\n🔍 === VERIFICACIÓN PROCESO DAEMON ===")
    
    try:
        import psutil
        
        # Buscar procesos relacionados con el daemon
        procesos_encontrados = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                if ('daemon.py' in cmdline or 
                    'bot_sender.py' in cmdline or
                    'main.py' in cmdline):
                    procesos_encontrados.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline
                    })
            except:
                continue
        
        if procesos_encontrados:
            log_mensaje(f"   ✅ {len(procesos_encontrados)} procesos relacionados encontrados:")
            for proc in procesos_encontrados:
                log_mensaje(f"      PID {proc['pid']}: {proc['cmdline']}")
        else:
            log_mensaje("   ⚠️ No se encontraron procesos del daemon")
            log_mensaje("      Esto es normal en Railway si el daemon está en un hilo")
        
    except ImportError:
        log_mensaje("   ⚠️ psutil no disponible, no se puede verificar procesos")
    except Exception as e:
        log_mensaje(f"   ❌ Error verificando procesos: {e}")

def test_daemon_manual():
    """Test manual del daemon ejecutando bot_sender.py"""
    log_mensaje("\n🧪 === TEST MANUAL DAEMON ===")
    
    try:
        import subprocess
        
        log_mensaje("   🚀 Ejecutando bot_sender.py manualmente...")
        
        resultado = subprocess.run(
            [sys.executable, 'src/bots/senders/bot_sender.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        log_mensaje(f"   📊 Código de salida: {resultado.returncode}")
        
        if resultado.stdout:
            log_mensaje("   📤 Output:")
            for line in resultado.stdout.split('\n'):
                if line.strip():
                    log_mensaje(f"      {line}")
        
        if resultado.stderr and resultado.stderr.strip():
            log_mensaje("   ⚠️ Errores:")
            for line in resultado.stderr.split('\n'):
                if line.strip():
                    log_mensaje(f"      {line}")
        
        if resultado.returncode == 0:
            log_mensaje("   ✅ Ejecución manual exitosa")
            
            # Verificar si se procesaron notificaciones
            if '✅' in resultado.stdout and 'enviado' in resultado.stdout:
                log_mensaje("   🎉 Se enviaron notificaciones")
            elif 'No hay notificaciones pendientes' in resultado.stdout:
                log_mensaje("   📭 No había notificaciones pendientes")
            
            return True
        else:
            log_mensaje("   ❌ Error en ejecución manual")
            return False
            
    except subprocess.TimeoutExpired:
        log_mensaje("   ⏰ Timeout ejecutando bot_sender")
        return False
    except Exception as e:
        log_mensaje(f"   ❌ Error en test manual: {e}")
        return False

def main():
    """Función principal"""
    log_mensaje("🤖 === VERIFICACIÓN DAEMON RAILWAY ===")
    log_mensaje("Este script verifica que el daemon esté funcionando correctamente\n")
    
    # 1. Verificar configuración
    whatsapp_ok, interval = verificar_configuracion_daemon()
    
    # 2. Verificar procesos (si psutil está disponible)
    verificar_proceso_daemon()
    
    # 3. Test manual del daemon
    log_mensaje("\n🧪 Ejecutando test manual del daemon...")
    test_manual_ok = test_daemon_manual()
    
    # 4. Simular notificaciones si el test manual funcionó
    if test_manual_ok and whatsapp_ok:
        log_mensaje("\n📝 Simulando notificaciones para probar el daemon...")
        if simular_carga_notificaciones():
            log_mensaje("\n👀 Monitoreando por 5 minutos para ver si el daemon las procesa...")
            monitorear_notificaciones(5)
    
    # Resumen final
    log_mensaje("\n📋 === RESUMEN VERIFICACIÓN DAEMON ===")
    
    if whatsapp_ok:
        log_mensaje("✅ WhatsApp configurado - daemon debería estar activo")
    else:
        log_mensaje("❌ WhatsApp NO configurado - daemon no funcionará")
    
    if test_manual_ok:
        log_mensaje("✅ Test manual del daemon exitoso")
    else:
        log_mensaje("❌ Test manual del daemon falló")
    
    log_mensaje(f"⏰ Intervalo configurado: {interval//60} minutos")
    
    log_mensaje("\n🔧 === ACCIONES RECOMENDADAS ===")
    
    if not whatsapp_ok:
        log_mensaje("1. Configurar variables de WhatsApp en Railway")
        log_mensaje("2. Reiniciar el servicio después de configurar")
    
    if not test_manual_ok:
        log_mensaje("1. Revisar logs de Railway para errores")
        log_mensaje("2. Verificar que los archivos src/bots/senders/bot_sender.py existan")
        log_mensaje("3. Comprobar dependencias instaladas")
    
    log_mensaje("4. En Railway Dashboard, verificar:")
    log_mensaje("   - Variables de entorno configuradas")
    log_mensaje("   - Logs del servicio")
    log_mensaje("   - Estado del deployment")
    
    log_mensaje("\n💡 Si el daemon funciona manualmente pero no automáticamente,")
    log_mensaje("   el problema está en main.py o en el hilo del daemon")

if __name__ == '__main__':
    main()
