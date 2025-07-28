import re
from datetime import datetime, timedelta
import json
import os
import time

# Importar el nuevo módulo de base de datos
from database import (
    obtener_turnos_por_telefono,
    obtener_turnos_con_id_por_telefono,
    obtener_horarios_ocupados,
    verificar_horario_disponible,
    crear_turno,
    cancelar_turno_por_usuario
)

# Importar el módulo de notificaciones
from notifications import obtener_notificaciones_pendientes, marcar_notificacion_enviada

CONFIG_PATH = 'config.json'

user_states = {}
user_data = {}

# Tiempo máximo de inactividad en segundos para limpiar estados huérfanos
STATE_TIMEOUT = 600  # 10 minutos
# Guardar el último acceso de cada usuario
user_last_active = {}


def cargar_config():
    config_default = {
        "hora_inicio": 8, "hora_fin": 18, "intervalo": 30, "dias_bloqueados": [],
        "horarios_por_dia": {
            dia: {
                "manana": {"hora_inicio": 8, "hora_fin": 12, "intervalo": 30},
                "tarde": {"hora_inicio": 15, "hora_fin": 18, "intervalo": 30}
            } for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        }
    }
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            if "dias_bloqueados" not in config:
                config["dias_bloqueados"] = []
            if "horarios_por_dia" not in config:
                config["horarios_por_dia"] = config_default["horarios_por_dia"]
            # Migración: si algún día tiene solo un rango, convertirlo a dos rangos
            for dia, val in config["horarios_por_dia"].items():
                if "manana" not in val or "tarde" not in val:
                    config["horarios_por_dia"][dia] = {
                        "manana": val if isinstance(val, dict) else config_default["horarios_por_dia"][dia]["manana"],
                        "tarde": config_default["horarios_por_dia"][dia]["tarde"]
                    }
            return config
    return config_default


