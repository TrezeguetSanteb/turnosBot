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
STATE_CHOOSING_PROFESSIONAL = 'choosing_professional'
STATE_CHOOSING_DAY = 'choosing_day'
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


def generar_horarios_disponibles(fecha, profesional_id=None):
    """Generar horarios disponibles para una fecha, filtrando por profesional si se especifica"""
    try:
        # Obtener configuración de horarios (simplificado por ahora)
        horarios_base = []

        # Mañana: 8:00 a 12:00
        for hour in range(8, 12):
            for minute in [0, 30]:
                hora = f"{hour:02d}:{minute:02d}"
                horarios_base.append(hora)

        # Tarde: 15:00 a 18:00
        for hour in range(15, 18):
            for minute in [0, 30]:
                hora = f"{hour:02d}:{minute:02d}"
                horarios_base.append(hora)

        # Si no se especifica profesional, mostrar todos los horarios donde hay algún profesional disponible
        if profesional_id is None:
            horarios_disponibles = []
            for hora in horarios_base:
                profesionales_disponibles = obtener_profesionales_disponibles_fecha_hora(fecha, hora)
                if profesionales_disponibles:
                    horarios_disponibles.append(hora)
            return horarios_disponibles
        
        # Si se especifica profesional, filtrar solo horarios donde ese profesional está disponible
        else:
            conn = get_db_connection()
            ocupados = conn.execute('''
                SELECT hora FROM turnos 
                WHERE fecha = ? AND profesional_id = ?
            ''', (fecha, profesional_id)).fetchall()
            conn.close()

            horas_ocupadas = [o['hora'] for o in ocupados]
            horarios_disponibles = [h for h in horarios_base if h not in horas_ocupadas]
            return horarios_disponibles

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

        elif current_state == STATE_CHOOSING_PROFESSIONAL:
            return handle_choosing_professional(message, phone_number, states, data)

        elif current_state == STATE_CHOOSING_DAY:
            return handle_choosing_day(message, phone_number, states, data)

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
        states[phone_number] = STATE_CHOOSING_PROFESSIONAL
        
        # Obtener todos los profesionales activos
        profesionales = obtener_profesionales_activos()
        
        if not profesionales:
            states[phone_number] = STATE_MENU
            return "❌ No hay profesionales disponibles en este momento.\n\nEscribe *menu* para ver otras opciones."
        
        respuesta = "👥 *¿Con qué profesional deseas reservar tu turno?*\n\n"
        
        for i, prof in enumerate(profesionales, 1):
            respuesta += f"*{i}* - {prof['nombre']}\n"
        
        respuesta += f"*{len(profesionales) + 1}* - Cualquiera (mostrar toda la disponibilidad)\n"
        respuesta += "\nResponde con el número de tu elección."
        
        data[phone_number]['profesionales_disponibles'] = profesionales
        return respuesta

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

    # Generar horarios disponibles según el profesional elegido
    profesional_id = data[phone_number].get('profesional_id')
    horarios = generar_horarios_disponibles(fecha.strftime('%Y-%m-%d'), profesional_id)

    if not horarios:
        profesional_nombre = data[phone_number].get('profesional_nombre', '')
        if profesional_nombre == 'Cualquiera':
            return f"❌ No hay horarios disponibles para el {fecha.strftime('%d/%m/%Y')} con ningún profesional.\n\nPrueba con otra fecha."
        else:
            return f"❌ No hay horarios disponibles para el {fecha.strftime('%d/%m/%Y')} con {profesional_nombre}.\n\nPrueba con otra fecha o escribe *menu* para elegir otro profesional."

    states[phone_number] = STATE_WAITING_TIME

    # Mostrar horarios agrupados
    profesional_nombre = data[phone_number].get('profesional_nombre', '')
    if profesional_nombre == 'Cualquiera':
        respuesta = f"⏰ *Horarios disponibles para {fecha.strftime('%d/%m/%Y')} (todos los profesionales):*\n\n"
    else:
        respuesta = f"⏰ *Horarios disponibles para {fecha.strftime('%d/%m/%Y')} con {profesional_nombre}:*\n\n"

    mañana = [h for h in horarios if int(h.split(':')[0]) < 14]
    tarde = [h for h in horarios if int(h.split(':')[0]) >= 14]

    # Guardar horarios para selección numerada
    data[phone_number]['horarios_disponibles'] = horarios
    
    # Mostrar horarios como opciones numeradas
    respuesta += "📋 *Horarios disponibles:*\n\n"
    
    for i, hora in enumerate(horarios, 1):
        if profesional_nombre == 'Cualquiera':
            profs_disponibles = obtener_profesionales_disponibles_fecha_hora(fecha.strftime('%Y-%m-%d'), hora)
            nombres_profs = [p['nombre'] for p in profs_disponibles]
            respuesta += f"*{i}* - {hora} ({', '.join(nombres_profs)})\n"
        else:
            # Determinar si es mañana o tarde
            hora_num = int(hora.split(':')[0])
            emoji = "🌅" if hora_num < 14 else "🌆"
            respuesta += f"*{i}* - {emoji} {hora}\n"

    respuesta += "\nResponde con el número de tu horario preferido."

    return respuesta


