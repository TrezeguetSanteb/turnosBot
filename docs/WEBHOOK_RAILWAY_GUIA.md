# 🔗 CONFIGURACIÓN DEL WEBHOOK WHATSAPP EN RAILWAY

## 🎯 RESPUESTA DIRECTA

**SÍ, Railway te da la URL para el webhook de WhatsApp automáticamente.**

**Es la MISMA URL base + `/webhook`**

## 🌐 EJEMPLO COMPLETO

### Tu URL de Railway:
```
https://turnosbot-peluqueria.up.railway.app
```

### URL del Webhook para WhatsApp:
```
https://turnosbot-peluqueria.up.railway.app/webhook
```

## 📋 PASO A PASO: CONFIGURAR WEBHOOK EN META

### 1. **Obtener URL de Railway**
Después del deploy en Railway:
```
1. Ve a Railway Dashboard
2. Click en tu proyecto
3. Ve a "Deployments" 
4. Copia la URL que aparece (ej: https://turnosbot-abc123.up.railway.app)
```

### 2. **Configurar en Meta Developer Console**
```
1. Ve a https://developers.facebook.com/apps/
2. Selecciona tu App de WhatsApp Business
3. Ve a WhatsApp > Configuration
4. En "Webhook" section:
   
   📝 Callback URL: https://turnosbot-peluqueria.up.railway.app/webhook
   📝 Verify Token: mi_token_secreto_super_seguro_2024
   
5. Click "Verify and Save"
6. Subscribe to field: messages
```

### 3. **Variables que DEBEN coincidir**

En **Railway Dashboard > Variables**:
```bash
WHATSAPP_VERIFY_TOKEN=mi_token_secreto_super_seguro_2024
```

En **Meta Developer Console > Webhook**:
```bash
Verify Token: mi_token_secreto_super_seguro_2024
```

**¡DEBEN SER EXACTAMENTE IGUALES!**

## 🧪 VERIFICACIÓN DEL WEBHOOK

### Probar verificación manualmente:
```bash
# Reemplaza con tu URL real de Railway
curl "https://turnosbot-peluqueria.up.railway.app/webhook?hub.verify_token=mi_token_secreto_super_seguro_2024&hub.challenge=test123"

# Respuesta esperada: test123
```

### Probar que el servidor responde:
```bash
# Health check
curl https://turnosbot-peluqueria.up.railway.app/health

# Respuesta esperada:
# {
#   "status": "ok",
#   "service": "whatsapp-bot", 
#   "whatsapp_configured": true
# }
```

## 🔧 ARQUITECTURA EN RAILWAY

```
Railway URL: https://turnosbot-peluqueria.up.railway.app
│
├── /mobile     ← Panel Admin (PWA)
├── /webhook    ← WhatsApp Webhook (GET/POST)
├── /health     ← Health Check
└── /api/stats  ← API de estadísticas
```

### El proceso `main.py` ejecuta:
1. **Panel Admin** en puerto principal (ej: 8080)
2. **Bot WhatsApp** en puerto principal + 1 (ej: 8081)
3. **Daemon** en background

### Railway maneja automáticamente:
- ✅ **Routing** entre servicios
- ✅ **Load balancing**
- ✅ **HTTPS** (certificado SSL gratis)
- ✅ **URL única** para todo

## 📝 CONFIGURACIÓN COMPLETA PASO A PASO

### En Railway Dashboard:
```bash
# Variables necesarias:
WHATSAPP_ACCESS_TOKEN=EAABwIjMvEaaBAPI1234567890abcdefghijklmnopqrstuvwxyz
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=mi_token_secreto_super_seguro_2024
ADMIN_PHONE_NUMBER=5491123456789
```

### En Meta Developer Console:
```bash
# WhatsApp > Configuration > Webhook:
Callback URL: https://TU-URL-DE-RAILWAY.up.railway.app/webhook
Verify Token: mi_token_secreto_super_seguro_2024
Webhook Fields: ☑️ messages
```

## 🚨 ERRORES COMUNES

### ❌ Error: "The callback URL or verify token couldn't be validated"
```
Problema: Token no coincide o URL incorrecta
Solución: 
1. Verificar que WHATSAPP_VERIFY_TOKEN en Railway = Verify Token en Meta
2. Verificar que la URL termine en /webhook
3. Verificar que el deploy esté funcionando (health check)
```

### ❌ Error: "URL not reachable"
```
Problema: Railway app no está funcionando
Solución:
1. Verificar deploy exitoso en Railway Dashboard
2. Probar health check: https://tu-url.up.railway.app/health
3. Ver logs en Railway Dashboard > Deployments > View Logs
```

### ❌ Error: Webhook verifica pero no recibe mensajes
```
Problema: Variables de WhatsApp incorrectas
Solución:
1. Verificar WHATSAPP_ACCESS_TOKEN
2. Verificar WHATSAPP_PHONE_NUMBER_ID
3. Verificar que el número esté asociado a la app en Meta
```

## 🔍 DEBUGGING DEL WEBHOOK

