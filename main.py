#!/usr/bin/env python3
"""
Proceso principal para Railway - Ejecuta todos los servicios
VERSIÓN NUEVA ESTRUCTURA: Usa imports desde src/
"""
import os
import sys
import threading
import time
import subprocess
import signal
from flask import Flask

# Agregar src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def log(message):
    print(f"[MAIN] {message}", flush=True)


def verificar_variables_entorno():
    """Verificar que todas las variables de entorno requeridas estén configuradas"""
    log("🔍 Verificando variables de entorno...")

    # Variables críticas para WhatsApp
    variables_criticas = {
        'WHATSAPP_ACCESS_TOKEN': 'Token de acceso de WhatsApp Business API',
        'WHATSAPP_PHONE_NUMBER_ID': 'ID del número de teléfono de WhatsApp',
        'WHATSAPP_VERIFY_TOKEN': 'Token de verificación del webhook',
        'ADMIN_PHONE_NUMBER': 'Número de teléfono del administrador'
    }

    # Variables opcionales con valores por defecto
    variables_opcionales = {
        'WHATSAPP_BUSINESS_ACCOUNT_ID': 'ID de la cuenta de WhatsApp Business',
        'NOTIFICATION_INTERVAL': 'Intervalo de notificaciones (default: 60)',
        'LOG_LEVEL': 'Nivel de logging (default: INFO)',
        'PORT': 'Puerto del servidor (default: 9000)'
    }

    errores = []
    advertencias = []

    # Verificar variables críticas
    for var, descripcion in variables_criticas.items():
        valor = os.environ.get(var)
        if not valor:
            errores.append(f"❌ {var}: {descripcion}")
        else:
            # Ocultar parte del token por seguridad
            if 'TOKEN' in var:
                valor_mostrar = valor[:10] + "..." + \
                    valor[-5:] if len(valor) > 15 else valor[:5] + "..."
            elif 'PHONE' in var:
                valor_mostrar = valor[:5] + "..." + \
                    valor[-4:] if len(valor) > 9 else valor
            else:
                valor_mostrar = valor[:10] + \
                    "..." if len(valor) > 10 else valor
            log(f"✅ {var}: {valor_mostrar}")

    # Verificar variables opcionales
    for var, descripcion in variables_opcionales.items():
        valor = os.environ.get(var)
        if not valor:
            advertencias.append(f"⚠️  {var}: {descripcion}")
        else:
            log(f"✅ {var}: {valor}")

    # Mostrar resultados
    if errores:
        log("❌ VARIABLES CRÍTICAS FALTANTES:")
        for error in errores:
            log(f"   {error}")
        log("")
        log("🔧 Para configurar en Railway:")
        log("   1. Ve a Railway Dashboard > Tu Proyecto > Variables")
        log("   2. Click 'Add Variable' para cada una")
        log("   3. Redeploy automático después de agregar variables")
        log("")

    if advertencias:
        log("⚠️  Variables opcionales no configuradas:")
        for adv in advertencias:
            log(f"   {adv}")
        log("")

    # Verificar configuración específica de Railway
    railway_url = os.environ.get('RAILWAY_STATIC_URL')
    if railway_url:
        log(f"🚂 Railway URL: {railway_url}")
    else:
        log("ℹ️  RAILWAY_STATIC_URL no disponible (normal en desarrollo local)")

    return len(errores) == 0


def run_daemon():
    """Ejecutar daemon de notificaciones en thread separado"""
    import asyncio

    def daemon_wrapper():
        try:
            log("Iniciando daemon de notificaciones...")
            # Importar desde nueva estructura
            from services.daemon import main as daemon_main
            # Pasar in_thread=True para evitar problemas con signals
            asyncio.run(daemon_main(in_thread=True))
        except Exception as e:
            log(f"Error en daemon: {e}")
            time.sleep(5)  # Esperar antes de reintentar
            daemon_wrapper()  # Reintentar

    daemon_wrapper()


def run_whatsapp_bot():
    """Ejecutar bot de WhatsApp en thread separado"""
    try:
        log("Iniciando bot de WhatsApp...")
        from bots.whatsapp_bot import app as whatsapp_app

        # Obtener puerto para WhatsApp (puerto principal + 1)
        main_port = int(os.environ.get('PORT', 9000))
        whatsapp_port = main_port + 1

        whatsapp_app.run(
            host='0.0.0.0',
            port=whatsapp_port,
            debug=False,
            use_reloader=False  # Importante en threading
        )
    except Exception as e:
        log(f"Error en bot WhatsApp: {e}")


def run_admin_panel():
    """Ejecutar panel de administración"""
    try:
        log("Iniciando panel de administración...")
        from admin.panel import app as admin_app

        port = int(os.environ.get('PORT', 9000))
        admin_app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False
        )
    except Exception as e:
        log(f"Error en panel admin: {e}")


def main():
    log("🚀 Iniciando TurnosBot en Railway... (NUEVA ESTRUCTURA)")

    # Verificar variables de entorno
    if not verificar_variables_entorno():
        log("⚠️ Continuando con configuración incompleta...")
        log("⚠️ Algunas funcionalidades pueden no estar disponibles")

    log("")  # Línea en blanco para separar

    # Inicializar base de datos
    log("📦 Inicializando base de datos...")
    try:
        import sqlite3
        schema_path = 'data/schema.sql' if os.path.exists(
            'data/schema.sql') else 'schema.sql'
        db_path = 'data/turnos.db' if os.path.exists('data/') else 'turnos.db'

        if not os.path.exists(db_path):
            with open(schema_path, 'r') as f:
                schema = f.read()
            conn = sqlite3.connect(db_path)
            conn.executescript(schema)
            conn.close()
            log("✅ Base de datos creada")
        else:
            log("✅ Base de datos existente")
    except Exception as e:
        log(f"❌ Error con base de datos: {e}")

    # Iniciar servicios en threads
    threads = []

    # 1. Daemon de notificaciones
    daemon_thread = threading.Thread(target=run_daemon, daemon=True)
    daemon_thread.start()
    threads.append(daemon_thread)
    log("✅ Daemon iniciado")

    # 2. Bot de WhatsApp (si está configurado)
    if os.environ.get('WHATSAPP_ACCESS_TOKEN'):
        whatsapp_thread = threading.Thread(
            target=run_whatsapp_bot, daemon=True)
        whatsapp_thread.start()
        threads.append(whatsapp_thread)
        log("✅ Bot WhatsApp iniciado")
    else:
        log("⚠️ WhatsApp no configurado")

    # 3. Panel de administración (proceso principal)
    log("✅ Todos los servicios iniciados")
    log(f"🌐 Panel disponible en puerto {os.environ.get('PORT', 9000)}")

    # El panel admin corre en el thread principal
    run_admin_panel()


if __name__ == '__main__':
    main()
