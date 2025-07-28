from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import json
from datetime import datetime, timedelta

# Importar el nuevo módulo de base de datos
from database import obtener_turnos_por_fecha, eliminar_turno_admin, obtener_todos_los_turnos

# Importar el módulo de notificaciones
from notifications import notificar_cancelacion_turno, notificar_dia_bloqueado

# Importar notificaciones para admin
from admin_notifications import notificar_admin

CONFIG_PATH = 'config.json'

app = Flask(__name__)


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
            # Si encontramos el turno, enviar notificación
            if turno_a_eliminar:
                turno_id, nombre, fecha, hora, telefono = turno_a_eliminar
                notificar_cancelacion_turno(
                    turno_id, nombre, fecha, hora, telefono)
                print(
                    f"✅ Notificación enviada a {telefono} por cancelación de turno")

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

        # Notificar al admin sobre el bloqueo
        try:
            notificar_admin('bloqueo_dia', fecha)
        except Exception as e:
            print(f"❌ Error al notificar admin sobre bloqueo: {e}")

    return redirect(url_for('index', semana=semana))


@app.route('/desbloquear_dia', methods=['POST'])
def desbloquear_dia():
    fecha = request.form['fecha']
    semana = request.form.get('semana')
    config = cargar_config()
    if fecha in config['dias_bloqueados']:
        config['dias_bloqueados'].remove(fecha)
        guardar_config(config)

        # Notificar al admin sobre el desbloqueo
        try:
            notificar_admin('desbloqueo_dia', fecha)
        except Exception as e:
            print(f"❌ Error al notificar admin sobre desbloqueo: {e}")
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
    from notifications import obtener_notificaciones_pendientes
    notificaciones = obtener_notificaciones_pendientes()
    return jsonify({
        'total': len(notificaciones),
        'notificaciones': notificaciones
    })


@app.route('/marcar_enviada/<int:index>', methods=['POST'])
def marcar_enviada(index):
    """Marcar una notificación como enviada"""
    try:
        from notifications import obtener_notificaciones_pendientes, marcar_notificacion_enviada
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
        from db_maintenance import obtener_estadisticas_db
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
        from db_maintenance import mantenimiento_completo
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


if __name__ == '__main__':
    # El puerto lo asigna automáticamente la plataforma cloud
    port = int(os.environ.get('PORT', 9000))
    app.run(host='0.0.0.0', port=port, debug=False)
