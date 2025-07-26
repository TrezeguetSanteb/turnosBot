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
from datetime import datetime
import signal
from bot_config import config

# Configuración desde bot_config
INTERVALO_SEGUNDOS = config.NOTIFICATION_INTERVAL
SCRIPT_SENDER = 'bot_sender.py'  # Script genérico
EJECUTAR_AL_INICIO = True

# Variables globales para el control del daemon
ejecutando = True
stats = {
    'ejecuciones': 0,
    'errores': 0,
    'ultimo_envio': None,
    'notificaciones_enviadas': 0
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
        log_mensaje(f"🚀 Ejecutando bot_sender.py...")

        # Ejecutar el script
        resultado = subprocess.run(
            [sys.executable, SCRIPT_SENDER],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        stats['ejecuciones'] += 1

        if resultado.returncode == 0:
            # Analizar output para contar notificaciones enviadas
            output_lines = resultado.stdout.split('\n')
            for line in output_lines:
                if '✅ Notificación enviada exitosamente' in line:
                    stats['notificaciones_enviadas'] += 1

            stats['ultimo_envio'] = datetime.now()
            log_mensaje("✅ bot_sender.py ejecutado exitosamente")

            # Mostrar output si hay notificaciones
            if '📨 Enviando' in resultado.stdout:
                log_mensaje("📋 Output del envío:")
                for line in output_lines:
                    if any(emoji in line for emoji in ['📨', '✅', '❌', '📊', '🧹']):
                        print(f"    {line}")
        else:
            stats['errores'] += 1
            log_mensaje(
                f"❌ Error al ejecutar bot_sender.py: {resultado.stderr}")

    except Exception as e:
        stats['errores'] += 1
        log_mensaje(f"❌ Excepción al ejecutar bot_sender.py: {e}")


def mostrar_estadisticas():
    """Muestra estadísticas del daemon"""
    uptime = time.time() - stats.get('inicio', time.time())
    horas = int(uptime // 3600)
    minutos = int((uptime % 3600) // 60)

    log_mensaje("📊 ESTADÍSTICAS DEL DAEMON")
    log_mensaje(f"    Tiempo activo: {horas}h {minutos}m")
    log_mensaje(f"    Ejecuciones: {stats['ejecuciones']}")
    log_mensaje(f"    Errores: {stats['errores']}")
    log_mensaje(
        f"    Notificaciones enviadas: {stats['notificaciones_enviadas']}")
    if stats['ultimo_envio']:
        log_mensaje(
            f"    Último envío: {stats['ultimo_envio'].strftime('%H:%M:%S')}")


async def main():
    """Función principal del daemon"""
    global ejecutando

    # Configurar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

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
