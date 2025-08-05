from src.admin.notifications import notificar_admin_cancelacion_directa
from src.services.notifications import notificar_cancelacion_turno, notificar_dia_bloqueado
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, Response
import os
import json
import requests
from datetime import datetime, timedelta
import threading
import time

# Importar el nuevo módulo de base de datos
from src.core.database import obtener_turnos_por_fecha, eliminar_turno_admin, obtener_todos_los_turnos
import sys
sys.path.append(os.path.join(os.path.dirname(
    __file__), '..', 'bots', 'senders'))


def generar_domingos_proximos_meses(meses=6):
    """Genera las fechas de todos los domingos de los próximos meses"""
    domingos = []
    hoy = datetime.now().date()

    # Encontrar el próximo domingo
    dias_hasta_domingo = (6 - hoy.weekday()) % 7
    if dias_hasta_domingo == 0 and hoy.weekday() == 6:  # Si hoy es domingo
        proximo_domingo = hoy
    else:
        proximo_domingo = hoy + timedelta(days=dias_hasta_domingo)

    # Generar domingos para los próximos meses
    fecha_limite = hoy + timedelta(days=meses * 30)  # Aproximadamente X meses
    domingo_actual = proximo_domingo

    while domingo_actual <= fecha_limite:
        domingos.append(domingo_actual.strftime('%Y-%m-%d'))
        domingo_actual += timedelta(days=7)  # Siguiente domingo

    return domingos


# Importar el módulo de notificaciones

# Importar notificaciones para admin

# Obtener ruta raíz del proyecto y configuración
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config', 'config.json')
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')

# Asegurar que los directorios existen
os.makedirs(os.path.join(PROJECT_ROOT, 'config'), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)


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
    else:
        config = config_default.copy()

    # Agregar automáticamente todos los domingos como días bloqueados
    domingos = generar_domingos_proximos_meses(6)  # 6 meses
    dias_bloqueados_set = set(config["dias_bloqueados"])

    # Agregar domingos que no estén ya en la lista
    for domingo in domingos:
        if domingo not in dias_bloqueados_set:
            config["dias_bloqueados"].append(domingo)

    # Guardar la configuración actualizada
    guardar_config(config)

    return config


def guardar_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)


@app.route('/', methods=['GET'])
def index():
    semana_inicio_str = request.args.get('semana')
    hoy = datetime.now().date()
    if semana_inicio_str:
        semana_inicio = datetime.strptime(semana_inicio_str, '%Y-%m-%d').date()
    else:
        semana_inicio = hoy - timedelta(days=hoy.weekday())
        semana_inicio_str = semana_inicio.strftime('%Y-%m-%d')

    dias_semana = []
    config = cargar_config()
    dias_bloqueados = set(config.get('dias_bloqueados', []))
    horarios_por_dia = config.get('horarios_por_dia', {})

    nombres_dias = ['Lunes', 'Martes', 'Miércoles',
                    'Jueves', 'Viernes', 'Sábado', 'Domingo']

    if semana_inicio == (hoy - timedelta(days=hoy.weekday())):
        # Semana actual: mostrar desde hoy y los 6 días siguientes
        for i in range(7):
            dia = hoy + timedelta(days=i)
            fecha_str = dia.strftime('%Y-%m-%d')
            nombre_dia = nombres_dias[dia.weekday()]
            turnos = obtener_turnos_por_fecha(fecha_str)
            turnos_marcados = []
            for t in turnos:
                # t[2]=fecha, t[3]=hora (formato HH:MM)
                turno_dt = datetime.strptime(
                    f"{t[2]} {t[3]}", "%Y-%m-%d %H:%M")
                es_nuevo = (datetime.now() - turno_dt).total_seconds() < 86400
                turnos_marcados.append(list(t) + [es_nuevo])
            horario = horarios_por_dia.get(nombre_dia, {
                'manana': {'hora_inicio': config['hora_inicio'], 'hora_fin': 12, 'intervalo': config['intervalo']},
                'tarde': {'hora_inicio': 15, 'hora_fin': config['hora_fin'], 'intervalo': config['intervalo']}
            })
            dias_semana.append({
                'nombre': nombre_dia,
                'fecha': fecha_str,
                'turnos': turnos_marcados,
                'bloqueado': fecha_str in dias_bloqueados,
                'horario': horario,
                'es_hoy': fecha_str == hoy.strftime('%Y-%m-%d')
            })
    else:
        # Otra semana: mostrar los 7 días de esa semana
        for i in range(7):
            dia = semana_inicio + timedelta(days=i)
            fecha_str = dia.strftime('%Y-%m-%d')
            nombre_dia = nombres_dias[dia.weekday()]
            turnos = obtener_turnos_por_fecha(fecha_str)
            turnos_marcados = []
            for t in turnos:
                turno_dt = datetime.strptime(
                    f"{t[2]} {t[3]}", "%Y-%m-%d %H:%M")
                es_nuevo = (datetime.now() - turno_dt).total_seconds() < 86400
                turnos_marcados.append(list(t) + [es_nuevo])
            horario = horarios_por_dia.get(nombre_dia, {
                'manana': {'hora_inicio': config['hora_inicio'], 'hora_fin': 12, 'intervalo': config['intervalo']},
                'tarde': {'hora_inicio': 15, 'hora_fin': config['hora_fin'], 'intervalo': config['intervalo']}
            })
            dias_semana.append({
                'nombre': nombre_dia,
                'fecha': fecha_str,
                'turnos': turnos_marcados,
                'bloqueado': fecha_str in dias_bloqueados,
                'horario': horario,
                'es_hoy': fecha_str == hoy.strftime('%Y-%m-%d')
            })
    return render_template('admin_panel.html', dias_semana=dias_semana, semana_inicio_str=semana_inicio_str, dias_bloqueados=list(dias_bloqueados))


