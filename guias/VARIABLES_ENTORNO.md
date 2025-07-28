# 🔧 VARIABLES DE ENTORNO - CONFIGURACIÓN COMPLETA

## 📋 VARIABLES REQUERIDAS (CRÍTICAS)

### WhatsApp Business API
```bash
# Token de acceso de WhatsApp Business API
# Obténlo desde: https://developers.facebook.com/apps/
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ID del número de teléfono de WhatsApp Business  
# Formato: solo números, sin + ni espacios
# Ejemplo: 15551234567 (para +1 555 123-4567)
WHATSAPP_PHONE_NUMBER_ID=123456789012345

# Token para verificar webhook (elige cualquier string secreto)
# Debe coincidir con el configurado en Meta Developer Console
WHATSAPP_VERIFY_TOKEN=mi_token_secreto_super_seguro_2024

# Número de WhatsApp del administrador (recibe notificaciones)
# Formato: código país + número sin espacios ni símbolos
# Ejemplo: 5491123456789 (para +54 9 11 2345-6789)
ADMIN_PHONE_NUMBER=5491123456789
```

## 📋 VARIABLES OPCIONALES (RECOMENDADAS)

### WhatsApp Business API (Opcional)
```bash
# ID de la cuenta de WhatsApp Business (mejora el logging)
WHATSAPP_BUSINESS_ACCOUNT_ID=123456789012345
```

### Configuración del Sistema
```bash
# Intervalo de verificación de notificaciones en segundos
# Default: 60 segundos (1 minuto)
# Rango recomendado: 30-300 segundos
NOTIFICATION_INTERVAL=60

# Nivel de logging para debug
# Valores: DEBUG, INFO, WARNING, ERROR
# Recomendado para producción: INFO
LOG_LEVEL=INFO
```

## 📋 VARIABLES AUTOMÁTICAS DE RAILWAY (NO CONFIGURAR)

```bash
# Puerto asignado automáticamente por Railway
# Railway asigna esto automáticamente, NO lo configures manualmente
PORT=8080

# URL estática asignada por Railway
# Railway genera esto automáticamente después del primer deploy
RAILWAY_STATIC_URL=https://tu-proyecto-abc123.up.railway.app

# Environment de Railway
RAILWAY_ENVIRONMENT=production
```

## 🔍 VERIFICACIÓN DE VARIABLES

### En main.py se verifica automáticamente:
```python
def verificar_variables_entorno():
    # Variables críticas (DEBEN estar configuradas)
    variables_criticas = {
        'WHATSAPP_ACCESS_TOKEN': 'Token de WhatsApp',
        'WHATSAPP_PHONE_NUMBER_ID': 'ID del número de WhatsApp', 
        'WHATSAPP_VERIFY_TOKEN': 'Token de verificación',
        'ADMIN_PHONE_NUMBER': 'Número del administrador'
    }
    
    # Variables opcionales (mejoran la funcionalidad)
    variables_opcionales = {
        'WHATSAPP_BUSINESS_ACCOUNT_ID': 'ID de cuenta WhatsApp',
        'NOTIFICATION_INTERVAL': 'Intervalo de notificaciones',
        'LOG_LEVEL': 'Nivel de logging'
    }
```

## 🚂 CONFIGURACIÓN EN RAILWAY DASHBOARD

### Paso a paso:
1. **Ir a Railway Dashboard**
2. **Seleccionar tu proyecto**  
3. **Click en "Variables"**
4. **Click "Add Variable"**
5. **Agregar cada variable una por una:**

```
Variable Name: WHATSAPP_ACCESS_TOKEN
Variable Value: EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Variable Name: WHATSAPP_PHONE_NUMBER_ID  
Variable Value: 123456789012345

Variable Name: WHATSAPP_VERIFY_TOKEN
Variable Value: mi_token_secreto_super_seguro_2024

Variable Name: ADMIN_PHONE_NUMBER
Variable Value: 5491123456789
```

## ⚠️ IMPORTANTE: SEGURIDAD

