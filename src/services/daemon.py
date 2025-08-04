#!/usr/bin/env python3
"""
Daemon para envío automático de notificaciones.
Este script ejecuta bot_sender.py cada cierto tiempo automáticamente.
Se adapta automáticamente al tipo de bot configurado en .env
"""

import asyncio
import time
import subprocess
import sys
import os
from datetime import datetime, timedelta
import signal
import requests

# Configurar path para imports - obtener ruta raíz del proyecto (2 niveles arriba desde src/services/)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(project_root, 'src'))

from core.config import config

# Configuración desde bot_config
INTERVALO_SEGUNDOS = config.NOTIFICATION_INTERVAL
# Script genérico en nueva estructura
SCRIPT_SENDER = 'src/bots/senders/bot_sender.py'
EJECUTAR_AL_INICIO = True

# Configuración para keep-alive en Railway
KEEP_ALIVE_INTERVAL = 300  # 5 minutos
RAILWAY_VARS = ['RAILWAY_STATIC_URL', 'RAILWAY_ENVIRONMENT', 'RAILWAY_SERVICE_NAME']
is_railway = any(os.environ.get(var) for var in RAILWAY_VARS)
railway_url = os.environ.get('RAILWAY_STATIC_URL')

# Variables globales para el control del daemon
ejecutando = True
ultimo_mantenimiento = None  # Para controlar el mantenimiento diario
ultimo_keep_alive = None  # Para controlar el keep-alive
stats = {
    'ejecuciones': 0,
    'errores': 0,
    'ultimo_envio': None,
    'notificaciones_enviadas': 0,
    'ultimo_mantenimiento': None
}


def signal_handler(signum, frame):
    """Maneja la señal de interrupción"""
    global ejecutando
    print(f"\n🛑 Recibida señal {signum}. Deteniendo daemon...")
    ejecutando = False


