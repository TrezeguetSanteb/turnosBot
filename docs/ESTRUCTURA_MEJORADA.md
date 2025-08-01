# 📁 ESTRUCTURA COMPLETA DEL PROYECTO REORGANIZADO

## 🎯 ESTRUCTURA PROPUESTA COMPLETA

```
turnosBot/
├── main.py                           # Punto de entrada principal
├── requirements.txt                  # Dependencias Python
├── railway.json                      # Configuración Railway
├── README.md                         # Documentación principal
├── .gitignore                        # Git ignore
│
├── src/                              # Código fuente
│   ├── __init__.py
│   ├── core/                         # Lógica central
│   │   ├── __init__.py
│   │   ├── bot_core.py               # Lógica principal del bot
│   │   ├── config.py                 # bot_config.py renombrado
│   │   └── database.py               # Gestor de base de datos
│   │
│   ├── bots/                         # Implementaciones de bots
│   │   ├── __init__.py
│   │   ├── whatsapp_bot.py           # bot_whatsapp.py renombrado
│   │   ├── telegram_bot.py           # bot_telegram.py renombrado
│   │   └── senders/
│   │       ├── __init__.py
│   │       ├── whatsapp_sender.py    # Envío WhatsApp
│   │       └── bot_sender.py         # Envío genérico
│   │
│   ├── admin/                        # Panel de administración
│   │   ├── __init__.py
│   │   ├── panel.py                  # admin_panel.py renombrado
│   │   └── notifications.py          # admin_notifications.py
│   │
│   ├── services/                     # Servicios y daemons
│   │   ├── __init__.py
│   │   ├── daemon.py                 # daemon_notificaciones.py
│   │   ├── notifications.py          # notifications.py
│   │   └── maintenance.py            # db_maintenance.py
│   │
│   └── utils/                        # Utilidades
│       ├── __init__.py
│       └── helpers.py                # Funciones auxiliares
│
├── scripts/                          # Scripts de utilidades (.sh)
│   ├── check_nuevo_cliente.sh        # Verificar configuración cliente
│   ├── check_deploy_ready.sh         # Verificar antes de deploy
│   ├── setup.sh                      # Instalación inicial
│   ├── backup.sh                     # Backup automático
│   ├── maintenance.sh                # Mantenimiento manual
│   └── migrate.sh                    # Script para migrar estructura
│
├── config/                           # Configuraciones (.json y templates)
│   ├── .env.template                 # Template variables entorno
│   ├── config.json                   # Configuración del sistema
│   ├── settings.json                 # Configuraciones específicas
│   └── defaults/
│       └── config_default.json       # Configuración por defecto
│
├── data/                             # Datos, base de datos y logs
│   ├── schema.sql                    # Esquema de base de datos
│   ├── turnos.db                     # Base de datos SQLite
│   ├── admin_notifications.json      # Log notificaciones admin
│   ├── notifications_log.json        # Log notificaciones usuarios
│   └── logs/                         # Logs del sistema
│       ├── app.log
│       ├── error.log
│       └── access.log
│
├── web/                              # Frontend y assets
│   ├── templates/                    # Templates HTML
│   │   ├── admin_panel.html
│   │   └── admin_panel_mobile.html
│   └── static/                       # Assets estáticos
│       ├── css/
│       │   └── admin.css
│       ├── js/
│       │   └── admin.js
│       ├── images/
│       │   └── icon-192.png
│       ├── manifest.json             # PWA manifest
│       └── sw.js                     # Service Worker
│
├── docs/                             # Documentación
│   ├── README.md                     # Documentación principal
│   ├── DEPLOY_GUIA.md               # Guía de despliegue
│   ├── VARIABLES_ENTORNO.md         # Variables de entorno
│   ├── WEBHOOK_RAILWAY_GUIA.md      # Configuración webhook
│   ├── ARQUITECTURA_MULTI_CLIENTE.md # Arquitectura multi-cliente
│   ├── CLIENTE_NUEVO_GUIA.md        # Guía nuevo cliente
│   └── examples/                     # Ejemplos
│       ├── config_ejemplo.json
│       └── webhook_test.py
│
└── tests/                            # Tests (futuro)
    ├── __init__.py
    ├── test_bot_core.py
    ├── test_whatsapp.py
    └── test_admin.py
```

