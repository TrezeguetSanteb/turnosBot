#!/usr/bin/env python3
"""
VERIFICAR DAEMON RAILWAY - Diagnóstico específico
Verifica si el daemon realmente se está ejecutando en Railway
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta

def log(message):
    """Log con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)

def verificar_entorno_railway():
    """Verificar si estamos en Railway y configuración"""
    log("🚂 === VERIFICAR ENTORNO RAILWAY ===")
    
    # Variables de Railway
    railway_vars = {
        'RAILWAY_STATIC_URL': os.environ.get('RAILWAY_STATIC_URL'),
        'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT'),
        'RAILWAY_SERVICE_NAME': os.environ.get('RAILWAY_SERVICE_NAME'),
        'PORT': os.environ.get('PORT'),
    }
    
    es_railway = any(railway_vars.values())
    log(f"   Entorno: {'🚂 Railway' if es_railway else '💻 Local'}")
    
    if es_railway:
        for var, value in railway_vars.items():
            if value:
                log(f"   {var}: {value}")
    
    # Variables WhatsApp
    whatsapp_vars = [
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_PHONE_NUMBER_ID',
        'WHATSAPP_VERIFY_TOKEN',
        'ADMIN_PHONE_NUMBER'
    ]
    
    whatsapp_configurado = all(os.environ.get(var) for var in whatsapp_vars)
    log(f"   WhatsApp: {'✅ Configurado' if whatsapp_configurado else '❌ NO configurado'}")
    
    # Interval daemon
    interval = int(os.environ.get('NOTIFICATION_INTERVAL', '300'))
    log(f"   Daemon interval: {interval}s ({interval//60} min)")
    
    return es_railway, whatsapp_configurado

def verificar_main_py():
    """Verificar que main.py inicie el daemon correctamente"""
    log("\n🔍 === VERIFICAR MAIN.PY ===")
    
    if not os.path.exists('main.py'):
        log("   ❌ main.py no existe")
        return False
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar que tenga las funciones críticas
        checks = {
            'run_daemon': 'run_daemon' in content,
            'daemon_thread': 'daemon_thread' in content,
            'services.daemon': 'services.daemon' in content,
            'has_whatsapp': 'has_whatsapp' in content,
            'threading.Thread': 'threading.Thread' in content
        }
        
        log("   Verificando componentes de main.py:")
        for check, exists in checks.items():
            status = "✅" if exists else "❌"
            log(f"      {status} {check}")
        
        return all(checks.values())
        
    except Exception as e:
        log(f"   ❌ Error leyendo main.py: {e}")
        return False

def simular_inicio_daemon():
    """Simular el inicio del daemon como lo hace main.py"""
    log("\n🚀 === SIMULAR INICIO DAEMON ===")
    
    try:
        # Verificar si las variables de WhatsApp están configuradas
        whatsapp_vars = [
            'WHATSAPP_ACCESS_TOKEN',
            'WHATSAPP_PHONE_NUMBER_ID',
            'WHATSAPP_VERIFY_TOKEN',
            'ADMIN_PHONE_NUMBER'
        ]
        
        has_whatsapp = all(os.environ.get(var) for var in whatsapp_vars)
        log(f"   has_whatsapp: {has_whatsapp}")
        
        if not has_whatsapp:
            log("   ❌ PROBLEMA: WhatsApp no configurado - daemon NO se iniciará")
            log("   💡 Solución: Configurar variables de WhatsApp en Railway")
            return False
        
        log("   ✅ WhatsApp configurado - daemon DEBERÍA iniciarse")
        
        # Intentar importar y ejecutar el daemon
        log("   🔄 Intentando importar services.daemon...")
        
        # Agregar src al path como lo hace main.py
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        try:
            from services.daemon import main as daemon_main
            log("   ✅ Import services.daemon exitoso")
            
            # Intentar ejecutar daemon en modo test
            log("   🚀 Ejecutando daemon en modo test...")
            
            import asyncio
            
            # Crear un timeout para no bloquear
            async def test_daemon():
                try:
                    await asyncio.wait_for(daemon_main(in_thread=True), timeout=10.0)
                except asyncio.TimeoutError:
                    log("   ⏰ Daemon ejecutándose (timeout después de 10s)")
                    return True
                except Exception as e:
                    log(f"   ❌ Error en daemon: {e}")
                    return False
            
            result = asyncio.run(test_daemon())
            return result
            
        except ImportError as e:
            log(f"   ❌ Error importando daemon: {e}")
            return False
        except Exception as e:
            log(f"   ❌ Error ejecutando daemon: {e}")
            return False
        
    except Exception as e:
        log(f"   ❌ Error en simulación: {e}")
        return False