### ❌ NO HAGAS ESTO:
```bash
# NO subas un archivo .env al repositorio
# NO hardcodees tokens en el código
# NO compartas tokens en mensajes/emails
```

### ✅ HAZ ESTO:
```bash
# ✅ Configura variables solo en Railway Dashboard
# ✅ Usa .env solo para desarrollo local (en .gitignore)
# ✅ Regenera tokens si los comprometes
```

## 🧪 VERIFICACIÓN LOCAL vs PRODUCCIÓN

### Desarrollo Local (.env):
```bash
# Crea archivo .env para desarrollo local
WHATSAPP_ACCESS_TOKEN=EAAxxxxx_desarrollo
WHATSAPP_PHONE_NUMBER_ID=123456_desarrollo
WHATSAPP_VERIFY_TOKEN=token_desarrollo
ADMIN_PHONE_NUMBER=549111111111
```

### Producción Railway (Variables):
```bash
# Configura en Railway Dashboard > Variables
# NUNCA subas el archivo .env al repositorio
# Railway usa las variables del Dashboard, no archivos .env
```

## 🔧 COMANDOS DE VERIFICACIÓN

### Verificar variables localmente:
```bash
# Verificar que todas las variables estén configuradas
python -c "
import os
vars_needed = ['WHATSAPP_ACCESS_TOKEN', 'WHATSAPP_PHONE_NUMBER_ID', 'WHATSAPP_VERIFY_TOKEN', 'ADMIN_PHONE_NUMBER']
for var in vars_needed:
    value = os.environ.get(var)
    if value:
        print(f'✅ {var}: {value[:10]}...')
    else:
        print(f'❌ {var}: NO CONFIGURADA')
"
```

### Verificar variables en Railway:
```bash
# Después del deploy, verifica via health check
curl https://tu-proyecto.up.railway.app/health

# Ver logs de inicio en Railway Dashboard > Deployments > Logs
# Buscar líneas que empiecen con [MAIN]
```

## 📊 EJEMPLO DE SALIDA DE VERIFICACIÓN

### Configuración Correcta:
```
[MAIN] 🔍 Verificando variables de entorno...
[MAIN] ✅ WHATSAPP_ACCESS_TOKEN: EAABwIjMvE...BZCc6u
[MAIN] ✅ WHATSAPP_PHONE_NUMBER_ID: 12345...7890
[MAIN] ✅ WHATSAPP_VERIFY_TOKEN: mi_tok...2024
[MAIN] ✅ ADMIN_PHONE_NUMBER: 54911...6789
[MAIN] ✅ NOTIFICATION_INTERVAL: 60
[MAIN] ✅ LOG_LEVEL: INFO
[MAIN] 🚂 Railway URL: https://tu-proyecto.up.railway.app
```

### Configuración Incompleta:
```
[MAIN] 🔍 Verificando variables de entorno...
[MAIN] ❌ VARIABLES CRÍTICAS FALTANTES:
[MAIN]    ❌ WHATSAPP_ACCESS_TOKEN: Token de acceso de WhatsApp Business API
[MAIN]    ❌ ADMIN_PHONE_NUMBER: Número de teléfono del administrador
[MAIN] 
[MAIN] 🔧 Para configurar en Railway:
[MAIN]    1. Ve a Railway Dashboard > Tu Proyecto > Variables
[MAIN]    2. Click 'Add Variable' para cada una
[MAIN]    3. Redeploy automático después de agregar variables
```

---

## 🎯 RESUMEN RÁPIDO

**Variables que DEBES configurar en Railway:**
1. `WHATSAPP_ACCESS_TOKEN` - Token de Meta
2. `WHATSAPP_PHONE_NUMBER_ID` - ID del número de WhatsApp  
3. `WHATSAPP_VERIFY_TOKEN` - Token secreto para webhook
4. `ADMIN_PHONE_NUMBER` - Número que recibe notificaciones

**El resto son opcionales y tienen valores por defecto sensatos.**
