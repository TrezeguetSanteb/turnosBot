import sqlite3
import re
from datetime import datetime
import json
from bot_core import handle_message, user_states, user_data, cargar_config

DB_PATH = 'turnos.db'
CONFIG_PATH = 'config.json'


# Inicializar la base de datos si no existe
def init_db():
    import os
    if not os.path.exists(DB_PATH):
        with open('schema.sql', 'r') as f:
            schema = f.read()
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(schema)
        conn.close()


init_db()


def main():
    print('Bienvenido al bot de gestión de turnos (modo terminal). Escribe "hola" para comenzar.')
    from_number = 'terminal_user'
    while True:
        incoming_msg = input('> ').strip()
        if incoming_msg.lower() == 'salir':
            print('¡Hasta luego!')
            break
        respuesta = handle_message(
            incoming_msg, from_number, user_states, user_data)
        print(respuesta)


if __name__ == '__main__':
    main()
