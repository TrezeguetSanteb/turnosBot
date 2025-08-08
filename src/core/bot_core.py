"""
Bot Core - Lógica principal del bot de turnos con múltiples profesionales
"""
import os
import sqlite3
import json
from datetime import datetime, timedelta
import re


# Estados de conversación
user_states = {}
user_data = {}

# Estados posibles
STATE_GREETING = 'greeting'
STATE_WAITING_DATE = 'waiting_date'
STATE_WAITING_TIME = 'waiting_time'
STATE_WAITING_PROFESSIONAL = 'waiting_professional'
STATE_WAITING_NAME = 'waiting_name'
STATE_CONFIRMING = 'confirming'
STATE_MENU = 'menu'
STATE_CANCELING = 'canceling'


def get_db_connection():
    """Obtener conexión a la base de datos"""
    project_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..'))
    db_path = os.path.join(project_root, 'data', 'turnos.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def obtener_profesionales_activos():
    """Obtener lista de profesionales activos"""
    try:
        conn = get_db_connection()
        profesionales = conn.execute('''
            SELECT id, nombre, color FROM profesionales 
            WHERE activo = 1 
            ORDER BY orden, nombre
        ''').fetchall()
        conn.close()

        return [dict(p) for p in profesionales]
    except Exception as e:
        print(f"Error obteniendo profesionales: {e}")
        return [{"id": 1, "nombre": "Martín", "color": "#e74c3c"}]


def obtener_profesionales_disponibles_fecha_hora(fecha, hora):
    """Obtener profesionales disponibles para una fecha/hora específica"""
    try:
        conn = get_db_connection()

        # Obtener profesionales que ya tienen turno en ese horario
        ocupados = conn.execute('''
            SELECT profesional_id FROM turnos 
            WHERE fecha = ? AND hora = ?
        ''', (fecha, hora)).fetchall()

        ocupados_ids = [o['profesional_id'] for o in ocupados]

        # Obtener todos los profesionales activos
        profesionales = conn.execute('''
            SELECT id, nombre, color FROM profesionales 
            WHERE activo = 1 AND id NOT IN ({})
            ORDER BY orden, nombre
        '''.format(','.join('?' * len(ocupados_ids)) if ocupados_ids else '0'), ocupados_ids).fetchall()

        conn.close()

        return [dict(p) for p in profesionales]

    except Exception as e:
        print(f"Error obteniendo disponibles: {e}")
        return obtener_profesionales_activos()


def crear_turno(fecha, hora, nombre, telefono, profesional_id):
    """Crear un nuevo turno"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO turnos (fecha, hora, nombre, telefono, profesional_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (fecha, hora, nombre, telefono, profesional_id))

        turno_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return turno_id

    except Exception as e:
        print(f"Error creando turno: {e}")
        return None


def obtener_turnos_usuario(telefono):
    """Obtener turnos de un usuario"""
    try:
        conn = get_db_connection()
        turnos = conn.execute('''
            SELECT t.id, t.fecha, t.hora, t.nombre, p.nombre as profesional_nombre
            FROM turnos t
            LEFT JOIN profesionales p ON t.profesional_id = p.id
            WHERE t.telefono = ? AND t.fecha >= ?
            ORDER BY t.fecha, t.hora
        ''', (telefono, datetime.now().strftime('%Y-%m-%d'))).fetchall()

        conn.close()

        return [dict(t) for t in turnos]

    except Exception as e:
        print(f"Error obteniendo turnos: {e}")
        return []


def cancelar_turno(turno_id, telefono):
    """Cancelar un turno del usuario"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            DELETE FROM turnos 
            WHERE id = ? AND telefono = ?
        ''', (turno_id, telefono))

        rows_deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_deleted > 0

    except Exception as e:
        print(f"Error cancelando turno: {e}")
        return False


def generar_horarios_disponibles(fecha):
    """Generar horarios disponibles para una fecha"""
    try:
        # Obtener configuración de horarios (simplificado por ahora)
        horarios_mañana = []
        horarios_tarde = []

        # Mañana: 8:00 a 12:00
        for hour in range(8, 12):
            for minute in [0, 30]:
                hora = f"{hour:02d}:{minute:02d}"
                horarios_mañana.append(hora)

        # Tarde: 15:00 a 18:00
        for hour in range(15, 18):
            for minute in [0, 30]:
                hora = f"{hour:02d}:{minute:02d}"
                horarios_tarde.append(hora)

        return horarios_mañana + horarios_tarde

    except Exception as e:
        print(f"Error generando horarios: {e}")
        return ["09:00", "10:00", "16:00", "17:00"]  # Fallback


def validar_fecha(fecha_str):
    """Validar y parsear fecha en formato DD/MM o DD/MM/YYYY"""
    try:
        # Intentar diferentes formatos
        fecha_patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%d/%m/%Y'),  # DD/MM/YYYY
            (r'(\d{1,2})/(\d{1,2})', '%d/%m'),  # DD/MM (año actual)
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', '%d-%m-%Y'),  # DD-MM-YYYY
            (r'(\d{1,2})-(\d{1,2})', '%d-%m'),  # DD-MM (año actual)
        ]

        for pattern, format_str in fecha_patterns:
            match = re.match(pattern, fecha_str.strip())
            if match:
                if '%Y' in format_str:
                    fecha = datetime.strptime(
                        fecha_str.strip(), format_str).date()
                else:
                    # Agregar año actual
                    fecha = datetime.strptime(
                        f"{fecha_str.strip()}/{datetime.now().year}", f"{format_str}/%Y").date()

                # Validar que no sea una fecha pasada
                if fecha < datetime.now().date():
                    return None, "La fecha no puede ser anterior a hoy."

                # Validar que esté dentro de los próximos 60 días
                limite = datetime.now().date() + timedelta(days=60)
                if fecha > limite:
                    return None, "Solo puedes reservar turnos hasta 2 meses adelante."

                return fecha, None

        return None, "Formato de fecha inválido. Usa DD/MM o DD/MM/YYYY."

    except Exception as e:
        return None, "Error al procesar la fecha."


def validar_hora(hora_str):
    """Validar formato de hora"""
    try:
        # Intentar diferentes formatos
        hora_patterns = [
            r'(\d{1,2}):(\d{2})',  # HH:MM
            r'(\d{1,2})\.(\d{2})',  # HH.MM
            r'(\d{1,2})',  # HH (agregar :00)
        ]

        for pattern in hora_patterns:
            match = re.match(pattern, hora_str.strip())
            if match:
                if len(match.groups()) == 2:
                    hour, minute = match.groups()
                else:
                    hour = match.group(1)
                    minute = "00"

                hour = int(hour)
                minute = int(minute)

                # Validar rangos
                if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                    return None, "Hora inválida."

                return f"{hour:02d}:{minute:02d}", None

        return None, "Formato de hora inválido. Usa HH:MM."

    except Exception as e:
        return None, "Error al procesar la hora."


def handle_message(message, phone_number, states, data):
    """
    Manejar mensaje del usuario
    """
    message = message.strip().lower()
    phone_number = phone_number.strip()

    # Obtener estado actual del usuario
    current_state = states.get(phone_number, STATE_GREETING)
    user_info = data.get(phone_number, {})

    try:
        if current_state == STATE_GREETING or message in ['hola', 'menu', 'inicio']:
            return handle_greeting(phone_number, states, data)

        elif current_state == STATE_MENU:
            return handle_menu_selection(message, phone_number, states, data)

        elif current_state == STATE_WAITING_DATE:
            return handle_date_input(message, phone_number, states, data)

        elif current_state == STATE_WAITING_TIME:
            return handle_time_input(message, phone_number, states, data)

        elif current_state == STATE_WAITING_PROFESSIONAL:
            return handle_professional_selection(message, phone_number, states, data)

        elif current_state == STATE_WAITING_NAME:
            return handle_name_input(message, phone_number, states, data)

        elif current_state == STATE_CONFIRMING:
            return handle_confirmation(message, phone_number, states, data)

        elif current_state == STATE_CANCELING:
            return handle_cancellation(message, phone_number, states, data)

        else:
            # Estado desconocido, reiniciar
            return handle_greeting(phone_number, states, data)

    except Exception as e:
        print(f"Error en handle_message: {e}")
        # Reiniciar conversación en caso de error
        states[phone_number] = STATE_GREETING
        data[phone_number] = {}
        return "❌ Ocurrió un error. Escribe *hola* para comenzar de nuevo."


def handle_greeting(phone_number, states, data):
    """Manejar saludo inicial y mostrar menú"""
    states[phone_number] = STATE_MENU
    data[phone_number] = {}

    menu = """
🦷 *¡Hola! Bienvenido al sistema de turnos.*

¿Qué deseas hacer?

*1️⃣* - Reservar un turno
*2️⃣* - Ver mis turnos
*3️⃣* - Cancelar un turno

Responde con el número de opción.
    """.strip()

    return menu


def handle_menu_selection(message, phone_number, states, data):
    """Manejar selección del menú principal"""
    if message in ['1', 'reservar', 'turno', 'nuevo']:
        states[phone_number] = STATE_WAITING_DATE
        return "📅 *Perfecto! Vamos a reservar tu turno.*\n\n¿Para qué fecha lo necesitas?\nPor favor envía la fecha en formato DD/MM (ejemplo: 15/03)"

    elif message in ['2', 'ver', 'mis turnos', 'turnos']:
        turnos = obtener_turnos_usuario(phone_number)

        if not turnos:
            states[phone_number] = STATE_MENU
            return "📋 *No tienes turnos reservados.*\n\nEscribe *menu* para ver las opciones disponibles."

        respuesta = "📋 *Tus turnos reservados:*\n\n"
        for turno in turnos:
            fecha_formateada = datetime.strptime(
                turno['fecha'], '%Y-%m-%d').strftime('%d/%m/%Y')
            profesional = turno['profesional_nombre'] or 'Sin asignar'
            respuesta += f"🗓️ {fecha_formateada} a las {turno['hora']}\n"
            respuesta += f"👤 Con: {profesional}\n"
            respuesta += f"📝 ID: {turno['id']}\n\n"

        states[phone_number] = STATE_MENU
        respuesta += "Escribe *menu* para ver más opciones."
        return respuesta

    elif message in ['3', 'cancelar']:
        turnos = obtener_turnos_usuario(phone_number)

        if not turnos:
            states[phone_number] = STATE_MENU
            return "📋 *No tienes turnos para cancelar.*\n\nEscribe *menu* para ver las opciones disponibles."

        data[phone_number]['cancelar_turnos'] = turnos
        states[phone_number] = STATE_CANCELING

        respuesta = "❌ *¿Qué turno deseas cancelar?*\n\n"
        for i, turno in enumerate(turnos, 1):
            fecha_formateada = datetime.strptime(
                turno['fecha'], '%Y-%m-%d').strftime('%d/%m/%Y')
            profesional = turno['profesional_nombre'] or 'Sin asignar'
            respuesta += f"*{i}* - {fecha_formateada} a las {turno['hora']} (Con: {profesional})\n"

        respuesta += "\nResponde con el número del turno a cancelar."
        return respuesta

    else:
        return "❌ Opción no válida. Por favor responde:\n*1* - Reservar turno\n*2* - Ver turnos\n*3* - Cancelar turno"


def handle_date_input(message, phone_number, states, data):
    """Manejar entrada de fecha"""
    fecha, error = validar_fecha(message)

    if error:
        return f"❌ {error}\n\nIntenta nuevamente con formato DD/MM (ejemplo: 15/03)"

    data[phone_number]['fecha'] = fecha.strftime('%Y-%m-%d')
    data[phone_number]['fecha_mostrar'] = fecha.strftime('%d/%m/%Y')

    # Generar horarios disponibles
    horarios = generar_horarios_disponibles(fecha.strftime('%Y-%m-%d'))

    if not horarios:
        return f"❌ No hay horarios disponibles para el {fecha.strftime('%d/%m/%Y')}.\n\nPrueba con otra fecha."

    states[phone_number] = STATE_WAITING_TIME

    # Mostrar horarios agrupados
    respuesta = f"⏰ *Horarios disponibles para {fecha.strftime('%d/%m/%Y')}:*\n\n"
    respuesta += "*Mañana:*\n"

    mañana = [h for h in horarios if int(h.split(':')[0]) < 14]
    tarde = [h for h in horarios if int(h.split(':')[0]) >= 14]

    if mañana:
        for hora in mañana:
            respuesta += f"🌅 {hora}\n"
    else:
        respuesta += "Sin horarios disponibles\n"

    respuesta += "\n*Tarde:*\n"

    if tarde:
        for hora in tarde:
            respuesta += f"🌆 {hora}\n"
    else:
        respuesta += "Sin horarios disponibles\n"

    respuesta += "\n¿A qué hora te gustaría el turno? (ejemplo: 10:30)"

    return respuesta


def handle_time_input(message, phone_number, states, data):
    """Manejar entrada de hora"""
    hora, error = validar_hora(message)

    if error:
        return f"❌ {error}\n\nIntenta nuevamente (ejemplo: 10:30)"

    fecha = data[phone_number]['fecha']

    # Verificar que la hora esté disponible
    horarios_disponibles = generar_horarios_disponibles(fecha)

    if hora not in horarios_disponibles:
        return f"❌ La hora {hora} no está disponible.\n\nPor favor elige una de las horas mostradas anteriormente."

    data[phone_number]['hora'] = hora

    # Obtener profesionales disponibles para esta fecha/hora
    profesionales = obtener_profesionales_disponibles_fecha_hora(fecha, hora)

    if not profesionales:
        return f"❌ No hay profesionales disponibles para {data[phone_number]['fecha_mostrar']} a las {hora}.\n\nPrueba con otro horario escribiendo *menu*."

    if len(profesionales) == 1:
        # Solo hay un profesional disponible, asignarlo automáticamente
        data[phone_number]['profesional_id'] = profesionales[0]['id']
        data[phone_number]['profesional_nombre'] = profesionales[0]['nombre']
        states[phone_number] = STATE_WAITING_NAME

        return f"👤 *Profesional asignado:* {profesionales[0]['nombre']}\n\n¿Cuál es tu nombre completo?"

    # Hay múltiples profesionales, permitir elegir
    data[phone_number]['profesionales_disponibles'] = profesionales
    states[phone_number] = STATE_WAITING_PROFESSIONAL

    respuesta = f"👥 *Hay varios profesionales disponibles para {data[phone_number]['fecha_mostrar']} a las {hora}:*\n\n"

    for i, prof in enumerate(profesionales, 1):
        respuesta += f"*{i}* - {prof['nombre']}\n"

    respuesta += "\n¿Con quién te gustaría reservar? Responde con el número."

    return respuesta


def handle_professional_selection(message, phone_number, states, data):
    """Manejar selección de profesional"""
    try:
        seleccion = int(message.strip())
        profesionales = data[phone_number].get('profesionales_disponibles', [])

        if 1 <= seleccion <= len(profesionales):
            profesional = profesionales[seleccion - 1]
            data[phone_number]['profesional_id'] = profesional['id']
            data[phone_number]['profesional_nombre'] = profesional['nombre']

            states[phone_number] = STATE_WAITING_NAME

            return f"👤 *Perfecto! Has elegido a {profesional['nombre']}*\n\n¿Cuál es tu nombre completo?"
        else:
            return f"❌ Opción inválida. Por favor responde con un número del 1 al {len(profesionales)}."

    except ValueError:
        profesionales = data[phone_number].get('profesionales_disponibles', [])
        return f"❌ Por favor responde con un número del 1 al {len(profesionales)}."


def handle_name_input(message, phone_number, states, data):
    """Manejar entrada del nombre"""
    nombre = message.strip().title()

    if len(nombre) < 2:
        return "❌ Por favor ingresa un nombre válido."

    data[phone_number]['nombre'] = nombre
    states[phone_number] = STATE_CONFIRMING

    # Mostrar resumen para confirmar
    fecha_mostrar = data[phone_number]['fecha_mostrar']
    hora = data[phone_number]['hora']
    profesional = data[phone_number]['profesional_nombre']

    respuesta = f"""
📋 *Confirma tu turno:*

📅 Fecha: {fecha_mostrar}
⏰ Hora: {hora}
👤 Profesional: {profesional}
🙋‍♂️ Nombre: {nombre}

¿Está todo correcto?
Responde *SÍ* para confirmar o *NO* para cancelar.
    """.strip()

    return respuesta


def handle_confirmation(message, phone_number, states, data):
    """Manejar confirmación del turno"""
    if message in ['si', 'sí', 'yes', 'ok', 'confirmar', 'confirmo']:
        # Crear el turno
        turno_id = crear_turno(
            data[phone_number]['fecha'],
            data[phone_number]['hora'],
            data[phone_number]['nombre'],
            phone_number,
            data[phone_number]['profesional_id']
        )

        if turno_id:
            # Limpiar datos del usuario
            states[phone_number] = STATE_MENU

            fecha_mostrar = data[phone_number]['fecha_mostrar']
            hora = data[phone_number]['hora']
            profesional = data[phone_number]['profesional_nombre']
            nombre = data[phone_number]['nombre']

            data[phone_number] = {}  # Limpiar datos

            respuesta = f"""
✅ *¡Turno confirmado!*

📅 Fecha: {fecha_mostrar}
⏰ Hora: {hora}
👤 Profesional: {profesional}
🙋‍♂️ Nombre: {nombre}
🆔 ID del turno: {turno_id}

📝 *Recordatorio importante:*
• Llega 5 minutos antes
• Si no puedes asistir, cancela con anticipación

Escribe *menu* para más opciones.
            """.strip()

            return respuesta
        else:
            states[phone_number] = STATE_MENU
            data[phone_number] = {}
            return "❌ Error al crear el turno. Por favor intenta nuevamente escribiendo *menu*."

    elif message in ['no', 'cancelar', 'cancel']:
        states[phone_number] = STATE_MENU
        data[phone_number] = {}
        return "❌ Turno cancelado.\n\nEscribe *menu* si deseas hacer otra consulta."

    else:
        return "❌ Por favor responde *SÍ* para confirmar o *NO* para cancelar."


def handle_cancellation(message, phone_number, states, data):
    """Manejar cancelación de turno"""
    try:
        seleccion = int(message.strip())
        turnos = data[phone_number].get('cancelar_turnos', [])

        if 1 <= seleccion <= len(turnos):
            turno = turnos[seleccion - 1]

            if cancelar_turno(turno['id'], phone_number):
                states[phone_number] = STATE_MENU
                data[phone_number] = {}

                fecha_formateada = datetime.strptime(
                    turno['fecha'], '%Y-%m-%d').strftime('%d/%m/%Y')
                profesional = turno['profesional_nombre'] or 'Sin asignar'

                return f"""
✅ *Turno cancelado exitosamente*

📅 Fecha: {fecha_formateada}
⏰ Hora: {turno['hora']}
👤 Profesional: {profesional}

Escribe *menu* para más opciones.
                """.strip()
            else:
                return "❌ Error al cancelar el turno. Intenta nuevamente."
        else:
            return f"❌ Opción inválida. Por favor responde con un número del 1 al {len(turnos)}."

    except ValueError:
        turnos = data[phone_number].get('cancelar_turnos', [])
        return f"❌ Por favor responde con un número del 1 al {len(turnos)}."
