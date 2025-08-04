# 🚂 Solución para Hibernación de Railway - TurnosBot

## 🔍 Problema Identificado

**Railway hiberna las aplicaciones** cuando no reciben tráfico HTTP por un período determinado. En TurnosBot:

- El **daemon de notificaciones** corre en background (no es HTTP)
- Cuando Railway hiberna la app, el **daemon se pausa**
- Los usuarios **NO reciben notificaciones** de WhatsApp cuando el admin cancela turnos

## ✅ Solución Implementada

### 1. Sistema Keep-Alive Anti-Hibernación

- **Endpoint HTTP**: `/api/keep-alive` en el panel de administración
- **Auto-ping**: El daemon hace ping a su propio endpoint cada 5 minutos
- **Resultado**: Railway detecta actividad HTTP y mantiene la app activa

### 2. Archivos Modificados

#### `src/admin/panel.py`
```python
@app.route('/api/keep-alive')
def keep_alive():
    """Endpoint para mantener la aplicación activa en Railway"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.now().isoformat(),
        'message': 'TurnosBot daemon keep-alive ping'
    })
```

#### `src/services/daemon.py`
- Detecta automáticamente si está en Railway
- Configura sistema keep-alive (ping cada 5 minutos)
- Mantiene funcionamiento normal en local
- Logs detallados de actividad

### 3. Scripts de Diagnóstico

- **`test_keep_alive.py`**: Prueba el sistema keep-alive
- **`test_railway.py`**: Diagnóstico completo para Railway
- **`solucion_hibernacion.py`**: Verificación final de la solución

## 🚀 Cómo Usar

### En Railway:

1. **Desplegar** los cambios actuales
2. **Verificar logs** del daemon:
   ```
   🚂 Entorno: Railway
   🌐 URL: https://tu-app.railway.app
   🏓 Keep-alive: Activado (cada 5.0 min)
   ```
3. **Observar pings** cada 5 minutos:
   ```
   🏓 Keep-alive ping a https://tu-app.railway.app/api/keep-alive
   ✅ Keep-alive ping enviado
   ```

### Probar Funcionamiento:

1. **Cancelar turno** desde panel admin
2. **Verificar notificación** creada en logs
3. **Confirmar WhatsApp** enviado al usuario

## 📊 Funcionamiento Técnico

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Panel Admin   │    │      Daemon      │    │   WhatsApp API  │
│                 │    │                  │    │                 │
│ 1. Cancela      │───►│ 2. Procesa       │───►│ 3. Envía        │
│    turno        │    │    notificación  │    │    mensaje      │
│                 │    │                  │    │                 │
│ 4. Keep-alive   │◄───│ 5. Auto-ping     │    │                 │
│    endpoint     │    │    cada 5 min    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       🚂 Railway detecta
                          actividad HTTP
                       → No hiberna la app
```

## ⚡ Antes vs Después

### ❌ Antes (Con hibernación):
1. Admin cancela turno
2. Notificación se crea ✅
3. Railway hiberna app 😴
4. Daemon se pausa ⏸️
5. Usuario NO recibe WhatsApp ❌

### ✅ Después (Con keep-alive):
1. Admin cancela turno
2. Notificación se crea ✅
3. Daemon hace ping 🏓
4. Railway mantiene app activa 🟢
5. Usuario recibe WhatsApp ✅

## 🔧 Configuración

### Variables de Entorno (Railway):
- `WHATSAPP_ACCESS_TOKEN`: Token de acceso a WhatsApp
- `WHATSAPP_PHONE_NUMBER_ID`: ID del número de teléfono
- `WHATSAPP_VERIFY_TOKEN`: Token de verificación
- `ADMIN_PHONE_NUMBER`: Número del administrador

### Auto-detectadas:
- `RAILWAY_STATIC_URL`: URL pública del servicio
- `RAILWAY_ENVIRONMENT`: Entorno de Railway
- `PORT`: Puerto asignado por Railway

## 📋 Verificación en Railway

### 1. Logs del Daemon:
```bash
# Buscar estos mensajes en los logs:
[timestamp] 🤖 DAEMON DE NOTIFICACIONES INICIADO
[timestamp] 🚂 Entorno: Railway
[timestamp] 🏓 Keep-alive: Activado (cada 5.0 min)
[timestamp] 🏓 Keep-alive ping a https://tu-app.railway.app/api/keep-alive
[timestamp] ✅ Keep-alive ping enviado
```

### 2. Test Manual:
```bash
# En Railway shell o localmente:
python test_railway.py
python solucion_hibernacion.py
```

### 3. Endpoint Manual:
```bash
curl https://tu-app.railway.app/api/keep-alive
# Debe responder: {"status": "alive", "timestamp": "...", "message": "..."}
```

## 🎯 Próximos Pasos

1. ✅ **Implementado**: Sistema anti-hibernación
2. 🚀 **Desplegar**: Cambios en Railway
3. 👀 **Monitorear**: Logs de keep-alive
4. 🧪 **Probar**: Cancelación de turno real
5. 📱 **Confirmar**: Usuario recibe WhatsApp

---

## 🏆 Resultado Esperado

Con esta solución, **TurnosBot funcionará correctamente en Railway** sin problemas de hibernación:

- ✅ Daemon siempre activo
- ✅ Notificaciones procesadas en tiempo real
- ✅ Usuarios reciben WhatsApp al cancelar turnos
- ✅ Sistema estable en producción

**¡El problema de hibernación está resuelto!** 🎉