@app.route('/eliminar/<int:turno_id>', methods=['POST'])
def eliminar(turno_id):
    try:
        # Obtener datos del turno antes de eliminarlo para notificar al usuario
        turnos = obtener_todos_los_turnos()
        turno_a_eliminar = None

        for turno in turnos:
            if turno[0] == turno_id:  # turno[0] es el ID
                turno_a_eliminar = turno
                break

        # Eliminar el turno
        if eliminar_turno_admin(turno_id):
            # Si encontramos el turno, enviar notificación directa por WhatsApp
            if turno_a_eliminar:
                turno_id, nombre, fecha, hora, telefono = turno_a_eliminar

                # Usar la nueva función de envío directo (inmediato)
                exito_envio = notificar_admin_cancelacion_directa(
                    nombre, fecha, hora, telefono)

                if exito_envio:
                    print(
                        f"✅ Usuario {nombre} notificado por WhatsApp sobre cancelación")
                else:
                    print(
                        f"❌ Error enviando WhatsApp a {nombre} ({telefono})")
                    print(f"⚠️ El usuario no fue notificado sobre la cancelación")

        semana = request.form.get('semana')
        if semana:
            return redirect(url_for('index', semana=semana))
        return redirect(url_for('index'))

    except Exception as e:
        print(f"❌ Error al eliminar turno: {e}")
        return redirect(url_for('index'))


@app.route('/configurar_dia', methods=['POST'])
def configurar_dia():
    nombre_dia = request.form['nombre_dia']
    semana = request.form.get('semana')
    config = cargar_config()
    if 'horarios_por_dia' not in config:
        config['horarios_por_dia'] = {}
    config['horarios_por_dia'][nombre_dia] = {
        'hora_inicio': int(request.form['hora_inicio']),
        'hora_fin': int(request.form['hora_fin']),
        'intervalo': int(request.form['intervalo'])
    }
    guardar_config(config)
    return redirect(url_for('index', semana=semana))


@app.route('/bloquear_dia', methods=['POST'])
def bloquear_dia():
    fecha = request.form['fecha']
    semana = request.form.get('semana')
    config = cargar_config()

    if fecha not in config['dias_bloqueados']:
        # Notificar a usuarios con turnos en este día antes de bloquearlo
        try:
            notificaciones = notificar_dia_bloqueado(fecha)
            if notificaciones:
                print(
                    f"✅ Enviadas {len(notificaciones)} notificaciones por bloqueo del día {fecha}")
        except Exception as e:
            print(f"❌ Error al enviar notificaciones por día bloqueado: {e}")

        # Bloquear el día
        config['dias_bloqueados'].append(fecha)
        guardar_config(config)

        print(f"🔒 Día {fecha} bloqueado (sin notificar al admin)")

    return redirect(url_for('index', semana=semana))


