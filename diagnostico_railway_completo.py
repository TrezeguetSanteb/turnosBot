#!/usr/bin/env python3
"""
Script de diagnóstico para Railway - Verificar estado real del bot en producción
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def verificar_entorno():
    """Verificar si estamos en Railway o local"""
    print("🔍 === VERIFICACIÓN DE ENTORNO ===")
    
    railway_vars = [
        'RAILWAY_STATIC_URL',
        'RAILWAY_ENVIRONMENT', 
        'RAILWAY_SERVICE_NAME',
        'RAILWAY_PROJECT_NAME',
        'RAILWAY_GIT_COMMIT_SHA'
    ]
    
    is_railway = any(os.environ.get(var) for var in railway_vars)
    
    if is_railway:
        print("🚂 EJECUTANDO EN RAILWAY")
        for var in railway_vars:
            value = os.environ.get(var)
            if value:
                print(f"   {var}: {value}")
    else:
        print("💻 EJECUTANDO EN LOCAL")
    
    print(f"📅 Fecha/hora actual: {datetime.now()}")
    return is_railway

def verificar_database_railway():
    """Verificar estado de la base de datos en Railway"""
    print("\n🔍 === VERIFICACIÓN BASE DE DATOS ===")
    
    try:
        # Verificar si existe el archivo de BD
        db_path = os.path.join(os.path.dirname(__file__), 'data', 'turnos.db')
        print(f"📂 Ruta BD: {db_path}")
        print(f"📂 BD existe: {os.path.exists(db_path)}")
        
        if os.path.exists(db_path):
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar tabla turnos
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='turnos'")
            tabla_existe = cursor.fetchone() is not None
            print(f"📋 Tabla 'turnos' existe: {tabla_existe}")
            
            if tabla_existe:
                # Contar turnos totales
                cursor.execute("SELECT COUNT(*) FROM turnos")
                total = cursor.fetchone()[0]
                print(f"📊 Total turnos: {total}")
                
                # Turnos para hoy
                hoy = datetime.now().strftime('%Y-%m-%d')
                cursor.execute("SELECT COUNT(*) FROM turnos WHERE fecha = ?", (hoy,))
                turnos_hoy = cursor.fetchone()[0]
                print(f"📅 Turnos para hoy ({hoy}): {turnos_hoy}")
                
                # Sample de turnos
                cursor.execute("SELECT fecha, hora, estado FROM turnos WHERE fecha >= ? ORDER BY fecha, hora LIMIT 10", (hoy,))
                turnos_sample = cursor.fetchall()
                print("📋 Sample turnos próximos:")
                for turno in turnos_sample:
                    print(f"   {turno[0]} {turno[1]} - {turno[2]}")
            
            conn.close()
            return True
        else:
            print("❌ Archivo de base de datos no existe")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando BD: {e}")
        return False

def verificar_configuracion_railway():
    """Verificar configuración en Railway"""
    print("\n🔍 === VERIFICACIÓN CONFIGURACIÓN ===")
    
    # Variables críticas de WhatsApp
    whatsapp_vars = {
        'WHATSAPP_ACCESS_TOKEN': 'Token de acceso WhatsApp',
        'WHATSAPP_PHONE_NUMBER_ID': 'ID número de teléfono',
        'WHATSAPP_VERIFY_TOKEN': 'Token de verificación',
        'ADMIN_PHONE_NUMBER': 'Número del admin'
    }
    
    config_ok = True
    for var, desc in whatsapp_vars.items():
        value = os.environ.get(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {desc}: {masked}")
        else:
            print(f"❌ {desc}: NO CONFIGURADO")
            config_ok = False
    
    # Verificar config.json
    config_file = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
    print(f"\n📁 Config file: {config_file}")
    print(f"📁 Existe: {os.path.exists(config_file)}")
    
    if os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            print(f"📋 Configuración cargada: {list(config_data.keys())}")
            
            # Mostrar horarios configurados
            if 'hora_inicio' in config_data and 'hora_fin' in config_data:
                print(f"⏰ Horarios: {config_data['hora_inicio']} - {config_data['hora_fin']}")
            if 'dias_bloqueados' in config_data:
                print(f"🚫 Días bloqueados: {config_data['dias_bloqueados']}")
                
        except Exception as e:
            print(f"❌ Error leyendo config: {e}")
            config_ok = False
    
    return config_ok

def test_bot_functions_railway():
    """Test de funciones del bot en Railway"""
    print("\n🔍 === TEST FUNCIONES BOT ===")
    
    try:
        from core.bot_core import obtener_fechas_disponibles, obtener_horarios_disponibles
        
        # Test fechas
        fechas = obtener_fechas_disponibles()
        print(f"📅 Fechas disponibles: {len(fechas)}")
        for i, fecha in enumerate(fechas[:3], 1):
            print(f"   {i}) {fecha['etiqueta']} - {fecha['fecha']}")
        
        # Test horarios para hoy
        if fechas:
            hoy = fechas[0]['fecha']  # Primera fecha (hoy)
            horarios = obtener_horarios_disponibles(hoy)
            print(f"⏰ Horarios para hoy ({hoy}): {len(horarios)}")
            for hora in horarios[:5]:  # Mostrar solo primeros 5
                print(f"   - {hora}")
            
            return len(horarios) > 0
        else:
            print("❌ No hay fechas disponibles")
            return False
            
    except Exception as e:
        print(f"❌ Error en test funciones: {e}")
        import traceback
        traceback.print_exc()
        return False

def simular_webhook_railway():
    """Simular recepción de webhook en Railway"""
    print("\n🔍 === SIMULACIÓN WEBHOOK RAILWAY ===")
    
    try:
        from bots.whatsapp_bot import app
        
        # Verificar que la app Flask existe
        print(f"✅ App Flask cargada: {app}")
        print(f"✅ Rutas disponibles: {[rule.rule for rule in app.url_map.iter_rules()]}")
        
        # Test de verificación de webhook
        verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mi_token_verificacion_whatsapp')
        print(f"🔑 Token de verificación configurado: {verify_token[:8]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error simulando webhook: {e}")
        import traceback
        traceback.print_exc()
        return False

def crear_reporte_railway():
    """Crear reporte completo para Railway"""
    print("\n📋 === REPORTE COMPLETO RAILWAY ===")
    
    # Información del entorno
    is_railway = verificar_entorno()
    db_ok = verificar_database_railway()
    config_ok = verificar_configuracion_railway()
    functions_ok = test_bot_functions_railway()
    webhook_ok = simular_webhook_railway()
    
    print("\n" + "="*60)
    print("📊 RESUMEN DIAGNÓSTICO RAILWAY:")
    print(f"   🚂 Entorno Railway: {'✅' if is_railway else '❌'}")
    print(f"   🗄️  Base de datos: {'✅' if db_ok else '❌'}")
    print(f"   ⚙️  Configuración: {'✅' if config_ok else '❌'}")
    print(f"   🤖 Funciones bot: {'✅' if functions_ok else '❌'}")
    print(f"   🔗 Webhook setup: {'✅' if webhook_ok else '❌'}")
    
    if all([db_ok, config_ok, functions_ok, webhook_ok]):
        print("\n✅ TODO ESTÁ BIEN EN RAILWAY")
        print("🔍 El problema puede ser:")
        print("   1. Webhook de Meta no configurado correctamente")
        print("   2. URL de Railway no accesible desde Meta")
        print("   3. Logs de Railway muestran errores específicos")
    else:
        print("\n❌ PROBLEMAS DETECTADOS")
        print("🔧 Revisar elementos marcados con ❌")
    
    return all([db_ok, config_ok, functions_ok, webhook_ok])

def main():
    print("🚂 === DIAGNÓSTICO RAILWAY TURNOSBOT ===")
    print(f"📅 {datetime.now()}")
    print("="*70)
    
    crear_reporte_railway()

if __name__ == "__main__":
    main()
