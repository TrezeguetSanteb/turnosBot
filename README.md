# Sistema de Notificaciones - Bot Multi-Canal

Sistema universal para enviar notificaciones automáticas por **Telegram** y **WhatsApp** cuando se cancelan turnos.

## ✨ Características

- 🔄 **Multi-canal**: Telegram y WhatsApp automáticamente
- ⚙️ **Configuración simple**: Solo edita `.env`
- 🤖 **Envío automático**: Al cancelar desde panel admin
- 📱 **Detección inteligente**: Detecta automáticamente qué canal usar
- 🚀 **Escalable**: Agrega nuevos canales fácilmente

## Configuración Rápida

### Telegram
1. **Cambiar token**: Edita `BOT_TOKEN` en `.env`

### WhatsApp (Opcional)
2. **Configurar Meta API**: Edita variables `WHATSAPP_*` en `.env`
3. **Ver guía completa**: `WHATSAPP_SETUP.md`

### Iniciar Sistema
3. **Iniciar daemon**: `./control_notificaciones.sh start`
4. **Verificar estado**: `./control_notificaciones.sh status`

## Archivos Principales

- **`.env`** - Configuración central (Telegram + WhatsApp)
- **`bot_config.py`** - Manejo centralizado de configuración
- **`bot_telegram.py`** - Bot de Telegram interactivo
- **`bot_whatsapp.py`** - Bot de WhatsApp interactivo
- **`bot_sender.py`** - Envío universal automático (Telegram + WhatsApp)
- **`whatsapp_sender.py`** - Módulo específico de WhatsApp
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
python bot_telegram.py    # Iniciar bot de Telegram
python bot_whatsapp.py    # Iniciar bot de WhatsApp

# Envío manual
python bot_sender.py      # Enviar notificaciones pendientes (todos los canales)

# Panel web admin
python admin_panel.py     # Panel web para gestionar turnos
```

## Detección Automática de Canales

El sistema detecta automáticamente qué canal usar según el número:

- **Telegram**: Números que son solo dígitos (ej: `123456789`)
- **WhatsApp**: Números con formato internacional (ej: `+541234567890`)

## Configuración Multi-Bot

Para correr múltiples instancias:

1. **Copia la carpeta** del proyecto
2. **Cambia solo el `.env`** con diferentes tokens
3. **Ejecuta** cada instancia independientemente

## Estructura de .env

```bash
# Telegram Bot
BOT_TOKEN='tu_token_telegram'

# WhatsApp Bot (Meta API) - Opcional
WHATSAPP_ACCESS_TOKEN='tu_token_whatsapp'
WHATSAPP_PHONE_NUMBER_ID='tu_phone_number_id'
WHATSAPP_BUSINESS_ACCOUNT_ID='tu_business_account_id'

# Sistema
NOTIFICATION_INTERVAL=60
LOG_LEVEL=INFO
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
