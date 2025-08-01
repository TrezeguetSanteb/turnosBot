# 🚀 GUÍA COMPLETA PARA DEPLOY EN RAILWAY - TURNOSBOT

## ✅ **ESTADO ACTUAL DEL PROYECTO**

### **📊 VERIFICACIÓN COMPLETADA**
- ✅ **9/9 módulos** funcionando correctamente
- ✅ **Estructura organizada** y profesional
- ✅ **Scripts ejecutables** funcionando
- ✅ **Archivos críticos** presentes (main.py, railway.json, requirements.txt)
- ✅ **Imports dinámicos** corregidos para máxima compatibilidad
- ✅ **Git repositorio** inicializado y listo

---

## 🎯 **PASO A PASO PARA DEPLOY**

### **FASE 1: PREPARACIÓN LOCAL**

#### **1.1. Verificar Estado Final**
```bash
# Ejecutar desde el directorio del proyecto
cd /ruta/a/turnosBot

# Verificar que todo funciona
python3 main.py --check-config

# Debería mostrar:
# [MAIN] 🚀 Iniciando TurnosBot en Railway...
# [MAIN] ✅ Todos los servicios iniciados
```

#### **1.2. Limpiar y Preparar Git**
```bash
# Agregar archivos al staging
git add .

# Verificar qué se va a commitear
git status

# Crear commit con la nueva estructura
git commit -m "feat: Implementar estructura modular y profesional

- Reorganizar código en estructura src/
- Crear sistema de imports dinámicos
- Organizar configuraciones en config/
- Centralizar datos en data/
- Separar frontend en web/
- Documentar en docs/
- Scripts organizados en scripts/
- Compatibilidad total con Railway
- Funcionalidad preservada 100%"
```

#### **1.3. Crear .gitignore Completo**
```bash
# Crear .gitignore si no existe
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
*.pid

# Database
*.db-journal

# Railway
.railway/

# Temporary files
tmp/
temp/
EOF
```

### **FASE 2: CONFIGURACIÓN EN RAILWAY**

#### **2.1. Crear Proyecto en Railway**
1. **Ir a Railway Dashboard**: https://railway.app/dashboard
2. **Click "New Project"**
3. **Seleccionar "Deploy from GitHub repo"**
4. **Conectar tu repositorio** `turnosBot`
5. **Railway detectará automáticamente** el archivo `railway.json`

#### **2.2. Configurar Variables de Entorno en Railway**

**⚠️ CRÍTICAS (Sin estas no funciona):**
```bash
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=tu_token_secreto_2024
ADMIN_PHONE_NUMBER=5491123456789
```

**🔧 OPCIONALES (Con valores por defecto):**
```bash
WHATSAPP_BUSINESS_ACCOUNT_ID=123456789
NOTIFICATION_INTERVAL=60
LOG_LEVEL=INFO
PORT=9000
```

**📋 Pasos en Railway:**
1. Ve a tu proyecto → **Variables**
2. Click **"Add Variable"**
3. Agregar una por una todas las variables
4. **Railway redeploy automáticamente** después de cada variable

#### **2.3. Verificar Configuración Railway**

**Archivo `railway.json` (ya configurado):**
```json
{
    "build": {
        "builder": "NIXPACKS"
    },
    "deploy": {
        "startCommand": "python main.py",
        "healthcheckPath": "/health",
        "healthcheckTimeout": 300,
        "restartPolicyType": "ON_FAILURE"
    }
}
```

### **FASE 3: DEPLOY Y VERIFICACIÓN**

#### **3.1. Push a Git y Deploy Automático**
```bash
# Push al repositorio (dispara deploy automático en Railway)
git push origin main

# Railway iniciará automáticamente:
# 1. Build del proyecto
# 2. Instalación de dependencias (requirements.txt)
# 3. Ejecución de main.py
```

#### **3.2. Monitorear Deploy en Railway**
1. **Ve a Railway Dashboard** → Tu Proyecto
2. **Click "Deployments"** para ver el progreso
3. **Monitorear logs** en tiempo real:
   ```
   [MAIN] 🚀 Iniciando TurnosBot en Railway...
   [MAIN] ✅ Todos los servicios iniciados
   [MAIN] 🌐 Panel disponible en puerto 9000
   ```

#### **3.3. Verificar URLs y Funcionamiento**

