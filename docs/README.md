# 🗓️ Sistema de Turnos Multi-Canal

Sistema completo de gestión de turnos con notificaciones automáticas por **Telegram** y **WhatsApp**, panel de administración web y bots conversacionales inteligentes.

## ✨ Características Principales

### 🤖 Bots Conversacionales
- **Telegram Bot**: Interfaz completa para agendar, consultar y cancelar turnos
- **WhatsApp Bot**: Mismo funcionamiento usando Meta Business API
- **Conversación inteligente**: Guía paso a paso para usuarios
- **Formato mejorado**: Listas numeradas y mensajes optimizados para móvil

### 📱 Panel de Administración
- **Interfaz web responsive**: Gestión completa desde cualquier dispositivo
- **Vista semanal**: Navegación fácil entre semanas
- **Gestión de turnos**: Cancelar, bloquear días, configurar horarios
- **PWA Ready**: Instalable como app móvil
- **Versión móvil optimizada**: `admin_panel_mobile.html`

### 🔔 Sistema de Notificaciones
- **Multi-canal automático**: Telegram y WhatsApp según el formato del número
- **Notificaciones al usuario**: Confirmaciones, cancelaciones, días bloqueados
- **Notificaciones al admin**: Cuando se agenda/cancela un turno
- **Daemon automático**: Envío cada 60 segundos sin intervención
- **Formato inteligente**: Convierte automáticamente números argentinos (549 ↔ 54)

### ⚙️ Configuración Centralizada
- **Archivo `.env`**: Toda la configuración en un solo lugar
- **Multi-instancia**: Fácil replicación para múltiples clientes
- **Detección automática**: Habilita funciones según tokens disponibles
- **Horarios flexibles**: Configuración por día con mañana/tarde

## 🚀 Instalación y Configuración

### 1. Dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración - Archivo `.env`

```bash
# Telegram Bot
BOT_TOKEN='tu_token_de_telegram'

# WhatsApp Bot (Meta Business API) - Opcional
WHATSAPP_ACCESS_TOKEN='tu_token_de_meta'
WHATSAPP_PHONE_NUMBER_ID='tu_phone_number_id'
WHATSAPP_BUSINESS_ACCOUNT_ID='tu_business_account_id'

# Admin - para recibir notificaciones inmediatas (opcional)
ADMIN_TELEFONO=549XXXXXXXXX    # Número WhatsApp del admin
ADMIN_CHAT_ID=123456789        # Chat ID Telegram del admin

# Sistema
NOTIFICATION_INTERVAL=60
LOG_LEVEL=INFO
```

### 3. Inicializar Base de Datos

```bash
# La base de datos se crea automáticamente al ejecutar cualquier script
python bot_core.py  # Esto creará turnos.db
```

## 📖 Comandos Principales

### Control del Sistema
```bash
# Daemon de notificaciones
./control_notificaciones.sh start    # Iniciar daemon automático
./control_notificaciones.sh stop     # Detener daemon
./control_notificaciones.sh status   # Ver estado del daemon
./control_notificaciones.sh logs     # Ver logs en tiempo real
./control_notificaciones.sh test     # Ejecutar envío manual una vez
./control_notificaciones.sh restart  # Reiniciar daemon

# Panel de administración
python admin_panel.py                # Iniciar panel web (puerto 9000)
```

### Bots Interactivos
```bash
# Telegram
python bot_telegram.py              # Bot conversacional Telegram

# WhatsApp
python bot_whatsapp.py              # Bot conversacional WhatsApp (puerto 5001)
```

### Envío Manual
```bash
python bot_sender.py               # Enviar notificaciones pendientes
```

### Utilidades
```bash
# Ver estado de notificaciones
python -c "from notifications import obtener_notificaciones_pendientes; print(f'Pendientes: {len(obtener_notificaciones_pendientes())}')"

# Limpiar notificaciones enviadas
python -c "from notifications import limpiar_notificaciones_enviadas; print(f'Eliminadas: {limpiar_notificaciones_enviadas()}')"

# Ver notificaciones del admin
python -c "from admin_notifications import obtener_notificaciones_admin; print(f'Admin: {len(obtener_notificaciones_admin())}')"
```

## 🔧 Estructura del Proyecto

### Archivos Principales
- **`bot_core.py`** - Lógica central del bot conversacional
- **`bot_config.py`** - Configuración centralizada desde `.env`
- **`database.py`** - Gestión de base de datos SQLite
- **`notifications.py`** - Sistema de notificaciones a usuarios
- **`admin_notifications.py`** - Sistema de notificaciones al admin

### Bots y Comunicación
- **`bot_telegram.py`** - Bot de Telegram
- **`bot_whatsapp.py`** - Bot de WhatsApp con webhook
- **`whatsapp_sender.py`** - Envío de mensajes WhatsApp
- **`bot_sender.py`** - Envío universal multi-canal

### Panel Web
- **`admin_panel.py`** - Servidor Flask del panel admin
- **`templates/admin_panel.html`** - Vista desktop del panel
- **`templates/admin_panel_mobile.html`** - Vista móvil optimizada
- **`static/`** - Archivos estáticos (CSS, JS, iconos PWA)

### Automatización
- **`daemon_notificaciones.py`** - Daemon en Python
- **`control_notificaciones.sh`** - Script de control del daemon

