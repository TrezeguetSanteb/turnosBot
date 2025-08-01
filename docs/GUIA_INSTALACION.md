
# 📱 Guía de Instalación - Sistema de Turnos

## 🎯 URLs de Acceso

- **Panel Web (computadora)**: http://192.168.68.130:5000
- **Panel Móvil (celular)**: http://192.168.68.130:5000/mobile

## 📋 Instrucciones de Instalación

### Para el Cliente:

1. **Ejecutar el sistema**:
   ```bash
   ./start_turnos.sh
   ```

2. **Acceder desde el celular**:
   - Asegúrate de estar en la misma red WiFi
   - Abre el navegador en tu celular
   - Ve a: `http://192.168.68.130:5000/mobile`
   - O escanea el código QR generado

3. **Instalar como App**:
   - En el navegador del celular, busca "Agregar a pantalla de inicio"
   - En Chrome: Menú (⋮) → "Instalar app"
   - En Safari: Compartir → "Agregar a pantalla de inicio"

### Funcionalidades del Panel Móvil:

✅ **Ver turnos por día**
✅ **Eliminar turnos**
✅ **Configurar horarios de atención**
✅ **Bloquear/desbloquear días**
✅ **Navegación por semanas**
✅ **Actualización automática cada 30 segundos**
✅ **Funciona offline (PWA)**

## 🔧 Configuración Inicial

El sistema viene preconfigurado con:
- Horarios: 9:00 - 12:00 (mañana) y 15:00 - 18:00 (tarde)
- Intervalos de 30 minutos
- Todos los días habilitados

Puedes modificar estos horarios desde el panel móvil.

## 🚀 Distribución a Clientes

### Opción 1: Local (Recomendada)
- El cliente ejecuta el script en su computadora/servidor
- Accede desde su celular en la misma red
- Todos los datos quedan en su dispositivo

### Opción 2: Servidor en la Nube
- Subir a un VPS (DigitalOcean, AWS, etc.)
- Configurar dominio personalizado
- Acceso desde cualquier lugar

### Opción 3: Raspberry Pi
- Instalar en una Raspberry Pi
- Configurar WiFi hotspot
- Sistema completamente autónomo

## 💰 Modelo de Negocio Sugerido

1. **Pago único por licencia**: $50-100 USD
2. **Instalación incluida**: Configuración remota
3. **Soporte por 6 meses**: WhatsApp/email
4. **Actualizaciones**: Por 1 año incluidas

## 📞 Soporte al Cliente

Para soporte técnico:
- WhatsApp: [Tu número]
- Email: [Tu email]
- Telegram: [Tu usuario]

---
*Sistema desarrollado por [Tu nombre/empresa]*
