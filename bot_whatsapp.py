import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import sqlite3
import re
from bot_core import handle_message, user_states, user_data, cargar_config

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

DB_PATH = 'turnos.db'

# Inicializar la base de datos si no existe


def init_db():
    if not os.path.exists(DB_PATH):
        with open('schema.sql', 'r') as f:
            schema = f.read()
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(schema)
        conn.close()


init_db()

# Configuración de horarios (leer desde archivo si existe)
CONFIG_PATH = 'config.json'


@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    resp = MessagingResponse()
    msg = resp.message()

    respuesta = handle_message(
        incoming_msg, from_number, user_states, user_data)
    msg.body(respuesta.replace('\n', ' '))
    return str(resp)


if __name__ == '__main__':
    app.run(debug=True)
