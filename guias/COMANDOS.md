# Comandos Útiles - Sistema de Turnos

## Instalación Inicial
```bash
# Clonar o descargar proyecto
# cd turnosBot

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus tokens

# Inicializar base de datos (automático)
python bot_core.py
```

## Comandos de Desarrollo

### Verificar Estado del Sistema
```bash
# Estado completo
./control_notificaciones.sh status
python -c "from bot_config import config; print(f'Telegram: {config.has_telegram()}, WhatsApp: {config.has_whatsapp()}')"

# Notificaciones pendientes
python -c "from notifications import obtener_notificaciones_pendientes; print(f'Usuario: {len(obtener_notificaciones_pendientes())}')"
python -c "from admin_notifications import obtener_notificaciones_admin; print(f'Admin: {len(obtener_notificaciones_admin())}')"

# Turnos en base de datos
python -c "from database import obtener_todos_los_turnos; print(f'Turnos totales: {len(obtener_todos_los_turnos())}')"
```

### Testing y Debug
```bash
# Prueba de envío manual
python bot_sender.py

# Prueba de notificación específica
python -c "
from admin_notifications import notificar_turno_agendado
notificar_turno_agendado('Test User', '2025-07-30', '15:00', '5491234567890')
"

# Ver última notificación creada
python -c "
from admin_notifications import obtener_notificaciones_admin
notifs = obtener_notificaciones_admin()
if notifs: print(f'Última: {notifs[0]}')
"

# Limpiar notificaciones de prueba
python -c "
from notifications import limpiar_notificaciones_enviadas
from admin_notifications import limpiar_notificaciones_admin
print(f'Usuario eliminadas: {limpiar_notificaciones_enviadas()}')
print(f'Admin eliminadas: {limpiar_notificaciones_admin()}')
"
```

### Simulación de Webhooks WhatsApp
```bash
# Webhook de verificación
curl "http://localhost:5001/webhook?hub.verify_token=mi_token_verificacion_whatsapp&hub.challenge=test123"

# Mensaje de prueba
curl -X POST http://localhost:5001/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "changes": [{
        "field": "messages",
        "value": {
          "messages": [{
            "from": "5491234567890",
            "type": "text",
            "text": {"body": "hola"}
          }]
        }
      }]
    }]
  }'

# Health check
curl http://localhost:5001/health
```

### APIs del Panel Admin
```bash
# Obtener turnos de la semana
curl "http://localhost:9000/api/turnos_semana?semana=2025-07-28"

# Notificaciones de usuario
curl http://localhost:9000/notificaciones

# Notificaciones de admin
curl http://localhost:9000/api/notificaciones_admin

# Estado de canales
curl http://localhost:9000/api/canales_config

# Enviar notificaciones manualmente
curl -X POST http://localhost:9000/api/enviar_notificaciones

# Marcar notificaciones como leídas
curl -X POST http://localhost:9000/api/marcar_notificaciones_leidas \
  -H "Content-Type: application/json" \
  -d '{"ids": [1, 2, 3]}'
```

## Base de Datos

### Consultas Útiles
```sql
-- Conectar a la base
sqlite3 turnos.db

-- Ver todos los turnos
SELECT * FROM turnos ORDER BY fecha, hora;

-- Turnos de hoy
SELECT * FROM turnos WHERE fecha = date('now');

-- Turnos por teléfono
SELECT * FROM turnos WHERE telefono = '5491234567890';

-- Estadísticas
SELECT 
  DATE(fecha) as dia,
  COUNT(*) as total_turnos
FROM turnos 
GROUP BY DATE(fecha) 
ORDER BY dia DESC;

-- Limpiar turnos antiguos (más de 30 días)
DELETE FROM turnos WHERE fecha < date('now', '-30 days');
```

### Backup y Restore
```bash
# Backup completo
cp turnos.db turnos_backup_$(date +%Y%m%d).db
cp notifications_log.json notifications_backup_$(date +%Y%m%d).json
cp admin_notifications.json admin_notifications_backup_$(date +%Y%m%d).json
cp config.json config_backup_$(date +%Y%m%d).json

# Restore
cp turnos_backup_20250725.db turnos.db
```

## Logs y Monitoreo

### Ver Logs en Tiempo Real
```bash
# Daemon
./control_notificaciones.sh logs

# Panel admin con filtro
python admin_panel.py 2>&1 | grep -E "(ERROR|WARNING|Notificación)"

# Bot WhatsApp con filtro
python bot_whatsapp.py 2>&1 | grep -E "(ERROR|Mensaje|Respuesta)"
```