def parse_fecha(fecha_str):
    fecha_str = fecha_str.strip().lower()
    hoy = datetime.now().date()
    dias_semana = {
        'lunes': 0, 'martes': 1, 'miercoles': 2, 'miércoles': 2, 'jueves': 3, 'viernes': 4, 'sabado': 5, 'sábado': 5, 'domingo': 6
    }
    if fecha_str in ["hoy"]:
        return hoy.strftime("%Y-%m-%d")
    if fecha_str in ["mañana", "manana"]:
        return (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
    if fecha_str in dias_semana:
        dia_objetivo = dias_semana[fecha_str]
        dias_a_sumar = (dia_objetivo - hoy.weekday() + 7) % 7
        if dias_a_sumar == 0:
            dias_a_sumar = 7  # próximo día, no hoy
        return (hoy + timedelta(days=dias_a_sumar)).strftime("%Y-%m-%d")
    # DD/MM/YYYY o DD-MM-YYYY
    for fmt in ["%d/%m/%Y", "%d-%m-%Y"]:
        try:
            return datetime.strptime(fecha_str, fmt).strftime("%Y-%m-%d")
        except Exception:
            pass
    # DD/MM o DD-MM (asume año actual o próximo si ya pasó)
    for fmt in ["%d/%m", "%d-%m"]:
        try:
            dt = datetime.strptime(fecha_str, fmt)
            anio = hoy.year
            fecha = datetime(anio, dt.month, dt.day)
            if fecha.date() < hoy:
                fecha = datetime(anio+1, dt.month, dt.day)
            return fecha.strftime("%Y-%m-%d")
        except Exception:
            pass
    # YYYY-MM-DD (formato original)
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except Exception:
        pass
    return None


def limpiar_estados_huerfanos():
    ahora = time.time()
    inactivos = [k for k, v in user_last_active.items() if ahora -
                 v > STATE_TIMEOUT]
    for k in inactivos:
        user_states.pop(k, None)
        user_data.pop(k, None)
        user_last_active.pop(k, None)


def formatear_fecha_legible(fecha_str, hora_str=None):
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    dias = ['lunes', 'martes', 'miércoles',
            'jueves', 'viernes', 'sábado', 'domingo']
    dt = datetime.strptime(fecha_str, '%Y-%m-%d')
    dia_semana = dias[dt.weekday()]
    fecha_legible = f"{dia_semana} {dt.day} de {meses[dt.month-1]}"
    if hora_str:
        return f"{fecha_legible}, {hora_str}"
    return fecha_legible


def obtener_fechas_disponibles():
    """Obtiene las fechas disponibles para reservar (hoy + 6 días)"""
    hoy = datetime.now().date()
    fechas = []
    dias_nombres = ['lunes', 'martes', 'miércoles',
                    'jueves', 'viernes', 'sábado', 'domingo']

    # Obtener días bloqueados desde la configuración
    config = cargar_config()
    dias_bloqueados = set(config.get('dias_bloqueados', []))

    for i in range(7):
        fecha = hoy + timedelta(days=i)
        fecha_str = fecha.strftime('%Y-%m-%d')

        # Saltar días bloqueados
        if fecha_str in dias_bloqueados:
            continue

        nombre_dia = dias_nombres[fecha.weekday()]
        etiqueta = "hoy" if i == 0 else ("mañana" if i == 1 else nombre_dia)
        fechas.append({
            'fecha': fecha_str,
            'etiqueta': etiqueta,
            'fecha_legible': formatear_fecha_legible(fecha_str)
        })
    return fechas


def obtener_horarios_disponibles(fecha_str):
    """Obtiene los horarios disponibles para una fecha específica"""
    config_horarios = cargar_config()
    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    nombre_dia = fecha_dt.strftime('%A')
    nombres_map = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                   'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
    nombre_dia = nombres_map.get(nombre_dia, nombre_dia)

    horarios_por_dia = config_horarios.get('horarios_por_dia', {})
    rangos = horarios_por_dia.get(nombre_dia, {
        'manana': {'hora_inicio': config_horarios['hora_inicio'], 'hora_fin': 12, 'intervalo': config_horarios['intervalo']},
        'tarde': {'hora_inicio': 15, 'hora_fin': config_horarios['hora_fin'], 'intervalo': config_horarios['intervalo']}
    })

    # Generar todos los horarios posibles
    posibles = []

    # Procesar mañana y tarde por separado para evitar superposiciones
    for nombre_rango, rango in [('manana', rangos['manana']), ('tarde', rangos['tarde'])]:
        hora_inicio = rango['hora_inicio']
        hora_fin = rango['hora_fin']
        intervalo = rango['intervalo']

        # Generar horarios desde hora_inicio hasta hora_fin (sin incluir hora_fin)
        minutos_totales = hora_inicio * 60  # Convertir a minutos desde medianoche
        minutos_fin = hora_fin * 60

        while minutos_totales < minutos_fin:
            horas = minutos_totales // 60
            minutos = minutos_totales % 60
            horario_str = f"{horas:02d}:{minutos:02d}"

            # Evitar duplicados si ya existe el horario
            if horario_str not in posibles:
                posibles.append(horario_str)

            minutos_totales += intervalo

    # Ordenar los horarios cronológicamente
    posibles.sort()

    # Si es hoy, filtrar horarios que ya pasaron
    hoy = datetime.now().date()
    hora_actual = datetime.now().time()

    if fecha_dt == hoy:
        # Filtrar horarios que ya pasaron
        posibles_filtrados = []
        for hora_str in posibles:
            hora_obj = datetime.strptime(hora_str, '%H:%M').time()
            if hora_obj > hora_actual:
                posibles_filtrados.append(hora_str)
        posibles = posibles_filtrados

    # Verificar cuáles están ocupados
    ocupados = obtener_horarios_ocupados(fecha_str)

    disponibles = [h for h in posibles if h not in ocupados]
    return disponibles


def verificar_notificaciones_pendientes(from_number):
    """Verifica si hay notificaciones pendientes para un usuario específico"""
    try:
        notificaciones = obtener_notificaciones_pendientes()
        print(
            f"🔍 Verificando notificaciones para {from_number}: {len(notificaciones)} pendientes")

        notificaciones_usuario = [
            n for n in notificaciones if n['telefono'] == from_number]

        print(
            f"📱 Notificaciones para este usuario: {len(notificaciones_usuario)}")

        if notificaciones_usuario:
            # Enviar la primera notificación pendiente
            notificacion = notificaciones_usuario[0]
            mensaje = notificacion['mensaje']

            print(f"📨 Enviando notificación: {notificacion['tipo']}")

            # Marcar como enviada
            marcar_notificacion_enviada(notificacion)

            return mensaje

        return None
    except Exception as e:
        print(f"❌ Error al verificar notificaciones: {e}")
        return None


def handle_message(incoming_msg, from_number, user_states, user_data):
    limpiar_estados_huerfanos()
    user_last_active[from_number] = time.time()
    state = user_states.get(from_number, 'inicio')
    config_horarios = cargar_config()

    # Las notificaciones se envían automáticamente por el daemon, no aquí
    # Esto evita interferir con el flujo de conversación

    # Menú principal
    if incoming_msg.lower() in ['hola', 'start', '/start'] or state == 'inicio':
        user_states[from_number] = 'menu_principal'
        return (
            '🤖 *Sistema de Turnos* 🤖\n\n'
            'Selecciona una opción:\n'
            '1️⃣ Reservar turno\n'
            '2️⃣ Ver mis turnos\n'
            '3️⃣ Cancelar turno\n'
            '4️⃣ Ayuda\n\n'
            'Escribe el número de tu opción:'
        )
    # Manejo del menú principal
    elif state == 'menu_principal':
        if incoming_msg.strip() == '1':
            user_states[from_number] = 'esperando_nombre'
            return (
                '📝 *Reservar Turno* 📝\n\n'
                'Por favor, ingresa tu nombre completo:'
            )
        elif incoming_msg.strip() == '2':
            # Ver turnos
            try:
                turnos = obtener_turnos_por_telefono(from_number)
                if turnos:
                    respuesta = '📅 *Tus turnos reservados:*\n\n'
                    for i, t in enumerate(turnos, 1):
                        respuesta += f"{i}) {t[0]}: {formatear_fecha_legible(t[1], t[2])}\n"
                    respuesta += '\n💬 Escribe *hola* para volver al menú principal'
                    user_states[from_number] = 'inicio'
                    return respuesta
                else:
                    user_states[from_number] = 'inicio'
                    return '❌ No tienes turnos reservados.\n\n💬 Escribe *hola* para volver al menú principal'
            except Exception as e:
                user_states[from_number] = 'inicio'
                return f"❌ Error al consultar turnos: {e}\n\n💬 Escribe *hola* para volver al menú principal"
        elif incoming_msg.strip() == '3':
            # Cancelar turno
            try:
                turnos = obtener_turnos_con_id_por_telefono(from_number)
                if turnos:
                    respuesta = '🗑️ *Cancelar Turno* 🗑️\n\n¿Qué turno deseas cancelar?\n\n'
                    for idx, t in enumerate(turnos, 1):
                        respuesta += f"{idx}) {t[1]}: {formatear_fecha_legible(t[2], t[3])}\n"
                    respuesta += '\nEscribe el número del turno a cancelar:'
                    user_states[from_number] = 'esperando_cancelacion'
                    user_data[from_number] = {'turnos': turnos}
                    return respuesta
                else:
                    user_states[from_number] = 'inicio'
                    return '❌ No tienes turnos para cancelar.\n\n💬 Escribe *hola* para volver al menú principal'
            except Exception as e:
                user_states[from_number] = 'inicio'
                return f"❌ Error al consultar turnos: {e}\n\n💬 Escribe *hola* para volver al menú principal"
        elif incoming_msg.strip() == '4':
            user_states[from_number] = 'inicio'
            return (
                '❓ *Ayuda* ❓\n\n'
                '• Este bot te permite reservar, ver y cancelar turnos\n'
                '• Solo puedes reservar turnos desde hoy hasta 6 días adelante\n'
                '• Los horarios disponibles dependen de la configuración del día\n'
                '• Usa los números para navegar por los menús\n\n'
                '💬 Escribe *hola* para volver al menú principal'
            )
        else:
            return (
                '❌ Opción inválida. Por favor selecciona:\n\n'
                '1️⃣ Reservar turno\n'
                '2️⃣ Ver mis turnos\n'
                '3️⃣ Cancelar turno\n'
                '4️⃣ Ayuda'
            )
    elif state == 'inicio' and incoming_msg.lower() == 'consultar':
        try:
            turnos = obtener_turnos_por_telefono(from_number)
            if turnos:
                respuesta = 'Tus turnos reservados:\n'
                for t in turnos:
                    respuesta += f"- {t[0]}: {formatear_fecha_legible(t[1], t[2])}\n"
                return respuesta.strip()
            else:
                return 'No tienes turnos reservados.'
        except Exception as e:
            return f"Ocurrió un error al consultar los turnos: {e}"
    elif state == 'inicio' and incoming_msg.lower() == 'cancelar':
        try:
            turnos = obtener_turnos_con_id_por_telefono(from_number)
            if turnos:
                respuesta = '¿Qué turno deseas cancelar? Escribe el número correspondiente:\n'
                for idx, t in enumerate(turnos, 1):
                    respuesta += f"{idx}) {t[1]}: {formatear_fecha_legible(t[2], t[3])}\n"
                user_states[from_number] = 'esperando_cancelacion'
                user_data[from_number] = {'turnos': turnos}
                return respuesta.strip()
            else:
                return 'No tienes turnos para cancelar.'
        except Exception as e:
            return f"Ocurrió un error al consultar los turnos: {e}"
    # Esperando confirmación de cancelación
    elif state == 'esperando_cancelacion':
        try:
            opcion = int(incoming_msg.strip())
            turnos = user_data[from_number]['turnos']
            if 1 <= opcion <= len(turnos):
                turno_id = turnos[opcion-1][0]
                turno_info = turnos[opcion-1]

                if cancelar_turno_por_usuario(turno_id, from_number):
                    # Notificar al admin sobre la cancelación
                    try:
                        from admin_notifications import notificar_cancelacion_turno
                        notificar_cancelacion_turno(
                            turno_info[1], turno_info[2], turno_info[3])
                    except Exception as e:
                        print(
                            f"⚠️ Error enviando notificación de cancelación: {e}")

                    user_states[from_number] = 'inicio'
                    user_data.pop(from_number, None)
                    fecha_legible = formatear_fecha_legible(
                        turno_info[2], turno_info[3])
                    return (
                        f"✅ *Turno Cancelado* ✅\n\n"
                        f"👤 Nombre: {turno_info[1]}\n"
                        f"📅 Fecha y hora: {fecha_legible}\n\n"
                        f"Tu turno ha sido cancelado exitosamente.\n\n"
                        f"💬 Escribe *hola* para volver al menú principal"
                    )
                else:
                    return f"❌ Error al cancelar el turno. Inténtalo nuevamente."
            else:
                return f"❌ Opción inválida. Selecciona un número del 1 al {len(turnos)}:"
        except ValueError:
            turnos = user_data[from_number]['turnos']
            return f"❌ Por favor ingresa un número del 1 al {len(turnos)}:"
        except Exception as e:
            user_states[from_number] = 'inicio'
            user_data.pop(from_number, None)
            return f"❌ Error al cancelar el turno: {e}\n\n💬 Escribe *hola* para volver al menú principal"
    # Esperando nombre para reserva
    elif state == 'esperando_nombre':
        if len(incoming_msg.strip()) < 2:
            return '❌ Por favor ingresa un nombre válido (mínimo 2 caracteres):'
        user_data[from_number] = {'nombre': incoming_msg.strip()}
        user_states[from_number] = 'seleccionando_fecha'

        # Mostrar fechas disponibles
        fechas = obtener_fechas_disponibles()
        respuesta = '📅 *Seleccionar Fecha* 📅\n\n¿Qué día prefieres para tu turno?\n\n'
        for i, fecha in enumerate(fechas, 1):
            respuesta += f"{i}) {fecha['etiqueta'].title()} ({fecha['fecha_legible']})\n"
        respuesta += '\nEscribe el número del día:'
        user_data[from_number]['fechas_disponibles'] = fechas
        return respuesta
    # Seleccionando fecha
    elif state == 'seleccionando_fecha':
        try:
            opcion = int(incoming_msg.strip())
            fechas = user_data[from_number]['fechas_disponibles']
            if 1 <= opcion <= len(fechas):
                fecha_seleccionada = fechas[opcion-1]['fecha']
                user_data[from_number]['fecha'] = fecha_seleccionada
                user_states[from_number] = 'seleccionando_hora'

                # Mostrar horarios disponibles
                horarios = obtener_horarios_disponibles(fecha_seleccionada)
                if horarios:
                    respuesta = f"🕐 *Seleccionar Horario* 🕐\n\nFecha: {fechas[opcion-1]['fecha_legible']}\n\nHorarios disponibles:\n\n"
                    for i, hora in enumerate(horarios, 1):
                        respuesta += f"{i}) {hora}\n"
                    respuesta += '\nEscribe el número del horario:'
                    user_data[from_number]['horarios_disponibles'] = horarios
                    return respuesta
                else:
                    user_states[from_number] = 'seleccionando_fecha'
                    return f"❌ No hay horarios disponibles para {fechas[opcion-1]['fecha_legible']}.\n\nPor favor selecciona otro día:"
            else:
                return f"❌ Opción inválida. Selecciona un número del 1 al {len(fechas)}:"
        except ValueError:
            fechas = user_data[from_number]['fechas_disponibles']
            return f"❌ Por favor ingresa un número del 1 al {len(fechas)}:"
    # Seleccionando hora
    elif state == 'seleccionando_hora':
        try:
            opcion = int(incoming_msg.strip())
            horarios = user_data[from_number]['horarios_disponibles']
            if 1 <= opcion <= len(horarios):
                hora_seleccionada = horarios[opcion-1]
                user_data[from_number]['hora'] = hora_seleccionada

                # Confirmar y guardar turno
                datos = user_data[from_number]
                try:
                    # Verificar disponibilidad y crear turno
                    if not verificar_horario_disponible(datos['fecha'], datos['hora']):
                        user_states[from_number] = 'seleccionando_hora'
                        return f"❌ El horario {datos['hora']} ya fue reservado por otro usuario.\n\nPor favor selecciona otro horario:"

                    if crear_turno(datos['nombre'], datos['fecha'], datos['hora'], from_number):
                        # Notificar al admin sobre el nuevo turno
                        try:
                            from admin_notifications import notificar_nuevo_turno
                            notificar_nuevo_turno(
                                datos['nombre'], from_number, datos['fecha'], datos['hora'])
                        except Exception as e:
                            print(
                                f"⚠️ Error enviando notificación de admin: {e}")

                        user_states[from_number] = 'inicio'
                        user_data.pop(from_number)
                        fecha_legible = formatear_fecha_legible(
                            datos['fecha'], datos['hora'])
                        return (
                            f"✅ *Turno Confirmado* ✅\n\n"
                            f"👤 Nombre: {datos['nombre']}\n"
                            f"📅 Fecha y hora: {fecha_legible}\n\n"
                            f"¡Tu turno ha sido reservado exitosamente!\n\n"
                            f"💬 Escribe *hola* para volver al menú principal"
                        )
                    else:
                        user_states[from_number] = 'inicio'
                        user_data.pop(from_number, None)
                        return f"❌ Error al guardar el turno. Inténtalo nuevamente.\n\n💬 Escribe *hola* para volver al menú principal"
                except Exception as e:
                    user_states[from_number] = 'inicio'
                    user_data.pop(from_number, None)
                    return f"❌ Error al guardar el turno: {e}\n\n💬 Escribe *hola* para volver al menú principal"
            else:
                return f"❌ Opción inválida. Selecciona un número del 1 al {len(horarios)}:"
        except ValueError:
            horarios = user_data[from_number]['horarios_disponibles']
            return f"❌ Por favor ingresa un número del 1 al {len(horarios)}:"
    # Mensaje no reconocido
    else:
        return (
            '❌ No entendí tu mensaje.\n\n'
            '💬 Escribe *hola* para ir al menú principal'
        )
