# Sistema de Notificaciones - Bot de Turnos

Sistema simple para enviar notificaciones automáticas cuando se cancelan turnos.

## Configuración Rápida

1. **Cambiar token del bot**: Edita `.env` y cambia `BOT_TOKEN`
2. **Iniciar daemon**: `./control_notificaciones.sh start`
3. **Verificar estado**: `./control_notificaciones.sh status`

## Archivos Principales

- **`.env`** - Configuración (solo cambiar BOT_TOKEN)
- **`bot_config.py`** - Manejo centralizado del token
- **`bot_telegram.py`** - Bot de Telegram interactivo
- **`bot_sender.py`** - Envío automático de notificaciones
- **`daemon_notificaciones.py`** - Daemon que ejecuta bot_sender.py cada 60 segundos
- **`control_notificaciones.sh`** - Script de control del daemon

## Comandos

```bash
# Control del daemon
./control_notificaciones.sh start    # Iniciar daemon automático
./control_notificaciones.sh stop     # Detener daemon
./control_notificaciones.sh status   # Ver estado
./control_notificaciones.sh logs     # Ver logs en tiempo real
./control_notificaciones.sh test     # Ejecutar envío una vez

# Bot interactivo
python bot_telegram.py               # Iniciar bot para respuestas
```

## Para usar múltiples bots

1. Copia todo el proyecto a otra carpeta
2. Cambia `BOT_TOKEN` en el `.env` de la nueva carpeta
3. Ejecuta el daemon en la nueva carpeta

Cada instancia es completamente independiente.

## Funcionamiento

1. Cuando se cancela un turno desde el panel admin, se crea una notificación
2. El daemon ejecuta `bot_sender.py` cada 60 segundos automáticamente
3. `bot_sender.py` envía las notificaciones y las elimina del log
4. Los usuarios también reciben notificaciones al contactar el bot

¡Listo! Solo cambias el token y tienes un nuevo bot funcionando.
