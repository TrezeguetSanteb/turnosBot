#!/usr/bin/env python3
"""
Diagnóstico completo para Railway - Sistema de notificaciones
"""

import sys
import os
import json
import sqlite3
from datetime import datetime

# Configurar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def log_mensaje(mensaje):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {mensaje}")

def diagnosticar_configuracion():
    """Verificar configuración en Railway"""
    log_mensaje("🔧 DIAGNÓSTICO DE CONFIGURACIÓN")
    
    try:
        from core.config import config
        
        print(f"✅ Config cargado correctamente")
        print(f"   Intervalo: {config.NOTIFICATION_INTERVAL} segundos")
        print(f"   WhatsApp configurado: {'✅ Sí' if config.has_whatsapp() else '❌ No'}")
        
        if config.has_whatsapp():
            print(f"   Admin phone: {'✅ Configurado' if config.get_admin_phone_number() else '❌ No configurado'}")
        
        # Variables de entorno críticas
        vars_criticas = ['WHATSAPP_ACCESS_TOKEN', 'WHATSAPP_PHONE_NUMBER_ID', 'ADMIN_PHONE_NUMBER']
        for var in vars_criticas:
            valor = os.getenv(var)
            if valor:
                masked = valor[:8] + "..." if len(valor) > 8 else "***"
                print(f"   {var}: {masked}")
            else:
                print(f"   {var}: ❌ NO CONFIGURADA")
                
    except Exception as e:
        print(f"❌ Error cargando config: {e}")
        import traceback
        traceback.print_exc()

def diagnosticar_base_datos():
    """Verificar estado de la base de datos"""
    log_mensaje("🗄️ DIAGNÓSTICO DE BASE DE DATOS")
    
    try:
        # Verificar archivo de BD
        db_path = 'data/turnos.db'
        if os.path.exists(db_path):
            print(f"✅ Base de datos existe: {db_path}")
            
            # Verificar tablas
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = [row[0] for row in cursor.fetchall()]
            print(f"   Tablas: {tablas}")
            
            # Verificar turnos
            if 'turno' in tablas:
                cursor.execute("SELECT COUNT(*) FROM turno")
                count_turnos = cursor.fetchone()[0]
                print(f"   Turnos en BD: {count_turnos}")
                
                if count_turnos > 0:
                    cursor.execute("SELECT id, nombre, telefono FROM turno LIMIT 3")
                    turnos_sample = cursor.fetchall()
                    print("   Últimos turnos:")
                    for turno in turnos_sample:
                        print(f"     ID {turno[0]}: {turno[1]} - {turno[2]}")
            
            conn.close()
        else:
            print(f"❌ Base de datos no existe: {db_path}")
            
    except Exception as e:
        print(f"❌ Error verificando BD: {e}")

def diagnosticar_notificaciones():
    """Verificar sistema de notificaciones"""
    log_mensaje("📨 DIAGNÓSTICO DE NOTIFICACIONES")
    
    try:
        # Verificar archivos de notificaciones
        archivos = {
            'admin': 'data/admin_notifications.json',
            'usuarios': 'data/notifications_log.json'
        }
        
        for tipo, archivo in archivos.items():
            if os.path.exists(archivo):
                with open(archivo, 'r') as f:
                    data = json.load(f)
                print(f"✅ {tipo.capitalize()}: {len(data)} notificaciones")
                
                # Mostrar últimas notificaciones
                if data:
                    print(f"   Últimas notificaciones {tipo}:")
                    for notif in data[-2:]:  # Últimas 2
                        timestamp = notif.get('timestamp', 'N/A')[:19]
                        tipo_notif = notif.get('tipo', 'N/A')
                        enviada = notif.get('enviada', notif.get('enviado', False))
                        print(f"     {tipo_notif} - {timestamp} - Enviada: {enviada}")
            else:
                print(f"⚠️ {tipo.capitalize()}: Archivo no existe")
                
        # Verificar funciones de notificaciones
        print("\n🔍 Verificando funciones de notificaciones:")
        
        from services.notifications import obtener_notificaciones_pendientes
        notifs_usuarios = obtener_notificaciones_pendientes()
        print(f"   Notificaciones usuarios pendientes: {len(notifs_usuarios)}")
        
        from admin.notifications import contar_notificaciones_pendientes
        notifs_admin = contar_notificaciones_pendientes()
        print(f"   Notificaciones admin pendientes: {notifs_admin}")
        
    except Exception as e:
        print(f"❌ Error verificando notificaciones: {e}")
        import traceback
        traceback.print_exc()