def log_mensaje(mensaje):
    """Registra un mensaje con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {mensaje}")


def ejecutar_bot_sender():
    """Ejecuta el script bot_sender.py"""
    try:
        log_mensaje(f"🚀 Ejecutando {SCRIPT_SENDER}...")

        # Obtener ruta raíz del proyecto (2 niveles arriba desde src/services/)
        project_root = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..'))

        # Ejecutar el script desde la raíz del proyecto
        resultado = subprocess.run(
            [sys.executable, SCRIPT_SENDER],
            capture_output=True,
            text=True,
            cwd=project_root
        )

        stats['ejecuciones'] += 1

        if resultado.returncode == 0:
            # Analizar output para contar notificaciones enviadas
            output_lines = resultado.stdout.split('\n')
            for line in output_lines:
                if '✅ Notificación enviada exitosamente' in line:
                    stats['notificaciones_enviadas'] += 1

            stats['ultimo_envio'] = datetime.now()

            # Mostrar output relevante
            if '📭 No hay notificaciones pendientes' in resultado.stdout:
                log_mensaje("📭 No hay notificaciones pendientes")
            elif '📨 Enviando' in resultado.stdout:
                log_mensaje("📋 Output del envío:")
                for line in output_lines:
                    if any(emoji in line for emoji in ['📨', '✅', '❌', '📊', '🧹']):
                        print(f"    {line}")
            else:
                log_mensaje("✅ Script ejecutado exitosamente")
        else:
            stats['errores'] += 1
            log_mensaje(
                f"❌ Error al ejecutar {SCRIPT_SENDER}: {resultado.stderr}")

    except Exception as e:
        stats['errores'] += 1
        log_mensaje(f"❌ Excepción al ejecutar {SCRIPT_SENDER}: {e}")


def mostrar_estadisticas():
    """Muestra las estadísticas del daemon"""
    log_mensaje("📊 === ESTADÍSTICAS ===")
    log_mensaje(f"   Ejecuciones: {stats['ejecuciones']}")
    log_mensaje(f"   Errores: {stats['errores']}")
    log_mensaje(
        f"   Notificaciones enviadas: {stats['notificaciones_enviadas']}")
    if stats['ultimo_envio']:
        log_mensaje(f"   Último envío: {stats['ultimo_envio']}")
    if stats['ultimo_mantenimiento']:
        log_mensaje(
            f"   Último mantenimiento: {stats['ultimo_mantenimiento']}")
    log_mensaje("==================")


def ejecutar_mantenimiento_db():
    """Ejecuta el mantenimiento de la base de datos"""
    try:
        log_mensaje("🔧 Ejecutando mantenimiento de base de datos...")

        from src.services.maintenance import mantenimiento_completo
        mantenimiento_completo()

        # Actualizar estadísticas
        global ultimo_mantenimiento
        ultimo_mantenimiento = datetime.now()
        stats['ultimo_mantenimiento'] = ultimo_mantenimiento.strftime(
            '%H:%M:%S')

        log_mensaje("✅ Mantenimiento de BD completado")

    except Exception as e:
        log_mensaje(f"❌ Error en mantenimiento de BD: {e}")


def necesita_mantenimiento():
    """Verifica si es necesario ejecutar mantenimiento (una vez por día)"""
    global ultimo_mantenimiento

    if ultimo_mantenimiento is None:
        return True

    # Verificar si ha pasado un día desde el último mantenimiento
    ahora = datetime.now()
    diferencia = ahora - ultimo_mantenimiento
    return diferencia.days >= 1


async def keep_alive_ping():
    """Hace ping al endpoint keep-alive para evitar hibernación en Railway"""
    global ultimo_keep_alive
    
    if not is_railway or not railway_url:
        return  # No hacer ping si no estamos en Railway o no hay URL
    
    ahora = time.time()
    if ultimo_keep_alive and (ahora - ultimo_keep_alive) < KEEP_ALIVE_INTERVAL:
        return  # No hacer ping aún
    
    try:
        # Determinar la URL del keep-alive
        keep_alive_url = f"{railway_url}/api/keep-alive"
        
        log_mensaje(f"🏓 Keep-alive ping a {keep_alive_url}")
        
        # Usar threading para evitar bloquear el loop async
        import threading
        
        def make_request():
            try:
                response = requests.get(keep_alive_url, timeout=10)
                return response.status_code
            except Exception:
                return None
        
        # Ejecutar en un thread separado
        thread = threading.Thread(target=make_request)
        thread.start()
        thread.join(timeout=15)  # Esperar máximo 15 segundos
        
        ultimo_keep_alive = ahora
        log_mensaje("✅ Keep-alive ping enviado")
            
    except Exception as e:
        log_mensaje(f"❌ Error inesperado en keep-alive: {e}")


def necesita_keep_alive():
    """Verifica si es necesario hacer keep-alive ping"""
    global ultimo_keep_alive
    
    if not is_railway or not railway_url:
        return False
    
    if ultimo_keep_alive is None:
        return True
    
    ahora = time.time()
    return (ahora - ultimo_keep_alive) >= KEEP_ALIVE_INTERVAL


async def mantener_conexion_railway():
    """Mantiene la conexión activa con Railway usando keep-alive endpoint"""
    global ultimo_keep_alive
    
    if not railway_url:
        log_mensaje("⚠️ No hay URL de Railway configurada para keep-alive")
        return

    log_mensaje(f"🏓 Iniciando keep-alive para Railway: {railway_url}")

    while ejecutando:
        try:
            await keep_alive_ping()
            # Esperar el intervalo de keep-alive
            await asyncio.sleep(KEEP_ALIVE_INTERVAL)

        except Exception as e:
            log_mensaje(f"❌ Error en keep-alive de Railway: {e}")
            await asyncio.sleep(30)  # Esperar antes de reintentar


async def main(in_thread=False):
    """Función principal del daemon"""
    global ejecutando

    # Solo configurar manejadores de señales si NO estamos en un thread
    if not in_thread:
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            log_mensaje("🔧 Manejadores de señales configurados")
        except ValueError as e:
            log_mensaje(
                f"⚠️ No se pudieron configurar señales (normal en threads): {e}")

    stats['inicio'] = time.time()

    log_mensaje("🤖 DAEMON DE NOTIFICACIONES INICIADO")
    log_mensaje("=" * 50)
    log_mensaje(
        f"Intervalo: {INTERVALO_SEGUNDOS} segundos ({INTERVALO_SEGUNDOS/60:.1f} minutos)")
    log_mensaje(f"Script: {SCRIPT_SENDER}")
    
    # Información sobre Railway
    if is_railway:
        log_mensaje(f"🚂 Entorno: Railway")
        if railway_url:
            log_mensaje(f"🌐 URL: {railway_url}")
            log_mensaje(f"🏓 Keep-alive: Activado (cada {KEEP_ALIVE_INTERVAL/60:.1f} min)")
        else:
            log_mensaje("⚠️ URL de Railway no disponible - keep-alive desactivado")
    else:
        log_mensaje("💻 Entorno: Local")
    
    log_mensaje("Presiona Ctrl+C para detener")
    log_mensaje("=" * 50)

    # Ejecutar una vez al inicio si está configurado
    if EJECUTAR_AL_INICIO:
        ejecutar_bot_sender()

    # Iniciar tarea de mantener conexión con Railway si es necesario
    if is_railway:
        asyncio.create_task(mantener_conexion_railway())

    contador_stats = 0

    while ejecutando:
        try:
            # Esperar el intervalo
            for i in range(INTERVALO_SEGUNDOS):
                if not ejecutando:
                    break
                await asyncio.sleep(1)

            if not ejecutando:
                break

            # Ejecutar bot_sender
            ejecutar_bot_sender()

            # Mostrar estadísticas cada 10 ejecuciones
            contador_stats += 1
            if contador_stats >= 10:
                mostrar_estadisticas()
                contador_stats = 0

            # Ejecutar mantenimiento de la base de datos si es necesario
            if necesita_mantenimiento():
                ejecutar_mantenimiento_db()

            # Hacer ping de keep-alive si es necesario
            if necesita_keep_alive():
                await keep_alive_ping()

        except Exception as e:
            log_mensaje(f"❌ Error en el loop principal: {e}")
            await asyncio.sleep(5)  # Esperar antes de continuar

    log_mensaje("🏁 Daemon detenido")
    mostrar_estadisticas()


if __name__ == '__main__':
    try:
        # Verificar que el script bot_sender existe
        if not os.path.exists(SCRIPT_SENDER):
            print(f"❌ Error: No se encuentra {SCRIPT_SENDER}")
            sys.exit(1)

        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n🛑 Daemon interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado en el daemon: {e}")
        sys.exit(1)