**Railway generará URLs automáticamente:**
- **Panel Admin**: `https://tu-proyecto.railway.app/`
- **Panel Móvil**: `https://tu-proyecto.railway.app/mobile`
- **Webhook WhatsApp**: `https://tu-proyecto.railway.app/webhook`

**Verificar que funciona:**
1. **Abrir Panel Admin** → Debe cargar correctamente
2. **Verificar Base de Datos** → Turnos deben aparecer
3. **Probar WhatsApp** → Enviar mensaje al bot
4. **Check Logs** → No debe haber errores críticos

### **FASE 4: CONFIGURACIÓN POST-DEPLOY**

#### **4.1. Configurar Webhook en Meta Developer Console**
1. **Ve a** https://developers.facebook.com/apps/
2. **Tu App** → WhatsApp → Configuration
3. **Webhook URL**: `https://tu-proyecto.railway.app/webhook`
4. **Verify Token**: El mismo que configuraste en `WHATSAPP_VERIFY_TOKEN`
5. **Subscribe to**: `messages`

#### **4.2. Verificar Conectividad**
```bash
# Probar webhook (desde tu local)
curl -X GET "https://tu-proyecto.railway.app/health"
# Debería responder: {"status": "ok"}

# Probar panel admin
curl -X GET "https://tu-proyecto.railway.app/"
# Debería responder con HTML del panel
```

#### **4.3. Monitoreo Continuo**
- **Railway Logs**: Monitorear errores en tiempo real
- **Panel Admin**: Verificar que los turnos se crean correctamente  
- **WhatsApp**: Probar flujo completo de reserva
- **Notificaciones**: Verificar que el daemon funciona

---

## 🔧 **TROUBLESHOOTING COMÚN**

### **❌ Error: "Module not found"**
**Solución**: Ya corregido con imports dinámicos en la nueva estructura

### **❌ Error: "Port already in use"**
**Solución**: Railway maneja puertos automáticamente, usar variable `PORT`

### **❌ Error: "Database not found"**
**Solución**: Verificar que `data/schema.sql` existe y es accesible

### **❌ Error: "Webhook verification failed"**
**Solución**: Verificar que `WHATSAPP_VERIFY_TOKEN` coincide exactamente

### **❌ Error: "Permission denied" en scripts**
**Solución**: 
```bash
chmod +x scripts/*.sh
git add scripts/
git commit -m "fix: Hacer scripts ejecutables"
git push
```

---

## 📊 **CHECKLIST FINAL PRE-DEPLOY**

### **✅ Archivos Críticos**
- [ ] `main.py` - Punto de entrada principal
- [ ] `railway.json` - Configuración Railway  
- [ ] `requirements.txt` - Dependencias Python
- [ ] `config/.env.template` - Template de variables
- [ ] `data/schema.sql` - Esquema de base de datos
- [ ] `src/` - Código fuente organizado

### **✅ Configuración Railway**
- [ ] Variables de entorno configuradas
- [ ] Repositorio conectado
- [ ] Deploy automático activado
- [ ] Webhook URL configurada en Meta

### **✅ Verificación Funcional**
- [ ] Imports funcionando (9/9 módulos)
- [ ] Scripts ejecutables (`./scripts/start_turnos.sh`)
- [ ] Panel admin carga correctamente
- [ ] Bot WhatsApp responde mensajes
- [ ] Base de datos operativa
- [ ] Daemon de notificaciones activo

---

## 🎉 **RESULTADO ESPERADO**

Una vez completado el deploy:

```
🎯 TURNOSBOT EN PRODUCCIÓN
========================

🌐 URLs:
• Panel Admin: https://tu-proyecto.railway.app/
• Panel Móvil: https://tu-proyecto.railway.app/mobile  
• API Webhook: https://tu-proyecto.railway.app/webhook

🤖 Servicios Activos:
• ✅ Panel de Administración Web
• ✅ Bot de WhatsApp Business
• ✅ Sistema de Notificaciones Automáticas
• ✅ Base de Datos SQLite
• ✅ Daemon de Envío de Mensajes

📊 Funcionalidades:
• ✅ Reserva de turnos via WhatsApp
• ✅ Gestión de turnos via panel web
• ✅ Notificaciones automáticas
• ✅ Panel responsive (móvil + desktop)
• ✅ Logs en tiempo real
• ✅ Auto-restart en caso de errores
```

**🚀 ¡Tu sistema TurnosBot estará completamente operativo en producción con una estructura profesional y escalable!**
