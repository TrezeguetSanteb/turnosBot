#!/bin/bash
# Script de control para el daemon de notificaciones.
# Uso: ./control_notificaciones.sh [start|stop|status|test]

DAEMON_SCRIPT="daemon_notificaciones.py"
PID_FILE="daemon_notificaciones.pid"
LOG_FILE="daemon_notificaciones.log"

case "$1" in
    start)
        echo "🚀 Iniciando daemon de notificaciones..."
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "❌ El daemon ya está ejecutándose (PID: $PID)"
                exit 1
            else
                echo "🧹 Limpiando PID file obsoleto..."
                rm -f "$PID_FILE"
            fi
        fi
        
        nohup python3 "$DAEMON_SCRIPT" > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "✅ Daemon iniciado con PID: $!"
        echo "📋 Log: tail -f $LOG_FILE"
        ;;
        
    stop)
        echo "🛑 Deteniendo daemon de notificaciones..."
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                kill $PID
                rm -f "$PID_FILE"
                echo "✅ Daemon detenido (PID: $PID)"
            else
                echo "❌ El daemon no está ejecutándose"
                rm -f "$PID_FILE"
            fi
        else
            echo "❌ No se encontró el archivo PID"
        fi
        ;;
        
    status)
        echo "📊 Estado del daemon de notificaciones:"
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "✅ Ejecutándose (PID: $PID)"
                echo "📋 Para ver el log: tail -f $LOG_FILE"
            else
                echo "❌ No está ejecutándose (PID file obsoleto)"
                rm -f "$PID_FILE"
            fi
        else
            echo "❌ No está ejecutándose"
        fi
        ;;
        
    test)
        echo "🧪 Ejecutando prueba de notificaciones..."
        python3 bot_sender.py
        ;;
        
    logs)
        echo "📋 Mostrando logs en tiempo real (Ctrl+C para salir):"
        tail -f "$LOG_FILE"
        ;;
        
    *)
        echo "Uso: $0 {start|stop|status|test|logs}"
        echo ""
        echo "Comandos:"
        echo "  start  - Iniciar el daemon en background"
        echo "  stop   - Detener el daemon"
        echo "  status - Ver estado del daemon"
        echo "  test   - Ejecutar envío de notificaciones una vez"
        echo "  logs   - Ver logs en tiempo real"
        exit 1
        ;;
esac
