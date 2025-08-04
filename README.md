# 🤖 TurnosBot - Sistema de Gestión de Turnos Automatizado

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![WhatsApp API](https://img.shields.io/badge/WhatsApp-Business%20API-25D366.svg)](https://developers.facebook.com/docs/whatsapp)
[![Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet.svg)](https://railway.app)
[![PWA](https://img.shields.io/badge/PWA-Ready-orange.svg)](https://web.dev/progressive-web-apps/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Sistema completo de gestión de turnos con bot de WhatsApp, panel web responsivo y notificaciones push en tiempo real.

## 🎯 Descripción del Proyecto

**TurnosBot** es una solución integral para la automatización de reservas de turnos que combina:
- **Bot conversacional de WhatsApp** para reservas 24/7
- **Panel de administración web** responsivo y optimizado para móviles
- **Sistema de notificaciones push** en tiempo real
- **Arquitectura escalable** desplegada en Railway

### 🏆 Destacado para CV
- **Arquitectura Full-Stack** completa con backend, frontend y base de datos
- **Integración con APIs externas** (WhatsApp Business API de Meta)
- **Sistema de notificaciones en tiempo real** usando Server-Sent Events (SSE)
- **Progressive Web App (PWA)** con capacidades nativas
- **Deploy en la nube** con optimizaciones de costos
- **Código limpio y documentado** siguiendo mejores prácticas

## ✨ Características Principales

### 🤖 Bot de WhatsApp Inteligente
- ✅ **Conversación natural** con flujo guiado
- ✅ **Reservas automáticas** 24/7 sin intervención humana
- ✅ **Validación inteligente** de horarios y disponibilidad
- ✅ **Confirmaciones instantáneas** y gestión de cancelaciones
- ✅ **Manejo de estados** persistente por usuario

### 📱 Panel de Administración Moderno
- ✅ **Interfaz responsiva** optimizada para móviles
- ✅ **Vista de calendario** semanal interactiva
- ✅ **Gestión completa de turnos** (crear, modificar, cancelar)
- ✅ **Configuración flexible** de horarios por día
- ✅ **Bloqueo de días** específicos (feriados, vacaciones)

### 🔔 Sistema de Notificaciones Avanzado
- ✅ **Notificaciones push** nativas del navegador
- ✅ **Actualizaciones en tiempo real** via Server-Sent Events
- ✅ **Badge de contador** para notificaciones pendientes
- ✅ **Panel deslizante** con historial completo
- ✅ **Fallback inteligente** (SSE → Polling si es necesario)

### ⚡ Optimizaciones de Rendimiento
- ✅ **Sleep/Idle optimization** para reducir costos en Railway
- ✅ **Monitor inteligente** con intervalos adaptativos
- ✅ **Caché y optimizaciones** para mejor UX
- ✅ **Progressive Web App** con service worker

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.12+** - Lenguaje principal
- **Flask** - Framework web minimalista y eficiente
- **SQLite** - Base de datos embebida (fácil deploy)
- **WhatsApp Business API** - Integración con Meta
- **Server-Sent Events** - Comunicación en tiempo real

### Frontend
- **HTML5** + **CSS3** + **JavaScript ES6+**
- **Progressive Web App** (PWA) con manifest y service worker
- **Responsive Design** - Mobile-first approach
- **Push Notifications API** - Notificaciones nativas
- **LocalStorage** - Persistencia client-side

### DevOps & Deploy
- **Railway** - Plataforma cloud para deploy
- **Git** - Control de versiones
- **GitHub** - Repositorio y CI/CD
- **Environment Variables** - Configuración segura

### APIs & Integraciones
- **Meta WhatsApp Business API** - Mensajería
- **Webhook handling** - Eventos en tiempo real
- **REST API** - Endpoints para el frontend
- **JSON** - Intercambio de datos

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     TURNOSBOT ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  👤 USUARIO          📱 WHATSAPP BOT      🌐 ADMIN PANEL   │
│      │                      │                    │          │
│      │ "Hola"              │                    │          │
│      │────────────────────▶│                    │          │
│      │                     │                    │          │
│      │ Menu + Opciones     │                    │          │
│      │◀────────────────────│                    │          │
│      │                     │                    │          │
│      │ Datos del turno     │                    │          │
│      │────────────────────▶│                    │          │
│      │                     │                    │          │
│      │                     ▼                    │          │
│      │            ┌─────────────────┐           │          │
│      │            │  CORE SYSTEM    │           │          │
│      │            │                 │           │          │
│      │            │ • bot_core.py   │           │          │
│      │            │ • database.py   │           │          │
│      │            │ • config.py     │           │          │
│      │            │                 │           │          │
│      │            └─────────────────┘           │          │
│      │                     │                    │          │
│      │                     ▼                    │          │
│      │            ┌─────────────────┐           │          │
│      │            │   SQLite DB     │           │          │
│      │            │                 │           │          │
│      │            │ • turnos        │           │          │
│      │            │ • horarios      │           │          │
│      │            │ • config        │           │          │
│      │            │                 │           │          │
│      │            └─────────────────┘           │          │
│      │                     │                    │          │
│      │                     │    ┌───────────────┼──────────┤
│      │                     │    │ NOTIFICATIONS │          │
│      │                     │    │               │          │
│      │                     │    │ • admin_notifications.json│
│      │                     │    │ • SSE Stream  │          │
│      │                     │    │ • Push API    │          │
│      │                     │    │               │          │
│      │                     │    └───────────────┼──────────┤
│      │                     │                    │          │
│      │ Confirmación        │                    │          │
│      │◀────────────────────┼────────────────────┼──────────┤
│                            │                    │          │
│                            │      🔔 Notif      │          │
│                            └───────────────────▶│          │
│                                                 │          │
│                                    📊 Dashboard │          │
│                                                 ▼          │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Funcionalidades Detalladas

### 🤖 Bot de WhatsApp

#### Flujo de Conversación
1. **Saludo inicial** → Menú de opciones
2. **Pedir turno** → Solicitar nombre
3. **Seleccionar fecha** → Mostrar domingos disponibles
4. **Elegir horario** → Horarios libres del día
5. **Confirmación** → Turno reservado + notificación al admin

#### Características Técnicas
- **Estado persistente** por usuario
- **Validación de horarios** en tiempo real
- **Manejo de errores** robusto
- **Limpieza automática** de estados huérfanos
- **Logs detallados** para debugging

### 📱 Panel de Administración

#### Vista Principal
- **Calendario semanal** con turnos visualizados
- **Información completa** de cada reserva
- **Navegación rápida** entre semanas
- **Responsive design** para todos los dispositivos

#### Gestión de Turnos
- **Crear turnos** manualmente si es necesario
- **Cancelar reservas** con un clic
- **Ver detalles** completos del cliente

### 🔔 Sistema de Notificaciones

#### Tecnologías Implementadas
- **Server-Sent Events (SSE)** - Tiempo real
- **Push Notifications API** - Notificaciones nativas
- **Fallback a Polling** - Compatibilidad universal
- **Service Worker** - Funciona con app cerrada

#### Tipos de Notificaciones
- 📅 **Nuevo turno** reservado
- ❌ **Cancelación** de turno
- 🚫 **Día bloqueado** por admin
- ✅ **Día desbloqueado** 
- ⚠️ **Errores del sistema**

## 👨‍💻 Autor

**Santiago Trezeguet**

### ⭐ Si te gustó este proyecto, dale una estrella!

**Construido con ❤️ usando Python, Flask y WhatsApp API**

