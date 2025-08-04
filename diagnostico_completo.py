#!/usr/bin/env python3
"""
Diagnóstico completo para identificar por qué no funcionan los turnos
"""

import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test de imports básicos"""
    print("🔍 === TEST DE IMPORTS ===")
    try:
        from core.config import BotConfig
        print("✅ BotConfig importado")
    except Exception as e:
        print(f"❌ Error importando BotConfig: {e}")
        return False
    
    try:
        from core.bot_core import obtener_fechas_disponibles, obtener_horarios_disponibles
        print("✅ Funciones de bot_core importadas")
    except Exception as e:
        print(f"❌ Error importando bot_core: {e}")
        return False
    
    try:
        from core.database import get_db_connection
        print("✅ Database importada")
    except Exception as e:
        print(f"❌ Error importando database: {e}")
        return False
    
    return True

def test_database():
    """Test de conexión a base de datos"""
    print("\n🔍 === TEST DE BASE DE DATOS ===")
    try:
        from core.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar estructura de tabla turno
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='turno'")
        if cursor.fetchone():
            print("✅ Tabla 'turno' existe")
        else:
            print("❌ Tabla 'turno' no existe")
            return False
        
        # Contar turnos
        cursor.execute("SELECT COUNT(*) FROM turno")
        total_turnos = cursor.fetchone()[0]
        print(f"📊 Total turnos en BD: {total_turnos}")
        
        # Turnos para hoy
        hoy = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM turno WHERE fecha = ?", (hoy,))
        turnos_hoy = cursor.fetchone()[0]
        print(f"📅 Turnos para hoy ({hoy}): {turnos_hoy}")
        
        # Ver algunos turnos de hoy
        cursor.execute("SELECT fecha, hora FROM turno WHERE fecha = ? LIMIT 10", (hoy,))
        turnos_detalle = cursor.fetchall()
        print("📋 Detalle turnos hoy:")
        for turno in turnos_detalle:
            print(f"   {turno[0]} {turno[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test de configuración"""
    print("\n🔍 === TEST DE CONFIGURACIÓN ===")
    try:
        from core.config import BotConfig
        config = BotConfig()
        
        print(f"📋 Intervalo notificaciones: {config.NOTIFICATION_INTERVAL} segundos")
        print(f"📋 Log level: {config.LOG_LEVEL}")
        
        # Verificar archivo config.json si existe
        config_file = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
        if os.path.exists(config_file):
            print(f"✅ Archivo config.json existe: {config_file}")
            import json
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            print(f"📋 Configuración cargada: {list(config_data.keys())}")
        else:
            print(f"⚠️  Archivo config.json no existe: {config_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bot_core_functions():
    """Test de las funciones principales"""
    print("\n🔍 === TEST DE FUNCIONES BOT_CORE ===")
    try:
        from core.bot_core import obtener_fechas_disponibles, obtener_horarios_disponibles
        
        # Test fechas
        print("📅 Testing obtener_fechas_disponibles...")
        fechas = obtener_fechas_disponibles()
        print(f"✅ Fechas obtenidas: {len(fechas)}")
        for i, fecha in enumerate(fechas[:3]):
            print(f"   {i+1}. {fecha}")
        
        # Test horarios para hoy
        print("\n⏰ Testing obtener_horarios_disponibles para hoy...")
        hoy = datetime.now().strftime('%Y-%m-%d')
        horarios = obtener_horarios_disponibles(hoy)
        print(f"✅ Horarios para hoy ({hoy}): {len(horarios)}")
        for i, horario in enumerate(horarios):
            print(f"   {i+1}. {horario}")
        
        # Test horarios para mañana
        print("\n⏰ Testing obtener_horarios_disponibles para mañana...")
        manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        horarios_manana = obtener_horarios_disponibles(manana)
        print(f"✅ Horarios para mañana ({manana}): {len(horarios_manana)}")
        
        return len(horarios) > 0
        
    except Exception as e:
        print(f"❌ Error en funciones bot_core: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_timezone():
    """Test de zona horaria"""
    print("\n🔍 === TEST DE ZONA HORARIA ===")
    try:
        import pytz
        from datetime import datetime
        
        # Hora UTC
        utc_now = datetime.utcnow()
        print(f"🌍 UTC: {utc_now}")
        
        # Hora local del sistema
        local_now = datetime.now()
        print(f"🏠 Sistema local: {local_now}")
        
        # Hora Argentina
        arg_tz = pytz.timezone('America/Argentina/Buenos_Aires')
        arg_now = datetime.now(arg_tz)
        print(f"🇦🇷 Argentina: {arg_now}")
        
        # Verificar si las funciones de zona horaria están disponibles
        try:
            from core.bot_core import obtener_hora_argentina, obtener_fecha_argentina
            hora_arg = obtener_hora_argentina()
            fecha_arg = obtener_fecha_argentina()
            print(f"✅ Función hora Argentina: {hora_arg}")
            print(f"✅ Función fecha Argentina: {fecha_arg}")
        except ImportError:
            print("⚠️  Funciones de zona horaria no disponibles en bot_core")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en zona horaria: {e}")
        return False

def test_whatsapp_simulation():
    """Simular una consulta de WhatsApp"""
    print("\n🔍 === SIMULACIÓN CONSULTA WHATSAPP ===")
    try:
        from core.bot_core import obtener_fechas_disponibles, obtener_horarios_disponibles
        
        print("📱 Simulando: Usuario pregunta por turnos disponibles")
        
        # Paso 1: Obtener fechas
        fechas = obtener_fechas_disponibles()
        print(f"✅ Paso 1 - Fechas disponibles: {len(fechas)}")
        
        if len(fechas) == 0:
            print("❌ PROBLEMA: No hay fechas disponibles")
            return False
        
        # Paso 2: Usuario selecciona hoy
        hoy = datetime.now().strftime('%Y-%m-%d')
        print(f"📅 Paso 2 - Usuario selecciona hoy: {hoy}")
        
        # Paso 3: Obtener horarios para hoy
        horarios = obtener_horarios_disponibles(hoy)
        print(f"✅ Paso 3 - Horarios para hoy: {len(horarios)}")
        
        if len(horarios) == 0:
            print("❌ PROBLEMA: No hay horarios disponibles para hoy")
            print("🔍 Investigando causa...")
            
            # Verificar en BD directamente
            from core.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Todos los turnos de hoy
            cursor.execute("SELECT fecha, hora, estado FROM turnos WHERE fecha = ?", (hoy,))
            todos_turnos_hoy = cursor.fetchall()
            print(f"📊 Turnos totales en BD para hoy: {len(todos_turnos_hoy)}")
            
            for turno in todos_turnos_hoy:
                print(f"   {turno[0]} {turno[1]} - Estado: {turno[2]}")
            
            # Verificar si es domingo (bloqueado por defecto)
            fecha_obj = datetime.strptime(hoy, '%Y-%m-%d')
            dia_semana = fecha_obj.weekday()  # 0=lunes, 6=domingo
            if dia_semana == 6:
                print("⚠️  NOTA: Hoy es domingo - puede estar bloqueado por defecto")
            
            conn.close()
            return False
        
        print("✅ Simulación exitosa - El bot debería funcionar")
        return True
        
    except Exception as e:
        print(f"❌ Error en simulación WhatsApp: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 === DIAGNÓSTICO COMPLETO TURNOSBOT ===")
    print(f"📅 Fecha/hora: {datetime.now()}")
    print("=" * 60)
    
    tests = [
        ("Imports básicos", test_imports),
        ("Base de datos", test_database),
        ("Configuración", test_config),
        ("Funciones bot_core", test_bot_core_functions),
        ("Zona horaria", test_timezone),
        ("Simulación WhatsApp", test_whatsapp_simulation),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        print(f"\n{'='*20} {nombre.upper()} {'='*20}")
        try:
            resultado = test_func()
            resultados.append(resultado)
        except Exception as e:
            print(f"❌ Error fatal en {nombre}: {e}")
            resultados.append(False)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL:")
    for i, (nombre, _) in enumerate(tests):
        estado = "✅ PASS" if resultados[i] else "❌ FAIL"
        print(f"   {estado} {nombre}")
    
    if all(resultados):
        print("\n🎉 TODOS LOS TESTS PASARON")
        print("✅ El problema puede ser de configuración o entorno")
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON")
        print("🔧 Revisar los errores específicos arriba")
    
    return all(resultados)

if __name__ == "__main__":
    main()