def verificar_archivos_daemon():
    """Verificar que todos los archivos del daemon existan"""
    log("\n📁 === VERIFICAR ARCHIVOS DAEMON ===")
    
    archivos_necesarios = [
        'src/services/daemon.py',
        'src/bots/senders/bot_sender.py',
        'src/services/notifications.py',
        'src/core/config.py'
    ]
    
    todos_ok = True
    for archivo in archivos_necesarios:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            log(f"   ✅ {archivo} ({size} bytes)")
        else:
            log(f"   ❌ {archivo} NO EXISTE")
            todos_ok = False
    
    return todos_ok

def crear_test_persistente():
    """Crear archivo de test para verificar si el daemon está corriendo"""
    log("\n📝 === CREAR TEST PERSISTENTE ===")
    
    try:
        test_file = 'daemon_test.json'
        test_data = {
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'checks': [],
            'daemon_running': False
        }
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        
        log(f"   ✅ Archivo de test creado: {test_file}")
        log("   💡 Si el daemon está corriendo, debería actualizar este archivo")
        
        return True
        
    except Exception as e:
        log(f"   ❌ Error creando test: {e}")
        return False

def monitorear_actividad_daemon():
    """Monitorear si hay actividad del daemon"""
    log("\n👀 === MONITOREAR ACTIVIDAD DAEMON (2 min) ===")
    
    notifications_file = 'data/notifications_log.json'
    
    if not os.path.exists(notifications_file):
        log("   ❌ Archivo de notificaciones no existe")
        return
    
    try:
        # Estado inicial
        with open(notifications_file, 'r', encoding='utf-8') as f:
            initial_notifications = json.load(f)
        
        initial_pending = len([n for n in initial_notifications if not n.get('enviado', False)])
        initial_sent = len([n for n in initial_notifications if n.get('enviado', False)])
        
        log(f"   📊 Estado inicial: {initial_pending} pendientes, {initial_sent} enviadas")
        
        # Crear notificación de prueba
        test_notification = {
            "id": f"daemon_test_{int(datetime.now().timestamp())}",
            "turno_id": 7777,
            "telefono": "+5491123456777",
            "mensaje": "🧪 TEST DAEMON: Verificando si el daemon procesa esta notificación",
            "tipo": "cancelacion_turno",
            "fecha_creacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "enviado": False,
            "test": True
        }
        
        initial_notifications.append(test_notification)
        
        with open(notifications_file, 'w', encoding='utf-8') as f:
            json.dump(initial_notifications, f, indent=2, ensure_ascii=False)
        
        log(f"   ✅ Notificación de test creada: {test_notification['id']}")
        
        # Monitorear por 2 minutos
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=2)
        
        log(f"   ⏰ Monitoreando hasta {end_time.strftime('%H:%M:%S')}...")
        
        while datetime.now() < end_time:
            time.sleep(15)  # Check cada 15 segundos
            
            try:
                with open(notifications_file, 'r', encoding='utf-8') as f:
                    current_notifications = json.load(f)
                
                current_pending = len([n for n in current_notifications if not n.get('enviado', False)])
                current_sent = len([n for n in current_notifications if n.get('enviado', False)])
                
                # Verificar si nuestra notificación de test fue procesada
                test_processed = False
                for notif in current_notifications:
                    if (notif.get('id') == test_notification['id'] and 
                        notif.get('enviado', False)):
                        test_processed = True
                        break
                
                if test_processed:
                    log("   🎉 ¡DAEMON ACTIVO! La notificación de test fue procesada")
                    return True
                elif current_sent > initial_sent:
                    log(f"   🔄 Actividad detectada: {current_sent - initial_sent} nuevas enviadas")
                else:
                    remaining = int((end_time - datetime.now()).total_seconds())
                    log(f"   ⏳ Sin actividad del daemon. Quedan {remaining}s...")
                    
            except Exception as e:
                log(f"   ⚠️ Error monitoreando: {e}")
        
        log("   ❌ DAEMON INACTIVO: No se detectó actividad en 2 minutos")
        return False
        
    except Exception as e:
        log(f"   ❌ Error en monitoreo: {e}")
        return False