@app.route('/desbloquear_dia', methods=['POST'])
def desbloquear_dia():
    fecha = request.form['fecha']
    semana = request.form.get('semana')
    config = cargar_config()
    if fecha in config['dias_bloqueados']:
        config['dias_bloqueados'].remove(fecha)
        guardar_config(config)

        print(f"🔓 Día {fecha} desbloqueado (sin notificar al admin)")

    return redirect(url_for('index', semana=semana))


@app.route('/api/turnos_semana')
def api_turnos_semana():
    """API para obtener datos de la semana - versión móvil"""
    semana_inicio_str = request.args.get('semana')
    hoy = datetime.now().date()

    if semana_inicio_str:
        semana_inicio = datetime.strptime(semana_inicio_str, '%Y-%m-%d').date()
    else:
        dias_hasta_lunes = hoy.weekday()
        semana_inicio = hoy - timedelta(days=dias_hasta_lunes)

    config = cargar_config()
    horarios_por_dia = config.get('horarios_por_dia', {})
    dias_bloqueados = set(config.get('dias_bloqueados', []))

    nombres_dias = ['Lunes', 'Martes', 'Miércoles',
                    'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dias_semana = []

    for i in range(7):
        dia = semana_inicio + timedelta(days=i)
        fecha_str = dia.strftime('%Y-%m-%d')
        nombre_dia = nombres_dias[dia.weekday()]
        turnos = obtener_turnos_por_fecha(fecha_str)

        turnos_marcados = []
        for t in turnos:
            turno_dt = datetime.strptime(f"{t[2]} {t[3]}", "%Y-%m-%d %H:%M")
            es_nuevo = (datetime.now() - turno_dt).total_seconds() < 86400
            turnos_marcados.append(list(t) + [es_nuevo])

        horario = horarios_por_dia.get(nombre_dia, {
            'manana': {'hora_inicio': 9, 'hora_fin': 12, 'intervalo': 30},
            'tarde': {'hora_inicio': 15, 'hora_fin': 18, 'intervalo': 30}
        })

        dias_semana.append({
            'nombre': nombre_dia,
            'fecha': fecha_str,
            'turnos': turnos_marcados,
            'bloqueado': fecha_str in dias_bloqueados,
            'es_hoy': dia == hoy,
            'horario': horario
        })

    return jsonify({
        'dias_semana': dias_semana,
        'semana_inicio_str': semana_inicio.strftime('%Y-%m-%d')
    })


@app.route('/configurar_rangos', methods=['POST'])
def configurar_rangos_mobile():
    """Configurar rangos horarios desde el panel móvil"""
    config = cargar_config()
    nombre_dia = request.form.get('nombre_dia')

    # Actualizar horarios
    if 'horarios_por_dia' not in config:
        config['horarios_por_dia'] = {}

    config['horarios_por_dia'][nombre_dia] = {
        'manana': {
            'hora_inicio': int(request.form.get('manana_hora_inicio')),
            'hora_fin': int(request.form.get('manana_hora_fin')),
            'intervalo': int(request.form.get('manana_intervalo'))
        },
        'tarde': {
            'hora_inicio': int(request.form.get('tarde_hora_inicio')),
            'hora_fin': int(request.form.get('tarde_hora_fin')),
            'intervalo': int(request.form.get('tarde_intervalo'))
        }
    }

    guardar_config(config)
    return jsonify({'success': True})


@app.route('/mobile')
def mobile_panel():
    """Versión móvil del panel de administración"""
    return render_template('admin_panel_mobile.html')


@app.route('/manifest.json')
def manifest():
    """Archivo manifest para PWA"""
    return send_from_directory('static', 'manifest.json', mimetype='application/json')


@app.route('/sw.js')
def service_worker():
    """Service Worker para PWA"""
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')


@app.route('/notificaciones')
def ver_notificaciones():
    """Ver notificaciones pendientes"""
    from src.services.notifications import obtener_notificaciones_pendientes
    notificaciones = obtener_notificaciones_pendientes()
    return jsonify({
        'total': len(notificaciones),
        'notificaciones': notificaciones
    })


@app.route('/marcar_enviada/<int:index>', methods=['POST'])
def marcar_enviada(index):
    """Marcar una notificación como enviada"""
    try:
        from src.services.notifications import obtener_notificaciones_pendientes, marcar_notificacion_enviada
        notificaciones = obtener_notificaciones_pendientes()
        if 0 <= index < len(notificaciones):
            marcar_notificacion_enviada(notificaciones[index])
            return jsonify({'success': True})
        return jsonify({'error': 'Índice inválido'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/static/<path:filename>')
def static_files(filename):
    """Servir archivos estáticos"""
    return send_from_directory('static', filename)


@app.route('/health')
def health_check():
    """Endpoint de salud para monitoreo de plataformas cloud"""
    return jsonify({
        'status': 'ok',
        'service': 'TurnosBot Admin Panel',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/stats')
def api_stats():
    """Endpoint para estadísticas de la base de datos"""
    try:
        from src.services.maintenance import obtener_estadisticas_db
        stats = obtener_estadisticas_db()

        if stats:
            return jsonify({
                'status': 'ok',
                'datos': stats,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'mensaje': 'No se pudieron obtener estadísticas'
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'mensaje': str(e)
        }), 500


@app.route('/api/mantenimiento', methods=['POST'])
def api_mantenimiento():
    """Endpoint para ejecutar mantenimiento manual"""
    try:
        from src.services.maintenance import mantenimiento_completo
        mantenimiento_completo()

        return jsonify({
            'status': 'ok',
            'mensaje': 'Mantenimiento ejecutado correctamente',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'mensaje': str(e)
        }), 500


# Webhook de WhatsApp - Agregado al panel admin para accesibilidad
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verificación del webhook de WhatsApp"""
    import logging
    logger = logging.getLogger(__name__)

    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    # Token de verificación desde variable de entorno
    expected_token = os.environ.get(
        'WHATSAPP_VERIFY_TOKEN', 'mi_token_verificacion_whatsapp')

    if verify_token == expected_token:
        logger.info("Webhook verificado exitosamente")
        return challenge
    else:
        logger.error(f"Token de verificación incorrecto: {verify_token}")
        return "Token incorrecto", 403


@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibir mensajes de WhatsApp y procesarlos"""
    import logging
    from src.core.bot_core import handle_message

    logger = logging.getLogger(__name__)

    try:
        data = request.get_json()
        logger.info(
            f"🔍 Datos completos recibidos en webhook: {json.dumps(data, indent=2)}")

        # Verificar que el mensaje es válido
        if not data or 'entry' not in data:
            logger.warning("⚠️ Datos inválidos o sin 'entry'")
            return jsonify({'status': 'ok'})

        for entry in data['entry']:
            logger.info(f"📨 Procesando entry: {entry}")

            for change in entry.get('changes', []):
                logger.info(f"🔄 Procesando change: {change}")

                if change.get('field') == 'messages':
                    value = change.get('value', {})
                    logger.info(f"📱 Value de mensajes: {value}")

                    # Procesar mensajes entrantes
                    for message in value.get('messages', []):
                        phone_number = message['from']
                        message_text = message.get('text', {}).get('body', '')
                        message_id = message['id']

                        logger.info(
                            f"📞 Mensaje de {phone_number}: '{message_text}' (ID: {message_id})")

                        # Usar el sistema de bot core con los parámetros correctos
                        try:
                            # Importar estados globales del bot_core
                            from src.core.bot_core import user_states, user_data

                            response = handle_message(
                                message_text, phone_number, user_states, user_data)
                            logger.info(
                                f"✅ Respuesta del bot_core: {response}")

                            if response:
                                logger.info(
                                    f"📤 Bot generó respuesta: {response}")
                                # Enviar respuesta inmediata por WhatsApp
                                try:
                                    enviado = enviar_respuesta_whatsapp(
                                        phone_number, response)
                                    if enviado:
                                        logger.info(
                                            f"✅ Respuesta enviada por WhatsApp a {phone_number}")
                                    else:
                                        logger.error(
                                            f"❌ No se pudo enviar respuesta a {phone_number}")
                                except Exception as send_error:
                                    logger.error(
                                        f"💥 Error enviando respuesta WhatsApp: {send_error}")
                            else:
                                logger.warning(
                                    f"⚠️ Bot no generó respuesta para: {message_text}")

                        except Exception as e:
                            logger.error(f"❌ Error en handle_message: {e}")
                            import traceback
                            logger.error(
                                f"🔍 Traceback completo: {traceback.format_exc()}")

        return jsonify({'status': 'ok'})

    except Exception as e:
        logger.error(f"💥 Error crítico procesando webhook: {e}")
        import traceback
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/test_webhook', methods=['POST'])
def test_webhook():
    """Endpoint para probar el webhook manualmente"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Estructura de prueba mínima
    test_data = {
        'entry': [{
            'changes': [{
                'field': 'messages',
                'value': {
                    'messages': [{
                        'from': data.get('phone', '5491123456789'),
                        'text': {'body': data.get('message', 'hola')},
                        'id': 'test_message_id'
                    }]
                }
            }]
        }]
    }

    # Procesar como webhook normal
    original_request = request
    try:
        # Simular request con test_data
        result = webhook()  # Esto procesará usando los datos de prueba
        return jsonify({
            'status': 'test_completed',
            'message': 'Webhook test executed',
            'test_data': test_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def enviar_respuesta_whatsapp(phone_number, message):
    """Enviar respuesta inmediata de WhatsApp"""
    try:
        # Obtener configuración de WhatsApp
        access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
        phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')

        if not access_token or not phone_number_id:
            print("⚠️ Variables de WhatsApp no configuradas para envío")
            return False

        # Limpiar número de teléfono (remover prefijos si es necesario)
        clean_number = phone_number
        if phone_number.startswith('+'):
            clean_number = phone_number[1:]

        # API endpoint
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

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            print(f"✅ Respuesta enviada a {phone_number}")
            return True
        else:
            print(
                f"❌ Error enviando respuesta: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error crítico enviando respuesta: {e}")
        return False


# API para notificaciones del panel móvil
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Obtener notificaciones para el panel móvil"""
    try:
        from src.admin.notifications import obtener_notificaciones_pendientes
        notificaciones = obtener_notificaciones_pendientes()

        # Formatear notificaciones para el frontend
        notificaciones_formateadas = []
        for notif in notificaciones:
            tipo = notif.get('tipo', '')
            datos = notif.get('datos', {})
            timestamp = notif.get('timestamp', '')

            # Crear mensaje legible según el tipo
            if tipo == 'nuevo_turno':
                mensaje = f"Nuevo turno: {datos.get('nombre', 'N/A')} - {datos.get('fecha', '')} {datos.get('hora', '')}"
                icono = "📅"
                prioridad = "normal"
            elif tipo == 'cancelacion_turno':
                mensaje = f"Turno cancelado: {datos.get('nombre', 'N/A')} - {datos.get('fecha', '')} {datos.get('hora', '')}"
                icono = "❌"
                prioridad = "alta"
            elif tipo == 'bloqueo_dia':
                mensaje = f"Día bloqueado: {datos.get('fecha', 'N/A')}"
                icono = "🚫"
                prioridad = "normal"
            elif tipo == 'desbloqueo_dia':
                mensaje = f"Día desbloqueado: {datos.get('fecha', 'N/A')}"
                icono = "✅"
                prioridad = "normal"
            else:
                mensaje = f"Evento: {tipo}"
                icono = "ℹ️"
                prioridad = "baja"

            notificaciones_formateadas.append({
                'id': f"{timestamp}_{tipo}",
                'tipo': tipo,
                'mensaje': mensaje,
                'icono': icono,
                'prioridad': prioridad,
                'timestamp': timestamp,
                'datos': datos
            })

        return jsonify({
            'success': True,
            'notifications': notificaciones_formateadas,
            'count': len(notificaciones_formateadas)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'notifications': [],
            'count': 0
        }), 500


@app.route('/api/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    """Marcar notificaciones como leídas"""
    try:
        from src.admin.notifications import limpiar_notificaciones_viejas
        # Limpiar notificaciones (las marca como procesadas)
        eliminadas = limpiar_notificaciones_viejas(0)  # Limpiar todas

        return jsonify({
            'success': True,
            'marked_read': eliminadas
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/notifications/count', methods=['GET'])
def get_notifications_count():
    """Obtener solo el conteo de notificaciones pendientes"""
    try:
        from src.admin.notifications import contar_notificaciones_pendientes
        count = contar_notificaciones_pendientes()

        return jsonify({
            'success': True,
            'count': count
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'count': 0
        }), 500


# Variables globales para notificaciones en tiempo real
clients_sse = []
last_notification_count = 0
consecutive_no_change = 0


def add_sse_client(client):
    """Agregar cliente SSE"""
    clients_sse.append(client)


def remove_sse_client(client):
    """Remover cliente SSE"""
    if client in clients_sse:
        clients_sse.remove(client)


def send_sse_notification(data):
    """Enviar notificación SSE a todos los clientes conectados"""
    global clients_sse
    dead_clients = []

    # Copia para evitar modificación durante iteración
    for client in clients_sse[:]:
        try:
            client.put(f"data: {json.dumps(data)}\n\n")
        except:
            dead_clients.append(client)

    # Remover clientes desconectados
    for client in dead_clients:
        remove_sse_client(client)


def notification_monitor():
    """Monitor de notificaciones para envío en tiempo real - optimizado para Railway Sleep"""
    global last_notification_count, consecutive_no_change

    while True:
        try:
            from src.admin.notifications import contar_notificaciones_pendientes
            current_count = contar_notificaciones_pendientes()

            if current_count != last_notification_count:
                # Hay cambios en las notificaciones
                data = {
                    'type': 'notification_update',
                    'count': current_count,
                    'timestamp': datetime.now().isoformat()
                }
                send_sse_notification(data)
                last_notification_count = current_count
                consecutive_no_change = 0

                # Después de cambio, revisar más frecuentemente por si hay más
                sleep_time = 2
            else:
                consecutive_no_change += 1

                # Usar intervalos progresivamente más largos cuando no hay cambios
                if len(clients_sse) == 0:
                    # Sin clientes conectados, dormir más tiempo
                    sleep_time = 30
                elif consecutive_no_change < 5:
                    sleep_time = 5  # Normal
                elif consecutive_no_change < 20:
                    sleep_time = 10  # Menos frecuente
                else:
                    sleep_time = 30  # Muy poco frecuente para permitir sleep

        except Exception as e:
            print(f"Error en monitor de notificaciones: {e}")
            sleep_time = 10

        time.sleep(sleep_time)


# Iniciar monitor en background
notification_monitor_thread = threading.Thread(
    target=notification_monitor, daemon=True)
notification_monitor_thread.start()

# Endpoint SSE para notificaciones en tiempo real


@app.route('/api/notifications/stream')
def notification_stream():
    """Stream de notificaciones en tiempo real usando Server-Sent Events"""
    import queue

    def event_stream():
        q = queue.Queue()
        add_sse_client(q)

        try:
            while True:
                try:
                    # Enviar heartbeat cada 30 segundos
                    data = q.get(timeout=30)
                    yield data
                except queue.Empty:
                    # Heartbeat para mantener conexión
                    yield "data: {\"type\": \"heartbeat\"}\n\n"
        except GeneratorExit:
            remove_sse_client(q)

    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )


# Health check endpoint para Railway Sleep optimization
@app.route('/api/health/detailed')
def health_check_detailed():
    """Health check detallado que indica el estado de actividad de la aplicación"""
    try:
        from src.admin.notifications import contar_notificaciones_pendientes
        notification_count = contar_notificaciones_pendientes()
        connected_clients = len(clients_sse)

        # Determinar si la app está "idle" (puede dormir)
        is_idle = (
            notification_count == 0 and
            connected_clients == 0 and
            consecutive_no_change > 10
        )

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'notifications_pending': notification_count,
                'sse_clients_connected': connected_clients,
                'can_sleep': is_idle
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/keep-alive')
def keep_alive():
    """Endpoint para mantener la aplicación activa en Railway"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.now().isoformat(),
        'message': 'TurnosBot daemon keep-alive ping'
    })


if __name__ == '__main__':
    # El puerto lo asigna automáticamente la plataforma cloud
    port = int(os.environ.get('PORT', 9000))
    app.run(host='0.0.0.0', port=port, debug=False)