### Ver logs en tiempo real:
```bash
# En Railway Dashboard:
1. Ve a tu proyecto
2. Click "Deployments"
3. Click "View Logs"
4. Envía un mensaje de prueba al WhatsApp
5. Verifica que aparezcan logs del webhook
```

### Logs esperados:
```
[MAIN] ✅ Bot WhatsApp iniciado
INFO - Webhook verificado exitosamente
INFO - Mensaje de +5491123456789: hola
INFO - Procesando mensaje con bot_core...
INFO - Respuesta generada: ¡Hola! 👋 Bienvenido al sistema de turnos...
INFO - Respuesta enviada a +5491123456789
```

## 📞 EJEMPLO COMPLETO DE CONFIGURACIÓN

### Cliente: "Peluquería Moderna"

**Railway URL generada:**
```
https://peluqueria-moderna-abc123.up.railway.app
```

**Variables en Railway:**
```bash
WHATSAPP_ACCESS_TOKEN=EAABwIjMvEaaBAPI1234567890abcdefg
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=peluqueria_token_2024
ADMIN_PHONE_NUMBER=5491122334455
```

**Configuración en Meta:**
```
App Name: Peluquería Moderna Bot
Webhook URL: https://peluqueria-moderna-abc123.up.railway.app/webhook
Verify Token: peluqueria_token_2024
WhatsApp Number: +54 9 11 8888-9999
```

**URLs finales:**
```
✅ Panel Admin: https://peluqueria-moderna-abc123.up.railway.app/mobile
✅ Webhook: https://peluqueria-moderna-abc123.up.railway.app/webhook
✅ Health: https://peluqueria-moderna-abc123.up.railway.app/health
```

---

## 🎯 RESUMEN

**Railway te da UNA URL que sirve para TODO:**
- ✅ **Panel de administración** en `/mobile`
- ✅ **Webhook de WhatsApp** en `/webhook` ← **ESTO ES LO QUE NECESITAS**
- ✅ **APIs y health checks** en otros endpoints

**No necesitas configurar nada extra. Railway automáticamente expone todos los endpoints del mismo dominio con HTTPS incluido.**

## 🔧 VERIFICACIÓN TÉCNICA DEL WEBHOOK

### Endpoints disponibles en Railway:
```python
# En bot_whatsapp.py:
@app.route('/webhook', methods=['GET'])   # ← Verificación de Meta
def verify_webhook():
    # Verifica WHATSAPP_VERIFY_TOKEN
    
@app.route('/webhook', methods=['POST'])  # ← Recepción de mensajes
def whatsapp_webhook():
    # Procesa mensajes de WhatsApp
    
@app.route('/health', methods=['GET'])    # ← Health check
def health_check():
    # Estado del bot WhatsApp
```

### Flujo de verificación en Meta Console:
```
1. Meta envía GET request:
   https://tu-app.up.railway.app/webhook?hub.verify_token=TU_TOKEN&hub.challenge=RANDOM_STRING

2. bot_whatsapp.py verifica:
   - Compara hub.verify_token con WHATSAPP_VERIFY_TOKEN
   - Si coincide, devuelve hub.challenge
   - Si no coincide, devuelve error 403

3. Meta recibe la respuesta:
   - Si recibe hub.challenge → ✅ Webhook verificado
   - Si recibe error → ❌ Configuración incorrecta
```

### Logs de verificación exitosa:
```
[bot_whatsapp] INFO - Webhook verificado exitosamente
```

### Logs de verificación fallida:
```
[bot_whatsapp] ERROR - Token de verificación inválido. Esperado: mi_token, Recibido: token_incorrecto
```

## 🚀 PROCESO COMPLETO DE SETUP

### 1. Deploy en Railway (automático)
```bash
git push origin main
# Railway detecta cambios y hace deploy automático
# Genera URL: https://tu-proyecto-abc123.up.railway.app
```

### 2. Configurar variables en Railway
```bash
# Railway Dashboard > Variables > Add Variable:
WHATSAPP_ACCESS_TOKEN=EAAxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345  
WHATSAPP_VERIFY_TOKEN=mi_token_secreto_2024
ADMIN_PHONE_NUMBER=5491123456789
```

### 3. Verificar que el servidor funciona
```bash
curl https://tu-proyecto-abc123.up.railway.app/health
# Respuesta: {"status":"ok","service":"whatsapp-bot","whatsapp_configured":true}
```

### 4. Configurar webhook en Meta
```bash
# Meta Developer Console > WhatsApp > Configuration:
Callback URL: https://tu-proyecto-abc123.up.railway.app/webhook
Verify Token: mi_token_secreto_2024
```

### 5. Meta verifica automáticamente
```bash
# Meta envía GET request a tu webhook
# Si todo está bien, se muestra "✅ Complete"
```

### 6. Activar suscripción a mensajes
```bash
# Meta Developer Console > WhatsApp > Configuration:
Webhook fields: ☑️ messages
```

### 7. Probar envío de mensaje
```bash
# Envía WhatsApp al número configurado
# Deberías ver logs en Railway Dashboard > Deployments > View Logs
```