def diagnostico_railway_daemon():
    """Diagnóstico final específico para Railway"""
    log("\n🔧 === DIAGNÓSTICO RAILWAY DAEMON ===")
    
    # Verificar si estamos en Railway
    railway_vars = ['RAILWAY_STATIC_URL', 'RAILWAY_ENVIRONMENT']
    es_railway = any(os.environ.get(var) for var in railway_vars)
    
    if not es_railway:
        log("⚠️ No estamos en Railway - ejecutar este script EN Railway")
        return
    
    log("🚂 Ejecutándose en Railway")
    
    # Verificar variables de WhatsApp
    whatsapp_vars = [
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_PHONE_NUMBER_ID',
        'WHATSAPP_VERIFY_TOKEN',
        'ADMIN_PHONE_NUMBER'
    ]
    
    whatsapp_ok = all(os.environ.get(var) for var in whatsapp_vars)
    
    if not whatsapp_ok:
        log("❌ PROBLEMA PRINCIPAL: Variables de WhatsApp faltantes")
        log("🔧 SOLUCIÓN:")
        log("   1. Ir a Railway Dashboard → tu servicio → Variables")
        log("   2. Agregar todas las variables de WhatsApp")
        log("   3. Redeploy o reiniciar el servicio")
        return
    
    log("✅ Variables de WhatsApp configuradas")
    
    # Verificar que main.py tenga la lógica correcta
    if not verificar_main_py():
        log("❌ PROBLEMA: main.py no tiene la lógica correcta del daemon")
        return
    
    log("✅ main.py tiene la lógica del daemon")
    
    # El problema puede ser:
    log("\n🔍 POSIBLES PROBLEMAS EN RAILWAY:")
    log("1. ❌ El proceso principal (main.py) no se está ejecutando")
    log("2. ❌ El hilo del daemon se está muriendo silenciosamente")
    log("3. ❌ Hay errores de importación que impiden el daemon")
    log("4. ❌ Railway está reiniciando el servicio constantemente")
    log("5. ❌ Problemas de permisos o recursos")
    
    log("\n🔧 SOLUCIONES RAILWAY:")
    log("1. Revisar logs de Railway Dashboard para errores")
    log("2. Verificar que el deployment sea exitoso")
    log("3. Comprobar métricas de CPU/memoria")
    log("4. Verificar que no haya restarts constantes")
    log("5. Probar redeploy desde la rama mejoras")

def main():
    """Función principal"""
    log("🤖 === VERIFICAR DAEMON RAILWAY ===")
    log("Diagnóstico específico para verificar si el daemon se ejecuta\n")
    
    # 1. Verificar entorno
    es_railway, whatsapp_ok = verificar_entorno_railway()
    
    # 2. Verificar archivos
    archivos_ok = verificar_archivos_daemon()
    
    # 3. Verificar main.py
    main_ok = verificar_main_py()
    
    # 4. Simular inicio del daemon
    daemon_ok = False
    if whatsapp_ok and archivos_ok and main_ok:
        daemon_ok = simular_inicio_daemon()
    
    # 5. Crear test persistente
    crear_test_persistente()
    
    # 6. Monitorear actividad
    daemon_activo = False
    if daemon_ok:
        daemon_activo = monitorear_actividad_daemon()
    
    # Resumen final
    log(f"\n📊 === RESUMEN VERIFICACIÓN ===")
    log(f"🚂 Railway: {'✅' if es_railway else '❌'}")
    log(f"📱 WhatsApp: {'✅' if whatsapp_ok else '❌'}")
    log(f"📁 Archivos: {'✅' if archivos_ok else '❌'}")
    log(f"📄 main.py: {'✅' if main_ok else '❌'}")
    log(f"🚀 Inicio daemon: {'✅' if daemon_ok else '❌'}")
    log(f"🔄 Daemon activo: {'✅' if daemon_activo else '❌'}")
    
    if daemon_activo:
        log("\n🎉 ¡DAEMON FUNCIONANDO! El problema debe estar en otra parte")
    elif not whatsapp_ok:
        log("\n❌ DAEMON NO FUNCIONA: Variables WhatsApp faltantes")
    elif not daemon_ok:
        log("\n❌ DAEMON NO FUNCIONA: Error en inicio o configuración")
    else:
        log("\n❌ DAEMON NO ACTIVO: Se inicia pero no procesa notificaciones")
    
    # Diagnóstico específico para Railway
    if es_railway:
        diagnostico_railway_daemon()

if __name__ == '__main__':
    main()