def handle_time_input(message, phone_number, states, data):
    """Manejar selección numérica de hora"""
    try:
        seleccion = int(message.strip())
        horarios_disponibles = data[phone_number].get('horarios_disponibles', [])
        
        if 1 <= seleccion <= len(horarios_disponibles):
            hora = horarios_disponibles[seleccion - 1]
            data[phone_number]['hora'] = hora

            fecha = data[phone_number]['fecha']
            profesional_id = data[phone_number].get('profesional_id')
            profesional_especifico = data[phone_number].get('profesional_especifico', True)

            # Si ya se eligió un profesional específico, ir directo al nombre
            if profesional_especifico and profesional_id:
                states[phone_number] = STATE_WAITING_NAME
                profesional_nombre = data[phone_number]['profesional_nombre']
                return f"👤 *Profesional: {profesional_nombre}*\n\n¿Cuál es tu nombre completo?"

            # Si se eligió "cualquiera", mostrar profesionales disponibles para esa hora
            else:
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

                respuesta = f"👥 *Profesionales disponibles para {data[phone_number]['fecha_mostrar']} a las {hora}:*\n\n"

                for i, prof in enumerate(profesionales, 1):
                    respuesta += f"*{i}* - {prof['nombre']}\n"

                respuesta += "\n¿Con quién te gustaría reservar? Responde con el número."

                return respuesta
                
        else:
            return f"❌ Opción inválida. Por favor responde con un número del 1 al {len(horarios_disponibles)}."
            
    except ValueError:
        horarios_disponibles = data[phone_number].get('horarios_disponibles', [])
        return f"❌ Por favor responde con un número del 1 al {len(horarios_disponibles)}."


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


def handle_choosing_professional(message, phone_number, states, data):
    """Manejar selección inicial de profesional"""
    try:
        seleccion = int(message.strip())
        profesionales = data[phone_number].get('profesionales_disponibles', [])
        
        if 1 <= seleccion <= len(profesionales):
            # Usuario eligió un profesional específico
            profesional = profesionales[seleccion - 1]
            data[phone_number]['profesional_id'] = profesional['id']
            data[phone_number]['profesional_nombre'] = profesional['nombre']
            data[phone_number]['profesional_especifico'] = True
            
            states[phone_number] = STATE_CHOOSING_DAY
            return generar_opciones_dias(phone_number, data, f"👤 *Has elegido a {profesional['nombre']}*\n\n")
            
        elif seleccion == len(profesionales) + 1:
            # Usuario eligió "Cualquiera"
            data[phone_number]['profesional_especifico'] = False
            data[phone_number]['profesional_id'] = None
            data[phone_number]['profesional_nombre'] = 'Cualquiera'
            
            states[phone_number] = STATE_CHOOSING_DAY
            return generar_opciones_dias(phone_number, data, "👥 *Has elegido ver disponibilidad de todos los profesionales*\n\n")
            
        else:
            return f"❌ Opción inválida. Por favor responde con un número del 1 al {len(profesionales) + 1}."
            
    except ValueError:
        profesionales = data[phone_number].get('profesionales_disponibles', [])
        return f"❌ Por favor responde con un número del 1 al {len(profesionales) + 1}."


