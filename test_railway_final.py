#!/usr/bin/env python3
"""
DIAGNÓSTICO COMPLETO RAILWAY - CANCELACIÓN TURNOS
Script que identifica exactamente dónde falla el flujo de cancelación
"""

import os
import sys
import json
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta

def log(message):
    """Log con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)

def paso_1_verificar_entorno():
    """PASO 1: Verificar configuración básica"""
    log("🔍 PASO 1: VERIFICAR ENTORNO")
    
    # Detectar Railway
    railway_vars = ['RAILWAY_STATIC_URL', 'RAILWAY_ENVIRONMENT']
    es_railway = any(os.environ.get(var) for var in railway_vars)
    log(f"   Entorno: {'🚂 Railway' if es_railway else '💻 Local'}")
    
    # Variables WhatsApp
    whatsapp_vars = {
        'WHATSAPP_ACCESS_TOKEN': os.environ.get('WHATSAPP_ACCESS_TOKEN'),
        'WHATSAPP_PHONE_NUMBER_ID': os.environ.get('WHATSAPP_PHONE_NUMBER_ID'),
        'WHATSAPP_VERIFY_TOKEN': os.environ.get('WHATSAPP_VERIFY_TOKEN'),
        'ADMIN_PHONE_NUMBER': os.environ.get('ADMIN_PHONE_NUMBER')
    }
    
    whatsapp_ok = all(whatsapp_vars.values())
    log(f"   WhatsApp: {'✅ Configurado' if whatsapp_ok else '❌ NO configurado'}")
    
    if not whatsapp_ok:
        log("   ❌ PROBLEMA ENCONTRADO: Variables WhatsApp faltantes")
        for var, value in whatsapp_vars.items():
            status = "✅" if value else "❌"
            log(f"      {status} {var}")
        return False
    
    # Interval daemon
    interval = int(os.environ.get('NOTIFICATION_INTERVAL', '300'))
    log(f"   Daemon: cada {interval//60} minutos")
    
    return True

def paso_2_verificar_archivos():
    """PASO 2: Verificar archivos críticos"""
    log("\n🔍 PASO 2: VERIFICAR ARCHIVOS")
    
    archivos_criticos = [
        'src/admin/panel.py',
        'src/services/notifications.py',
        'src/services/daemon.py',
        'src/bots/senders/bot_sender.py'
    ]
    
    todos_ok = True
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            log(f"   ✅ {archivo}")
        else:
            log(f"   ❌ {archivo} NO EXISTE")
            todos_ok = False
    
    return todos_ok

def paso_3_verificar_base_datos():
    """PASO 3: Verificar base de datos"""
    log("\n🔍 PASO 3: VERIFICAR BASE DE DATOS")
    
    if not os.path.exists('turnos.db'):
        log("   ❌ turnos.db NO EXISTE")
        return False
    
    try:
        conn = sqlite3.connect('turnos.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM turnos")
        total = cursor.fetchone()[0]
        log(f"   ✅ Base de datos OK - {total} turnos")
        conn.close()
        return True
    except Exception as e:
        log(f"   ❌ Error en BD: {e}")
        return False

def paso_4_simular_cancelacion():
    """PASO 4: Simular cancelación desde panel"""
    log("\n🔍 PASO 4: SIMULAR CANCELACIÓN")
    
    # Crear notificación directamente como lo hace el panel
    try:
        notifications_file = 'data/notifications_log.json'
        os.makedirs('data', exist_ok=True)
        
        # Leer notificaciones existentes
        if os.path.exists(notifications_file):
            with open(notifications_file, 'r', encoding='utf-8') as f:
                notifications = json.load(f)
        else:
            notifications = []
        
        # Contar pendientes antes
        pendientes_antes = len([n for n in notifications if not n.get('enviado', False)])
        
        # Crear notificación como lo hace panel.py
        nueva_notificacion = {
            "id": f"cancelacion_{int(datetime.now().timestamp())}",
            "turno_id": 8888,
            "telefono": "+5491123456788",  # Número formato internacional
            "mensaje": "🚨 CANCELACIÓN: Tu turno del 2024-12-20 a las 16:00 ha sido cancelado por el administrador. Disculpa las molestias.",
            "tipo": "cancelacion_turno",
            "fecha_creacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "enviado": False,
            "nombre": "Test Usuario",
            "fecha": "2024-12-20",
            "hora": "16:00"
        }
        
        notifications.append(nueva_notificacion)
        
        # Guardar
        with open(notifications_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, indent=2, ensure_ascii=False)
        
        pendientes_despues = len([n for n in notifications if not n.get('enviado', False)])
        
        log(f"   ✅ Notificación creada (ID: {nueva_notificacion['id']})")
        log(f"   📊 Pendientes: {pendientes_antes} → {pendientes_despues}")
        
        return True
        
    except Exception as e:
        log(f"   ❌ Error creando notificación: {e}")
        return False

def paso_5_verificar_daemon():
    """PASO 5: Verificar que daemon procese notificaciones"""
    log("\n🔍 PASO 5: VERIFICAR DAEMON")
    
    try:
        log("   🚀 Ejecutando bot_sender.py...")
        
        # Ejecutar daemon manualmente
        resultado = subprocess.run(
            [sys.executable, 'src/bots/senders/bot_sender.py'],
            capture_output=True,
            text=True,
            timeout=45
        )
        
        log(f"   📊 Código salida: {resultado.returncode}")
        
        # Analizar output
        if resultado.stdout:
            output = resultado.stdout
            log("   📤 Output daemon:")
            
            if "No hay notificaciones pendientes" in output:
                log("      📭 Sin notificaciones pendientes")
                return False
            elif "WhatsApp no está configurado" in output:
                log("      ❌ WhatsApp no configurado en daemon")
                return False
            elif "Enviando WhatsApp" in output:
                log("      📱 Intentando enviar WhatsApp...")
                if "✅" in output:
                    log("      ✅ Envío exitoso")
                    return True
                else:
                    log("      ❌ Error en envío")
                    return False
            else:
                # Mostrar output completo para debug
                for line in output.split('\n'):
                    if line.strip():
                        log(f"      {line}")
        
        if resultado.stderr:
            log("   ⚠️ Errores:")
            for line in resultado.stderr.split('\n'):
                if line.strip():
                    log(f"      {line}")
        
        return resultado.returncode == 0
        
    except Exception as e:
        log(f"   ❌ Error ejecutando daemon: {e}")
        return False

def paso_6_verificar_estado_final():
    """PASO 6: Verificar estado final de notificaciones"""
    log("\n🔍 PASO 6: ESTADO FINAL")
    
    notifications_file = 'data/notifications_log.json'
    
    if not os.path.exists(notifications_file):
        log("   ❌ Archivo notificaciones no existe")
        return
    
    try:
        with open(notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        pendientes = [n for n in notifications if not n.get('enviado', False)]
        enviadas = [n for n in notifications if n.get('enviado', False)]
        cancelaciones_pendientes = [n for n in pendientes if n.get('tipo') == 'cancelacion_turno']
        
        log(f"   📊 Total: {len(notifications)}")
        log(f"   📤 Enviadas: {len(enviadas)}")
        log(f"   📭 Pendientes: {len(pendientes)}")
        log(f"   🚨 Cancelaciones pendientes: {len(cancelaciones_pendientes)}")
        
        if cancelaciones_pendientes:
            log("   ❌ HAY CANCELACIONES SIN ENVIAR:")
            for notif in cancelaciones_pendientes[-3:]:
                created = notif.get('fecha_creacion', 'N/A')
                phone = notif.get('telefono', 'N/A')
                turno_id = notif.get('turno_id', 'N/A')
                log(f"      - {created}: Turno {turno_id} → {phone}")
        else:
            log("   ✅ No hay cancelaciones pendientes")
            
    except Exception as e:
        log(f"   ❌ Error verificando estado: {e}")

def diagnostico_final():
    """Diagnóstico final con recomendaciones"""
    log("\n🔧 === DIAGNÓSTICO FINAL ===")
    
    # Revisar archivo de notificaciones
    notifications_file = 'data/notifications_log.json'
    
    if os.path.exists(notifications_file):
        with open(notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        pendientes = [n for n in notifications if not n.get('enviado', False)]
        cancelaciones_pendientes = [n for n in pendientes if n.get('tipo') == 'cancelacion_turno']
        
        if cancelaciones_pendientes:
            log("❌ PROBLEMA IDENTIFICADO: Hay cancelaciones pendientes de envío")
            log("\n🔍 POSIBLES CAUSAS:")
            log("1. ❌ Variables de WhatsApp mal configuradas")
            log("2. ❌ Token de WhatsApp expirado")
            log("3. ❌ Números de teléfono en formato incorrecto")
            log("4. ❌ Problemas de conectividad con API WhatsApp")
            log("5. ❌ El daemon no está ejecutándose automáticamente")
            
            log("\n🔧 SOLUCIONES RAILWAY:")
            log("1. Verificar variables de entorno en Railway Dashboard")
            log("2. Revisar logs de Railway para errores del daemon")
            log("3. Asegurar que números tengan formato +54911XXXXXXXX")
            log("4. Verificar que el token de WhatsApp esté vigente")
            log("5. Comprobar que el servicio no se esté reiniciando")
            
        else:
            log("✅ NO HAY CANCELACIONES PENDIENTES")
            log("   El sistema funciona correctamente o no hay cancelaciones recientes")
    
    log("\n💡 PASOS PARA PROBAR EN RAILWAY:")
    log("1. Ejecutar este script: python test_railway_final.py")
    log("2. Cancelar un turno real desde el panel admin")
    log("3. Verificar que aparezca como pendiente")
    log("4. Esperar 5 minutos (intervalo del daemon)")
    log("5. Verificar si la notificación fue enviada")
    log("6. Revisar logs de Railway para errores")

def main():
    """Función principal"""
    log("🏥 === DIAGNÓSTICO FINAL RAILWAY - CANCELACIÓN TURNOS ===")
    log("Ejecutando verificación completa del flujo...\n")
    
    # Ejecutar pasos secuencialmente
    pasos_exitosos = 0
    
    if paso_1_verificar_entorno():
        pasos_exitosos += 1
    
    if paso_2_verificar_archivos():
        pasos_exitosos += 1
    
    if paso_3_verificar_base_datos():
        pasos_exitosos += 1
    
    if paso_4_simular_cancelacion():
        pasos_exitosos += 1
        
        # Solo continuar si la simulación funcionó
        if paso_5_verificar_daemon():
            pasos_exitosos += 1
    
    paso_6_verificar_estado_final()
    
    # Resumen
    log(f"\n📊 === RESUMEN ===")
    log(f"Pasos exitosos: {pasos_exitosos}/5")
    
    if pasos_exitosos == 5:
        log("✅ SISTEMA FUNCIONANDO CORRECTAMENTE")
    elif pasos_exitosos >= 3:
        log("⚠️ PROBLEMA PARCIAL - Revisar configuración WhatsApp")
    else:
        log("❌ PROBLEMA GRAVE - Revisar configuración básica")
    
    diagnostico_final()

if __name__ == '__main__':
    main()