### Configuración
- **`.env`** - Variables de entorno
- **`config.json`** - Configuración de horarios y días bloqueados
- **`requirements.txt`** - Dependencias Python

### Datos
- **`turnos.db`** - Base de datos SQLite
- **`notifications_log.json`** - Log de notificaciones pendientes
- **`admin_notifications.json`** - Notificaciones para el admin
- **`daemon.pid`** - PID del daemon (cuando está activo)

## 🌐 URLs del Sistema

### Panel de Administración
- **Desktop**: `http://localhost:9000/`
- **Móvil**: `http://localhost:9000/mobile`
- **Dashboard PWA**: `http://localhost:9000/dashboard` (si implementado)

### APIs
- **Turnos semana**: `GET /api/turnos_semana?semana=2025-07-28`
- **Notificaciones usuario**: `GET /notificaciones`
- **Notificaciones admin**: `GET /api/notificaciones_admin`
- **Enviar manual**: `POST /api/enviar_notificaciones`
- **Estados canales**: `GET /api/canales_config`

### WhatsApp Webhook
- **Webhook**: `http://localhost:5001/webhook` (POST)
- **Verificación**: `http://localhost:5001/webhook` (GET)
- **Health Check**: `http://localhost:5001/health`

## 🔄 Flujo de Funcionamiento

### Para Usuarios
1. **Contacto inicial**: Usuario envía "hola" al bot
2. **Agendar turno**: Bot guía paso a paso (nombre → fecha → hora)
3. **Consultar turnos**: Lista turnos activos del usuario
4. **Cancelar turno**: Selección numérica para cancelar
5. **Notificaciones**: Recibe confirmaciones y avisos automáticos

### Para Admin
1. **Panel web**: Gestiona turnos desde `http://localhost:9000`
2. **Notificaciones inmediatas**: Recibe alertas por Telegram/WhatsApp
3. **Acciones disponibles**: Cancelar turnos, bloquear días, configurar horarios
4. **Monitoreo**: Dashboard con estadísticas y estado del sistema

### Envío Automático
1. **Daemon activo**: Ejecuta `bot_sender.py` cada 60 segundos
2. **Detección inteligente**: Identifica canal por formato de número
3. **Conversión automática**: Ajusta formato para WhatsApp (549→54)
4. **Limpieza automática**: Elimina notificaciones enviadas
5. **Logs detallados**: Registro completo de actividad

## 🌍 Detección Automática de Canales

El sistema detecta automáticamente qué canal usar:

- **Telegram**: Chat IDs numéricos (ej: `123456789`, `-100123456789`)
- **WhatsApp**: Números que empiecen con `549` (Argentina)

### Conversión Automática WhatsApp
- **Entrada**: `549XXXXXXXXX` (formato usuario argentino)
- **Salida**: `54XXXXXXXXX` (formato requerido por Meta API)

## 💾 Configuración Multi-Cliente

Para gestionar múltiples clientes:

1. **Duplicar proyecto**:
   ```bash
   cp -r turnosBot cliente2_turnos
   cd cliente2_turnos
   ```

2. **Configurar `.env`** con tokens diferentes

3. **Cambiar puertos** en `admin_panel.py` y `bot_whatsapp.py`

4. **Ejecutar independientemente**:
   ```bash
   ./control_notificaciones.sh start
   python admin_panel.py
   ```

## 🔍 Solución de Problemas

### Bot no responde
```bash
# Verificar configuración
python -c "from bot_config import config; print(f'Telegram: {config.has_telegram()}, WhatsApp: {config.has_whatsapp()}')"

# Ver logs del daemon
./control_notificaciones.sh logs
```

### Notificaciones no se envían
```bash
# Verificar notificaciones pendientes
python -c "from notifications import obtener_notificaciones_pendientes; print(len(obtener_notificaciones_pendientes()))"

# Envío manual para debug
python bot_sender.py
```

### WhatsApp no funciona
```bash
# Verificar webhook
curl http://localhost:5001/health

# Renovar token en Meta Developers si expiró
```

### Panel admin no carga
```bash
# Verificar puerto
netstat -tlnp | grep :9000

# Reiniciar
python admin_panel.py
```

## 📝 Logs y Monitoreo

### Archivos de Log
- **Daemon**: `./control_notificaciones.sh logs`
- **Bot Telegram**: Salida de consola de `bot_telegram.py`
- **Bot WhatsApp**: Salida de consola de `bot_whatsapp.py`
- **Panel Admin**: Salida de consola de `admin_panel.py`

### Datos de Estado
- **`notifications_log.json`**: Notificaciones pendientes para usuarios
- **`admin_notifications.json`**: Notificaciones para el administrador
- **`daemon.pid`**: PID del proceso daemon activo
- **`turnos.db`**: Base de datos SQLite con todos los turnos

---

## 🚀 Próximos Pasos Recomendados

1. **⚙️ Configurar variables admin** en `.env` para notificaciones inmediatas
2. **🌐 Migrar a la nube** (Railway, Render, Google Cloud Run)
3. **📱 Mejorar PWA** con mejor caching y funcionalidades offline
4. **🔐 Solicitar revisión Meta** para pasar WhatsApp a producción
5. **📊 Dashboard con estadísticas** y métricas del sistema
6. **🔄 Backup automático** de base de datos y configuración

¡El sistema está listo para producción! 🎉
