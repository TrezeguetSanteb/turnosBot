"""
Gestión centralizada de rutas del proyecto.
Asegura que todos los módulos usen las rutas correctas independientemente de estructura.
"""

import os

# Obtener la raíz del proyecto (2 niveles arriba desde src/core/)
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))


def get_project_root():
    """Obtiene la ruta raíz del proyecto"""
    return PROJECT_ROOT


def get_data_path(filename=''):
    """Obtiene ruta en la carpeta data/"""
    data_dir = os.path.join(PROJECT_ROOT, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, filename) if filename else data_dir


def get_config_path(filename=''):
    """Obtiene ruta en la carpeta config/"""
    config_dir = os.path.join(PROJECT_ROOT, 'config')
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, filename) if filename else config_dir


def get_logs_path(filename=''):
    """Obtiene ruta en la carpeta data/logs/"""
    logs_dir = os.path.join(PROJECT_ROOT, 'data', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return os.path.join(logs_dir, filename) if filename else logs_dir


def get_templates_path(filename=''):
    """Obtiene ruta en la carpeta templates/"""
    templates_dir = os.path.join(PROJECT_ROOT, 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    return os.path.join(templates_dir, filename) if filename else templates_dir


def get_static_path(filename=''):
    """Obtiene ruta en la carpeta static/"""
    static_dir = os.path.join(PROJECT_ROOT, 'static')
    os.makedirs(static_dir, exist_ok=True)
    return os.path.join(static_dir, filename) if filename else static_dir


# Rutas específicas más usadas
DB_PATH = get_data_path('turnos.db')
SCHEMA_PATH = get_data_path('schema.sql')
CONFIG_JSON_PATH = get_config_path('config.json')
ADMIN_NOTIFICATIONS_PATH = get_data_path('admin_notifications.json')
NOTIFICATIONS_LOG_PATH = get_data_path('notifications_log.json')
