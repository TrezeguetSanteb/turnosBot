# 🚀 Guía para poner TurnosBot en la nube

## ¿Qué conseguimos?
- Un link público como: `https://tu-app.railway.app`
- **PWA instalable** desde cualquier dispositivo
- Funciona 24/7 sin que tengas que tener tu computadora prendida
- **WhatsApp Bot + Panel Admin + Notificaciones** todo en un solo lugar
- Es GRATIS (hasta cierto límite de uso)

## 🎯 **NUEVA ARQUITECTURA - Todo en Railway:**

### **✅ Servicios incluidos:**
1. **Panel PWA** → `https://tu-app.railway.app` (puerto principal)
2. **Bot WhatsApp** → `https://tu-app.railway.app/webhook` (mismo dominio)
3. **Daemon notificaciones** → Ejecutándose en background
4. **Base de datos SQLite** → Persistente en Railway

---

## 📋 **Paso a paso - Railway (Recomendado)**

### **1. Preparar el código**
```bash
# En tu terminal, dentro del proyecto:
git add .
git commit -m "TurnosBot completo para Railway"

# Si no tienes GitHub conectado:
git remote add origin https://github.com/TU_USUARIO/turnosBot.git
git branch -M main
git push -u origin main
```

### **2. Desplegar en Railway**
1. Ve a https://railway.app
2. Regístrate con tu cuenta de GitHub
3. **"New Project"** → **"Deploy from GitHub repo"**
4. Selecciona tu repositorio **"turnosBot"**
5. Railway detectará automáticamente que es Python

### **3. Configurar variables de entorno en Railway**
En tu proyecto Railway → **"Variables"**:

```bash
# WhatsApp (obligatorio para bot WhatsApp)
WHATSAPP_ACCESS_TOKEN=tu_token_de_meta
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
WHATSAPP_VERIFY_TOKEN=cualquier_texto_secreto
WHATSAPP_ALLOWED_NUMBERS=5491123456789,5499876543210

# Telegram (opcional, si también quieres Telegram)
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
TELEGRAM_CHAT_ID=tu_chat_id

# Admin
ADMIN_PHONE_NUMBER=5491123456789

# Producción
DEBUG=false
ENVIRONMENT=production
```

### **4. Configurar WhatsApp Webhook**
1. **Obtén tu URL**: Railway te dará algo como `https://turnosbot-production-xxxx.up.railway.app`
2. **En Meta Developers** (donde configuraste tu WhatsApp):
   - Webhook URL: `https://turnosbot-production-xxxx.up.railway.app/webhook`
   - Verify Token: El mismo que pusiste en `WHATSAPP_VERIFY_TOKEN`
3. **Suscribir a mensajes**: Activar "messages" en webhooks

### **5. ¡Listo! 🎉**

---

## 🌐 **Cómo usar después del despliegue:**

### **Para usuarios finales:**
- **Agendar turnos**: `https://tu-app.railway.app`
- **Instalar como app**: Ir al link, hacer clic en "Instalar app"

### **Para admin:**
- **Panel admin**: `https://tu-app.railway.app/mobile` (o `/admin`)
- **PWA**: Instalar y usar como app nativa

### **Para WhatsApp:**
- **Los usuarios escriben** al número de WhatsApp configurado
- **Reciben respuestas automáticas** del bot
- **El admin recibe notificaciones** automáticas

---

## 🔧 **Características técnicas:**

### **✅ Escalabilidad:**
- Todo corre en un solo contenedor optimizado
- Base de datos SQLite (perfecta para empezar)
- Memoria compartida entre servicios

### **✅ Monitoreo:**
- Health checks automáticos: `/health`
- Logs centralizados en Railway
- Restart automático si algo falla

### **✅ PWA Features:**
- **Instalable** en iOS/Android/Desktop
- **Funciona offline** (para consultas)
- **Notificaciones push** (próximamente)
- **Updates automáticos**

---

## 💰 **Costos y límites:**

### **Railway Free Tier:**
- **$5 USD/mes gratis** (no necesitas tarjeta)
- **500 horas/mes** (más que suficiente)
- **1GB RAM** y **1GB storage**
- **Dominio custom** disponible

### **Para escalar:**
- Si necesitas más, Railway Pro desde $20/mes
- Base de datos PostgreSQL externa (opcional)

---

## 🛠️ **Solución de problemas:**

### **Si el webhook no funciona:**
1. Verifica que la URL sea exacta
2. Revisa los logs en Railway
3. Confirma que `WHATSAPP_VERIFY_TOKEN` coincida

### **Si la PWA no instala:**
1. Debe ser HTTPS (Railway lo hace automático)
2. Verifica que `/manifest.json` sea accesible

### **Si las notificaciones no llegan:**
1. Revisa que `ADMIN_PHONE_NUMBER` esté correcto
2. Confirma que el daemon esté corriendo (logs)

---

## 🚀 **Próximos pasos avanzados:**

1. **Dominio personalizado**: `turnos.tuempresa.com`
2. **Base de datos externa**: PostgreSQL para múltiples instancias
3. **Analytics**: Tracking de uso
4. **Backup automático**: De la base de datos

---

## 📞 **Resultado final:**

### **Un link** → **App completa:**
```
https://tu-app.railway.app
├── 📱 PWA instalable
├── 🤖 Bot WhatsApp integrado  
├── 🔔 Notificaciones automáticas
├── 📊 Panel admin completo
└── 💾 Base de datos persistente
```

**¡Eso es todo!** Con un solo despliegue en Railway tienes una aplicación completa, profesional y accesible desde cualquier lugar del mundo.
