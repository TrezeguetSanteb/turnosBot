"""
WhatsApp Bot - Manejador de webhooks de WhatsApp
"""
from flask import Flask, request, jsonify
from datetime import datetime
import os
import json
import logging

# Crear app Flask
app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verificación del webhook de WhatsApp"""
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    expected_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mi_token_verificacion_whatsapp')

    if verify_token == expected_token:
        logger.info("✅ Webhook verificado exitosamente")
        return challenge
    else:
        logger.error(f"❌ Token de verificación incorrecto: {verify_token}")
        return "Token incorrecto", 403


@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibir mensajes de WhatsApp y procesarlos"""
    try:
        data = request.get_json()
        logger.info(f"🔍 Datos recibidos en webhook: {json.dumps(data, indent=2)}")

        if not data or 'entry' not in data:
            logger.warning("⚠️ Datos inválidos o sin 'entry'")
            return jsonify({'status': 'ok'})

        for entry in data['entry']:
            for change in entry.get('changes', []):
                if change.get('field') == 'messages':
                    value = change.get('value', {})

                    for message in value.get('messages', []):
                        phone_number = message['from']
                        message_text = message.get('text', {}).get('body', '')
                        message_id = message['id']

                        logger.info(f"📞 Mensaje de {phone_number}: '{message_text}' (ID: {message_id})")

                        # Procesar mensaje con el bot core
                        try:
                            from src.core.bot_core import handle_message, user_states, user_data
                            
                            response = handle_message(message_text, phone_number, user_states, user_data)
                            
                            if response:
                                logger.info(f"📤 Bot generó respuesta: {response}")
                                # Enviar respuesta
                                if enviar_respuesta_whatsapp(phone_number, response):
                                    logger.info(f"✅ Respuesta enviada a {phone_number}")
                                else:
                                    logger.error(f"❌ No se pudo enviar respuesta a {phone_number}")
                            else:
                                logger.warning(f"⚠️ Bot no generó respuesta para: {message_text}")

                        except Exception as e:
                            logger.error(f"❌ Error procesando mensaje: {e}")
                            import traceback
                            logger.error(f"🔍 Traceback: {traceback.format_exc()}")

        return jsonify({'status': 'ok'})

    except Exception as e:
        logger.error(f"💥 Error crítico en webhook: {e}")
        import traceback
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def enviar_respuesta_whatsapp(phone_number, message):
    """Enviar respuesta de WhatsApp"""
    try:
        import requests
        
        access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
        phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')

        if not access_token or not phone_number_id:
            logger.warning("⚠️ Variables de WhatsApp no configuradas")
            return False

        clean_number = phone_number.replace('+', '') if phone_number.startswith('+') else phone_number

        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": clean_number,
            "type": "text",
            "text": {
                "body": message
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            return True
        else:
            logger.error(f"❌ Error enviando WhatsApp: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ Error crítico enviando WhatsApp: {e}")
        return False


@app.route('/health', methods=['GET'])
def health_check():
    """Health check para el bot de WhatsApp"""
    return jsonify({
        'status': 'ok',
        'service': 'WhatsApp Bot',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080)) + 1
    app.run(host='0.0.0.0', port=port, debug=False)