### Análisis de Logs
```bash
# Contar notificaciones enviadas hoy
grep "$(date +%Y-%m-%d)" notifications_log.json | wc -l

# Últimos errores
grep -i error *.log | tail -10

# Estadísticas de uso por hora
grep "Mensaje de" bot_whatsapp.log | cut -d' ' -f2 | cut -d: -f1 | sort | uniq -c
```

## Productivización

### Configuración para Servidor
```bash
# Instalar como servicio systemd
sudo cp turnosbot.service /etc/systemd/system/
sudo systemctl enable turnosbot
sudo systemctl start turnosbot

# Variables de entorno para producción
export FLASK_ENV=production
export PYTHONPATH=/path/to/turnosBot
```

### Docker (Opcional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001 9000
CMD ["python", "daemon_notificaciones.py"]
```

### Nginx para WhatsApp Webhook
```nginx
server {
    listen 443 ssl;
    server_name tu-dominio.com;
    
    location /webhook {
        proxy_pass http://localhost:5001/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Problemas Comunes
```bash
# Puerto ocupado
netstat -tlnp | grep :9000
kill $(lsof -t -i:9000)

# Permisos del script
chmod +x control_notificaciones.sh

# Dependencias faltantes
pip install -r requirements.txt --upgrade

# Base de datos corrupta
rm turnos.db
python bot_core.py  # Se recrea automáticamente

# Token expirado WhatsApp
# Renovar en Meta Developers y actualizar .env
```

### Logs de Debug Detallados
```bash
# Activar debug completo
export LOG_LEVEL=DEBUG

# Bot con debug máximo
python -u bot_telegram.py 2>&1 | tee telegram_debug.log

# WhatsApp con requests debug
export PYTHONPATH=$PYTHONPATH:$PWD
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import requests
requests.post('http://localhost:5001/webhook', json={'test': True})
"
```

## Railway - Producción

### URLs Automáticas que Railway Genera
```bash
# Después del deploy, Railway te da:
# URL Base: https://tu-proyecto.up.railway.app

# Panel de administración (PWA)
https://tu-proyecto.up.railway.app/mobile

# Webhook para WhatsApp
https://tu-proyecto.up.railway.app/webhook

# Health check (monitoreo)
https://tu-proyecto.up.railway.app/health

# API de estadísticas
https://tu-proyecto.up.railway.app/api/stats

# API de mantenimiento
https://tu-proyecto.up.railway.app/api/mantenimiento
```

### Configuración de Variables en Railway
```bash
# En Railway Dashboard > Variables:
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=mi_token_secreto
ADMIN_PHONE_NUMBER=+5491123456789

# Railway asigna automáticamente:
PORT=8080  # (o el que Railway asigne)
RAILWAY_STATIC_URL=https://tu-proyecto.up.railway.app
```

### Verificación Post-Deploy
```bash
# Verificar que la app está funcionando
curl https://tu-proyecto.up.railway.app/health

# Respuesta esperada:
# {
#   "status": "ok",
#   "service": "TurnosBot Admin Panel", 
#   "timestamp": "2025-07-28T..."
# }

# Verificar webhook WhatsApp
curl "https://tu-proyecto.up.railway.app/webhook?hub.verify_token=tu_verify_token&hub.challenge=test123"

# Respuesta esperada: test123

# Ver estadísticas de la BD
curl https://tu-proyecto.up.railway.app/api/stats

# Acceder al panel admin
# https://tu-proyecto.up.railway.app/mobile
```

### Logs en Railway
```bash
# En Railway Dashboard > Deployments > View Logs

# También puedes usar Railway CLI:
railway logs

# Ver logs en tiempo real:
railway logs --follow
```

### Configurar Webhook en Meta Developer
```bash
# Una vez que tienes la URL de Railway:

# 1. Ir a Meta Developer Console
# 2. Tu App > WhatsApp > Configuration
# 3. Webhook URL: https://tu-proyecto.up.railway.app/webhook
# 4. Verify Token: el mismo que pusiste en WHATSAPP_VERIFY_TOKEN
# 5. Subscribe to: messages
```

### Comandos de Monitoreo Remoto
```bash
# Health check
curl https://tu-proyecto.up.railway.app/health

# Ver turnos de la semana actual
curl "https://tu-proyecto.up.railway.app/api/turnos_semana"

# Ejecutar mantenimiento manual
curl -X POST https://tu-proyecto.up.railway.app/api/mantenimiento

# Ver estadísticas de la base de datos
curl https://tu-proyecto.up.railway.app/api/stats
```
