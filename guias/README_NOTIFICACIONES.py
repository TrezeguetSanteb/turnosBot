#!/usr/bin/env python3
"""
GUÍA COMPLETA DEL SISTEMA DE NOTIFICACIONES AUTOMÁTICAS
========================================================

Este sistema permite enviar notificaciones automáticas cuando se cancelan turnos
o se bloquean días desde el panel administrativo.

ARCHIVOS PRINCIPALES:
---------------------

1. notifications.py - Módulo principal de notificaciones
2. bot_telegram.py - Bot de Telegram (ejecutar con: python bot_telegram.py)
3. telegram_sender.py - Script para envío directo por Telegram
4. daemon_notificaciones.py - Daemon que ejecuta telegram_sender.py automáticamente
5. control_notificaciones.sh - Script de control del daemon
6. crear_notificacion_telegram.py - Crear notificaciones de prueba

FUNCIONAMIENTO DEL SISTEMA:
---------------------------

1. Cuando se cancela un turno o se bloquea un día desde el panel admin,
   se crea automáticamente una notificación en notifications_log.json

2. Las notificaciones se envían de tres formas:
   a) Automáticamente cuando el usuario contacta cualquier bot (verificación en bot_core.py)
   b) Daemon automático que ejecuta telegram_sender.py cada 60 segundos
   c) Manualmente ejecutando los scripts de envío

3. Después de enviar notificaciones por Telegram, se eliminan automáticamente
   del log para evitar duplicados.

COMANDOS PRINCIPALES:
--------------------

# Control del daemon (RECOMENDADO PARA PRODUCCIÓN)
./control_notificaciones.sh start    # Iniciar daemon automático
./control_notificaciones.sh stop     # Detener daemon
./control_notificaciones.sh status   # Ver estado del daemon
./control_notificaciones.sh logs     # Ver logs en tiempo real
./control_notificaciones.sh test     # Ejecutar envío una vez

# Comandos manuales
python telegram_sender.py            # Enviar notificaciones pendientes una vez
python bot_telegram.py               # Iniciar bot de Telegram
python crear_notificacion_telegram.py # Crear notificación de prueba

CONFIGURACIÓN PARA PRODUCCIÓN:
------------------------------

1. Iniciar el daemon de notificaciones automáticas:
   ./control_notificaciones.sh start

2. Mantener el bot de Telegram corriendo (opcional, para respuestas interactivas):
   python bot_telegram.py &

3. Verificar que todo funciona:
   ./control_notificaciones.sh status

El daemon se encarga automáticamente de:
- Enviar notificaciones por Telegram cada 60 segundos
- Limpiar notificaciones ya enviadas
- Registrar logs de actividad
- Reintentar en caso de errores

VENTAJAS DEL NUEVO SISTEMA:
--------------------------

✅ Envío automático independiente del bot
✅ Limpieza automática de notificaciones enviadas
✅ No duplica notificaciones
✅ Funciona sin importar en qué plataforma se creó el turno
✅ Logs detallados para debugging
✅ Control fácil con scripts
✅ Reinicio automático en caso de errores

RESOLUCIÓN DE PROBLEMAS:
------------------------

❌ "Chat not found" en Telegram:
   - El usuario debe haber iniciado una conversación con el bot primero
   - Verifica que el ID de Telegram sea correcto (solo números)

❌ El daemon no está funcionando:
   - ./control_notificaciones.sh status
   - ./control_notificaciones.sh logs
   - Verificar que telegram_sender.py funciona: ./control_notificaciones.sh test

❌ Notificaciones no se envían:
   - Verificar notificaciones pendientes: python -c "from notifications import obtener_notificaciones_pendientes; print(len(obtener_notificaciones_pendientes()))"
   - Ejecutar manualmente: python telegram_sender.py

❌ Notificaciones duplicadas:
   - El sistema limpia automáticamente las enviadas
   - Si persiste, revisar notifications_log.json

ARCHIVOS DE LOG Y CONFIGURACIÓN:
--------------------------------

- notifications_log.json - Notificaciones pendientes y enviadas
- daemon_notificaciones.log - Log del daemon automático  
- daemon_notificaciones.pid - PID del daemon en ejecución

INTEGRACIÓN CON OTROS CANALES:
------------------------------

- WhatsApp: Las notificaciones se muestran cuando el usuario contacta el bot
- Otros canales: Modifica telegram_sender.py para agregar más métodos de envío

CONFIGURACIÓN AVANZADA:
-----------------------

Para cambiar el intervalo del daemon, edita daemon_notificaciones.py:
INTERVALO_SEGUNDOS = 60  # Cambiar a los segundos deseados

Para configurar múltiples tokens de Telegram o otros canales,
modifica telegram_sender.py según tus necesidades.

¡El sistema está completamente funcional y listo para producción! 🚀
"""

if __name__ == '__main__':
    print(__doc__)