## 🗂️ CATEGORIZACIÓN DE ARCHIVOS

### **ARCHIVOS .JSON POR CATEGORÍA:**

#### 🔧 **Configuración de Sistema (Raíz y config/)**
```bash
railway.json                    # ← RAÍZ (Railway lo busca aquí)
config/config.json             # ← Configuración del sistema
config/settings.json           # ← Configuraciones específicas
config/defaults/config_default.json # ← Valores por defecto
```

#### 📊 **Datos y Logs (data/)**
```bash
data/admin_notifications.json  # ← Log notificaciones admin
data/notifications_log.json    # ← Log notificaciones usuarios
```

#### 📱 **PWA y Frontend (web/static/)**
```bash
web/static/manifest.json       # ← PWA manifest
web/static/package.json        # ← Si tienes dependencias frontend
```

### **ARCHIVOS .SH POR FUNCIÓN:**

#### 🔍 **Scripts de Verificación**
```bash
scripts/check_nuevo_cliente.sh    # ← Verificar config cliente
scripts/check_deploy_ready.sh     # ← Verificar antes deploy
```

#### ⚙️ **Scripts de Instalación y Setup**
```bash
scripts/setup.sh                  # ← Instalación inicial
scripts/migrate.sh                # ← Migrar a nueva estructura
```

#### 🔧 **Scripts de Mantenimiento**
```bash
scripts/backup.sh                 # ← Backup automático
scripts/maintenance.sh            # ← Mantenimiento manual
```

## 🚀 SCRIPT DE MIGRACIÓN

### Crear script para migrar automáticamente:
```bash
#!/bin/bash
# scripts/migrate.sh - Migrar a nueva estructura

echo "🚀 Migrando proyecto a nueva estructura..."

# Crear directorios
mkdir -p src/{core,bots/senders,admin,services,utils}
mkdir -p scripts config/defaults data/logs web/{templates,static/{css,js,images}}
mkdir -p docs/examples tests

# Mover archivos Python
mv bot_core.py src/core/
mv bot_config.py src/core/config.py
mv database.py src/core/
mv bot_whatsapp.py src/bots/whatsapp_bot.py
mv bot_telegram.py src/bots/telegram_bot.py
mv whatsapp_sender.py src/bots/senders/
mv bot_sender.py src/bots/senders/
mv admin_panel.py src/admin/panel.py
mv admin_notifications.py src/admin/notifications.py
mv daemon_notificaciones.py src/services/daemon.py
mv notifications.py src/services/notifications.py
mv db_maintenance.py src/services/maintenance.py

# Mover scripts
mv *.sh scripts/ 2>/dev/null || true

# Mover datos
mv schema.sql data/
mv turnos.db data/ 2>/dev/null || true
mv *.json data/ 2>/dev/null || true

# Mover web assets
mv templates/* web/templates/ 2>/dev/null || true
mv static/* web/static/ 2>/dev/null || true

# Mover documentación
mv guias/* docs/ 2>/dev/null || true

echo "✅ Migración completada!"
```

## 📝 VENTAJAS DE LA NUEVA ESTRUCTURA

### ✅ **Organización Clara:**
- Scripts en `scripts/`
- Configuraciones en `config/`
- Datos en `data/`
- Frontend en `web/`

### ✅ **Fácil Mantenimiento:**
- Código fuente separado en `src/`
- Documentación en `docs/`
- Tests en `tests/`

### ✅ **Deploy Simplificado:**
- `railway.json` sigue en la raíz
- `main.py` sigue siendo el punto de entrada
- Railway no se ve afectado

### ✅ **Escalabilidad:**
- Fácil agregar nuevos bots
- Fácil agregar nuevos servicios
- Fácil agregar nuevas configuraciones

---

## 🎯 RESPUESTA DIRECTA

**Los archivos .sh van en `scripts/` y los .json se distribuyen según su función:**

- **`railway.json`** → Raíz (Railway lo busca ahí)
- **`config.json`** → `config/` (configuraciones)
- **`manifest.json`** → `web/static/` (PWA)
- **`notifications.json`** → `data/` (datos/logs)
- **Scripts `.sh`** → `scripts/` (todos juntos)

**¿Quieres que implemente esta migración?**
