#!/usr/bin/env python3
"""
TurnosBot - Sistema de Gestión de Turnos
Optimizado para Railway deployment
"""
import os
import sys
import threading
import time
import sqlite3

# Configurar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def log(message):
    """Log con timestamp para Railway"""
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)


def verificar_configuracion():
    """Verificar configuración y variables de entorno"""
    log("🔍 Verificando configuración...")

    # Variables críticas para WhatsApp
    whatsapp_vars = [
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_PHONE_NUMBER_ID',
        'WHATSAPP_VERIFY_TOKEN',
        'ADMIN_PHONE_NUMBER'
    ]

    whatsapp_ok = True
    for var in whatsapp_vars:
        if not os.environ.get(var):
            whatsapp_ok = False
            break
        else:
            # Mostrar parcialmente por seguridad
            value = os.environ.get(var)
            masked = value[:8] + "..." if len(value) > 8 else "***"
            log(f"✅ {var}: {masked}")

    if not whatsapp_ok:
        log("⚠️ Variables de WhatsApp incompletas")
        log("🔧 Configúralas en Railway Dashboard > Variables")

    # Entorno - Railway usa diferentes variables según el plan
    railway_vars = [
        'RAILWAY_STATIC_URL',  # URL pública del servicio
        'RAILWAY_ENVIRONMENT',  # Entorno (production, etc)
        'RAILWAY_SERVICE_NAME',  # Nombre del servicio
        'RAILWAY_PROJECT_NAME',  # Nombre del proyecto
        'RAILWAY_GIT_COMMIT_SHA'  # SHA del commit
    ]

    is_railway = any(os.environ.get(var) for var in railway_vars)
    railway_url = os.environ.get('RAILWAY_STATIC_URL')

    if is_railway:
        if railway_url:
            log(f"🚂 Railway URL: {railway_url}")
        else:
            log("🚂 Ejecutando en Railway (sin URL pública)")

        # Mostrar variables de Railway disponibles
        for var in railway_vars:
            value = os.environ.get(var)
            if value:
                log(f"   {var}: {value}")
    else:
        log("💻 Ejecutando localmente")

    return whatsapp_ok


def run_daemon():
    """Ejecutar daemon de notificaciones"""
    import asyncio

    def daemon_wrapper():
        try:
            log("🤖 Iniciando daemon de notificaciones...")
            from services.daemon import main as daemon_main
            asyncio.run(daemon_main(in_thread=True))
        except ImportError as e:
            log(f"⚠️ No se pudo importar daemon: {e}")
        except Exception as e:
            log(f"❌ Error en daemon: {e}")
            # Esperar antes de que el thread termine
            time.sleep(5)

    daemon_wrapper()


def run_whatsapp_bot():
    """Ejecutar bot de WhatsApp"""
    try:
        log("📱 Iniciando bot de WhatsApp...")
        from bots.whatsapp_bot import app as whatsapp_app

        # Puerto para WhatsApp (puerto principal + 1)
        main_port = int(os.environ.get('PORT', 9000))
        whatsapp_port = main_port + 1

        whatsapp_app.run(
            host='0.0.0.0',
            port=whatsapp_port,
            debug=False,
            use_reloader=False
        )
    except ImportError as e:
        log(f"⚠️ No se pudo importar WhatsApp bot: {e}")
    except Exception as e:
        log(f"❌ Error en WhatsApp bot: {e}")


def run_admin_panel():
    """Ejecutar panel de administración (proceso principal para Railway)"""
    try:
        log("🌐 Iniciando panel de administración...")
        from admin.panel import app as admin_app

        port = int(os.environ.get('PORT', 9000))

        admin_app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False
        )
    except ImportError as e:
        log(f"❌ No se pudo importar panel admin: {e}")
        raise  # Critical error - Railway needs to restart
    except Exception as e:
        log(f"❌ Error en panel admin: {e}")
        raise  # Critical error - Railway needs to restart


def inicializar_base_datos():
    """Inicializar base de datos SQLite"""
    try:
        # Crear directorio data si no existe
        os.makedirs('data', exist_ok=True)

        db_path = 'data/turnos.db'
        schema_path = 'data/schema.sql'

        if not os.path.exists(db_path):
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = f.read()
                conn = sqlite3.connect(db_path)
                conn.executescript(schema)
                conn.close()
                log("✅ Base de datos creada desde schema")
            else:
                log("⚠️ No se encuentra schema.sql, usando base de datos vacía")
        else:
            log("✅ Base de datos existente")

    except Exception as e:
        log(f"❌ Error inicializando BD: {e}")
        raise


def main():
    """Función principal optimizada para Railway"""
    log("🚀 Iniciando TurnosBot...")

    # Verificar configuración
    has_whatsapp = verificar_configuracion()

    # Inicializar base de datos
    log("📦 Inicializando base de datos...")
    inicializar_base_datos()

    # Obtener configuración del entorno
    railway_vars = ['RAILWAY_STATIC_URL', 'RAILWAY_ENVIRONMENT',
                    'RAILWAY_SERVICE_NAME', 'RAILWAY_PROJECT_NAME']
    is_railway = any(os.environ.get(var) for var in railway_vars)
    port = int(os.environ.get('PORT', 9000))

    log(f"🌐 Entorno: {'Railway' if is_railway else 'Local'}")
    log(f"📱 WhatsApp: {'Configurado' if has_whatsapp else 'No configurado'}")

    # Iniciar servicios en background threads
    threads = []

    # 1. Daemon de notificaciones (solo si WhatsApp está configurado)
    if has_whatsapp:
        daemon_thread = threading.Thread(target=run_daemon, daemon=True)
        daemon_thread.start()
        threads.append(daemon_thread)
        log("✅ Daemon de notificaciones iniciado")
    else:
        log("⚠️ Daemon no iniciado (WhatsApp no configurado)")

    # 2. Bot WhatsApp (solo si está configurado)
    if has_whatsapp:
        whatsapp_thread = threading.Thread(
            target=run_whatsapp_bot, daemon=True)
        whatsapp_thread.start()
        threads.append(whatsapp_thread)
        log("✅ Bot de WhatsApp iniciado")
    else:
        log("⚠️ Bot de WhatsApp no iniciado")

    # 3. Panel admin en el proceso principal (Railway requirement)
    log(f"🌐 Panel admin disponible en puerto {port}")
    log("✅ Todos los servicios configurados")

    # Ejecutar panel admin (bloquea hasta terminar)
    run_admin_panel()


if __name__ == '__main__':
    main()