def diagnosticar_daemon():
    """Verificar si el daemon puede ejecutarse"""
    log_mensaje("🤖 DIAGNÓSTICO DEL DAEMON")
    
    try:
        # Verificar imports del daemon
        from services.daemon import main as daemon_main
        print("✅ Daemon se puede importar")
        
        # Verificar bot_sender
        print("\n🔍 Probando bot_sender:")
        import subprocess
        result = subprocess.run(
            [sys.executable, 'src/bots/senders/bot_sender.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"   Return code: {result.returncode}")
        if result.stdout:
            print("   Output:")
            for line in result.stdout.split('\n')[:10]:  # Primeras 10 líneas
                if line.strip():
                    print(f"     {line}")
        
        if result.stderr:
            print("   Errores:")
            for line in result.stderr.split('\n')[:5]:  # Primeros 5 errores
                if line.strip():
                    print(f"     {line}")
                    
    except Exception as e:
        print(f"❌ Error verificando daemon: {e}")

def diagnosticar_whatsapp():
    """Verificar conectividad con WhatsApp"""
    log_mensaje("📱 DIAGNÓSTICO DE WHATSAPP")
    
    try:
        from core.config import config
        
        if not config.has_whatsapp():
            print("❌ WhatsApp no configurado")
            return
            
        # Intentar importar el sender
        from bots.senders.whatsapp_sender import whatsapp_sender
        print("✅ WhatsApp sender importado")
        
        # Verificar si podemos hacer una llamada de test (sin enviar mensaje real)
        print("   Verificando configuración WhatsApp...")
        
        # Solo verificar que las variables están configuradas
        access_token = config.WHATSAPP_ACCESS_TOKEN
        phone_id = config.WHATSAPP_PHONE_NUMBER_ID
        
        if access_token and phone_id:
            print(f"   ✅ Token configurado: {access_token[:20]}...")
            print(f"   ✅ Phone ID configurado: {phone_id}")
            
            # Opcional: Test básico de conectividad (sin enviar mensaje)
            import requests
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Solo verificar que el endpoint responde
            url = f"https://graph.facebook.com/v17.0/{phone_id}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                print(f"   API Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ WhatsApp API responde correctamente")
                else:
                    print(f"   ⚠️ WhatsApp API respuesta inesperada: {response.text[:100]}")
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Error conectando a WhatsApp API: {e}")
        else:
            print("   ❌ Tokens de WhatsApp incompletos")
            
    except Exception as e:
        print(f"❌ Error verificando WhatsApp: {e}")

def diagnosticar_panel_cancelacion():
    """Verificar flujo específico de cancelación desde panel"""
    log_mensaje("🎯 DIAGNÓSTICO FLUJO DE CANCELACIÓN")
    
    try:
        # Verificar imports del panel
        from admin.panel import app
        print("✅ Panel se puede importar")
        
        # Verificar funciones críticas
        from core.database import eliminar_turno_admin, obtener_todos_los_turnos
        from services.notifications import notificar_cancelacion_turno
        
        print("✅ Funciones de cancelación disponibles")
        
        # Verificar que hay turnos para cancelar
        turnos = obtener_todos_los_turnos()
        print(f"   Turnos disponibles: {len(turnos)}")
        
        if turnos:
            ultimo_turno = turnos[-1]
            print(f"   Último turno: ID {ultimo_turno[0]} - {ultimo_turno[1]} - {ultimo_turno[4]}")
            
            # Simular creación de notificación (sin eliminar turno real)
            print("\n🧪 Simulando creación de notificación:")
            turno_id, nombre, fecha, hora, telefono = ultimo_turno
            
            # Solo crear la notificación sin eliminar el turno
            notificar_cancelacion_turno(turno_id, nombre, fecha, hora, telefono)
            print(f"   ✅ Notificación creada para {telefono}")
            
            # Verificar que se creó
            from services.notifications import obtener_notificaciones_pendientes
            notifs = obtener_notificaciones_pendientes()
            notif_nueva = [n for n in notifs if n.get('telefono') == telefono]
            print(f"   📨 Notificaciones para {telefono}: {len(notif_nueva)}")
            
    except Exception as e:
        print(f"❌ Error verificando flujo de cancelación: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🔍 DIAGNÓSTICO COMPLETO RAILWAY - TURNOSBOT")
    print("=" * 60)
    print()
    
    # Información del entorno
    print(f"🌐 Entorno: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Local'}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print()
    
    diagnosticar_configuracion()
    print()
    diagnosticar_base_datos()
    print()
    diagnosticar_notificaciones()
    print()
    diagnosticar_daemon()
    print()
    diagnosticar_whatsapp()
    print()
    diagnosticar_panel_cancelacion()
    
    log_mensaje("🎯 DIAGNÓSTICO COMPLETADO")
    print("\n📋 Revisa los resultados arriba para identificar el problema.")

if __name__ == '__main__':
    main()
