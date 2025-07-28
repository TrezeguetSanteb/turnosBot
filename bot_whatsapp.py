#!/usr/bin/env python3
"""
Bot de WhatsApp para el sistema de turnos.
Usa la API de Meta y la configuración centralizada.
"""

import os
from flask import Flask, request, jsonify
import json
import logging
from bot_core import handle_message, user_states, user_data
from bot_config import config
# Importar el gestor de base de datos (se inicializa automáticamente)
from database import db_manager

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Verificar configuración de WhatsApp
if not config.has_whatsapp():
    raise ValueError("WhatsApp no está configurado. Verifica el archivo .env")

whatsapp_config = config.get_whatsapp_config()

# La base de datos se inicializa automáticamente al importar database.db_manager
logger.info("Base de datos inicializada automáticamente")


@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verificación del webhook de WhatsApp"""
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    # Token de verificación desde variable de entorno directamente
    expected_token = os.environ.get(
        'WHATSAPP_VERIFY_TOKEN', 'mi_token_verificacion_whatsapp')

    if verify_token == expected_token:
        logger.info("Webhook verificado exitosamente")
        return challenge
    else:
        logger.error(
            f"Token de verificación inválido. Esperado: {expected_token}, Recibido: {verify_token}")
        return "Error de verificación", 403


@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Webhook para recibir mensajes de WhatsApp"""
    try:
        data = request.get_json()
        logger.info(f"Webhook recibido: {json.dumps(data, indent=2)}")

        # Verificar que es un mensaje
        if (data.get('object') == 'whatsapp_business_account' and
            data.get('entry') and
                len(data['entry']) > 0):

            entry = data['entry'][0]
            if 'changes' in entry and len(entry['changes']) > 0:
                change = entry['changes'][0]

                if change.get('field') == 'messages' and 'value' in change:
                    value = change['value']

                    # Procesar mensajes
                    if 'messages' in value and len(value['messages']) > 0:
                        message = value['messages'][0]

                        # Extraer datos del mensaje
                        from_number = message.get('from', '')
                        message_text = ''

                        if message.get('type') == 'text':
                            message_text = message.get(
                                'text', {}).get('body', '')

                        if from_number and message_text:
                            logger.info(
                                f"Mensaje de {from_number}: {message_text}")

                            # Procesar el mensaje usando bot_core
                            logger.info("Procesando mensaje con bot_core...")
                            respuesta = handle_message(
                                message_text,
                                from_number,
                                user_states,
                                user_data
                            )
                            logger.info(f"Respuesta generada: {respuesta}")

                            # Enviar respuesta
                            if respuesta:
                                logger.info("Enviando respuesta...")
                                success = send_whatsapp_response(
                                    from_number, respuesta)
                                if success:
                                    logger.info(
                                        f"Respuesta enviada a {from_number}")
                                else:
                                    logger.error(
                                        f"Error enviando respuesta a {from_number}")
                            else:
                                logger.warning("No se generó respuesta")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def send_whatsapp_response(to_number, message):
    """Envía una respuesta por WhatsApp"""
    try:
        logger.info(f"Intentando enviar respuesta a {to_number}")
        logger.info(f"Mensaje a enviar: {message}")

        from whatsapp_sender import whatsapp_sender

        if whatsapp_sender:
            logger.info("WhatsApp sender está disponible, enviando mensaje...")
            result = whatsapp_sender.send_message(to_number, message)
            logger.info(f"Resultado del envío: {result}")
            return result
        else:
            logger.error("WhatsApp sender no está disponible")
            return False

    except Exception as e:
        logger.error(f"Error enviando respuesta WhatsApp: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'ok',
        'service': 'whatsapp-bot',
        'whatsapp_configured': config.has_whatsapp()
    })


if __name__ == '__main__':
    logger.info("Iniciando bot de WhatsApp...")
    logger.info(f"WhatsApp configurado: {config.has_whatsapp()}")

    if config.has_whatsapp():
        wconfig = config.get_whatsapp_config()
        logger.info(f"Phone Number ID: {wconfig['phone_number_id']}")

    app.run(host='0.0.0.0', port=5001, debug=True)
