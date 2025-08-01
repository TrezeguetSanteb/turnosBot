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
from src.core.config import config

# Configuración desde bot_config
INTERVALO_SEGUNDOS = config.NOTIFICATION_INTERVAL
# Script genérico en nueva estructura
SCRIPT_SENDER = 'src/bots/senders/bot_sender.py'
EJECUTAR_AL_INICIO = True

# Variables globales para el control del daemon
ejecutando = True
ultimo_mantenimiento = None  # Para controlar el mantenimiento diario
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
            log_mensaje("✅ Script ejecutado exitosamente")

            # Mostrar output si hay notificaciones
            if '📨 Enviando' in resultado.stdout:
                log_mensaje("📋 Output del envío:")
                for line in output_lines:
                    if any(emoji in line for emoji in ['📨', '✅', '❌', '📊', '🧹']):
                        print(f"    {line}")
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

    # Verificar si ha pasado un día
    ahora = datetime.now()
    tiempo_transcurrido = ahora - ultimo_mantenimiento

    # Ejecutar mantenimiento cada 24 horas
    return tiempo_transcurrido.total_seconds() > 86400  # 24 horas


# ...existing code...


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
    log_mensaje(f"Intervalo: {INTERVALO_SEGUNDOS} segundos")
    log_mensaje(f"Script: {SCRIPT_SENDER}")
    log_mensaje("Presiona Ctrl+C para detener")
    log_mensaje("=" * 50)

    # Ejecutar una vez al inicio si está configurado
    if EJECUTAR_AL_INICIO:
        ejecutar_bot_sender()

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
