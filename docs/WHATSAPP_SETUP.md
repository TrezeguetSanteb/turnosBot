# Configuración de WhatsApp Business API

## Estado Actual ✅

El sistema ya está **completamente configurado** y funcionando para WhatsApp. Solo necesitas configurar los números permitidos en Meta.

## Configuración en Meta Developers

### 1. Agregar Números de Prueba

1. Ve a [Meta Developers Console](https://developers.facebook.com/)
2. Selecciona tu aplicación de WhatsApp
3. Ve a **WhatsApp > Getting Started**
4. En la sección **"To"**, agrega los números que quieres probar
5. Formato: `+541234567890` (con código de país)

### 2. Webhook Configuration

Cuando tengas tu servidor público, configura el webhook:

- **URL**: `https://tu-dominio.com/webhook`
- **Verify Token**: `mi_token_verificacion_whatsapp`

### 3. Variables de Entorno (Ya configuradas ✅)

```bash
# WhatsApp Bot (Meta API)
WHATSAPP_ACCESS_TOKEN='EAAKmZByaebTYBPGfq93...'
WHATSAPP_PHONE_NUMBER_ID='748643838326451'
WHATSAPP_BUSINESS_ACCOUNT_ID='1145144844304025'
```

## Pruebas

### Envío Manual de Notificaciones
```bash
python bot_sender.py
```

### Bot Interactivo de WhatsApp
```bash
python bot_whatsapp.py
```

### Daemon Automático (ya corriendo ✅)
```bash
python daemon_notificaciones.py
```

## Funcionalidades Implementadas ✅

- ✅ **Sistema universal**: Funciona con Telegram y WhatsApp automáticamente
- ✅ **Configuración centralizada**: Solo cambias `.env`
- ✅ **Envío automático**: Al cancelar turnos desde el panel admin
- ✅ **Múltiples canales**: Detecta automáticamente qué canal usar por número
- ✅ **Rate limiting**: Respeta límites de API
- ✅ **Logging completo**: Logs detallados de todos los envíos
- ✅ **Error handling**: Manejo robusto de errores

## Detección Automática de Canales

El sistema detecta automáticamente qué canal usar:

- **Telegram**: Números que son solo dígitos (chat IDs)
- **WhatsApp**: Números que empiezan con `+54` o `54` (números reales)

## Próximos Pasos

1. **Agregar tu número** a la lista de destinatarios en Meta Console
2. **Probar envío** con tu número real
3. **Configurar webhook** cuando tengas dominio público
4. **Solicitar revisión** para producción cuando esté listo