def generar_opciones_dias(phone_number, data, prefijo=""):
    """Generar opciones de días para reservar"""
    hoy = datetime.now().date()
    opciones = []
    
    # Generar próximos 7 días (excluyendo domingos)
    for i in range(7):
        fecha = hoy + timedelta(days=i)
        
        # Saltar domingos
        if fecha.weekday() == 6:
            continue
            
        # Formatear nombre del día
        if i == 0:
            nombre_dia = "Hoy"
        elif i == 1:
            nombre_dia = "Mañana"
        else:
            dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            nombre_dia = dias_semana[fecha.weekday()]
        
        fecha_formateada = fecha.strftime('%d/%m')
        opciones.append({
            'fecha': fecha,
            'nombre': f"{nombre_dia} ({fecha_formateada})",
            'fecha_str': fecha.strftime('%Y-%m-%d'),
            'fecha_mostrar': fecha.strftime('%d/%m/%Y')
        })
    
    # Guardar opciones para usar en la selección
    data[phone_number]['opciones_dias'] = opciones
    
    # Generar respuesta
    respuesta = f"{prefijo}📅 *¿Para qué día necesitas el turno?*\n\n"
    
    for i, opcion in enumerate(opciones, 1):
        respuesta += f"*{i}* - {opcion['nombre']}\n"
    
    respuesta += "\nResponde con el número del día."
    
    return respuesta


def handle_choosing_day(message, phone_number, states, data):
    """Manejar selección de día"""
    try:
        seleccion = int(message.strip())
        opciones = data[phone_number].get('opciones_dias', [])
        
        if 1 <= seleccion <= len(opciones):
            dia_elegido = opciones[seleccion - 1]
            
            data[phone_number]['fecha'] = dia_elegido['fecha_str']
            data[phone_number]['fecha_mostrar'] = dia_elegido['fecha_mostrar']
            
            # Generar horarios disponibles según el profesional elegido
            profesional_id = data[phone_number].get('profesional_id')
            horarios = generar_horarios_disponibles(dia_elegido['fecha_str'], profesional_id)

            if not horarios:
                profesional_nombre = data[phone_number].get('profesional_nombre', '')
                if profesional_nombre == 'Cualquiera':
                    return f"❌ No hay horarios disponibles para {dia_elegido['fecha_mostrar']} con ningún profesional.\n\nEscribe *menu* para elegir otro día."
                else:
                    return f"❌ No hay horarios disponibles para {dia_elegido['fecha_mostrar']} con {profesional_nombre}.\n\nEscribe *menu* para elegir otro día."

            states[phone_number] = STATE_WAITING_TIME

            # Guardar horarios para selección numerada  
            data[phone_number]['horarios_disponibles'] = horarios

            # Mostrar horarios como opciones numeradas
            profesional_nombre = data[phone_number].get('profesional_nombre', '')
            if profesional_nombre == 'Cualquiera':
                respuesta = f"⏰ *Horarios disponibles para {dia_elegido['fecha_mostrar']} (todos los profesionales):*\n\n"
            else:
                respuesta = f"⏰ *Horarios disponibles para {dia_elegido['fecha_mostrar']} con {profesional_nombre}:*\n\n"
            
            respuesta += "📋 *Opciones de horarios:*\n\n"
            
            for i, hora in enumerate(horarios, 1):
                if profesional_nombre == 'Cualquiera':
                    profs_disponibles = obtener_profesionales_disponibles_fecha_hora(dia_elegido['fecha_str'], hora)
                    nombres_profs = [p['nombre'] for p in profs_disponibles]
                    respuesta += f"*{i}* - {hora} ({', '.join(nombres_profs)})\n"
                else:
                    # Determinar si es mañana o tarde
                    hora_num = int(hora.split(':')[0])
                    emoji = "🌅" if hora_num < 14 else "🌆"
                    respuesta += f"*{i}* - {emoji} {hora}\n"

            respuesta += "\nResponde con el número de tu horario preferido."

            return respuesta
            
        else:
            return f"❌ Opción inválida. Por favor responde con un número del 1 al {len(opciones)}."
            
    except ValueError:
        opciones = data[phone_number].get('opciones_dias', [])
        return f"❌ Por favor responde con un número del 1 al {len(opciones)}."
