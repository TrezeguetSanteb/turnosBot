#!/usr/bin/env python3
"""
Test específico para verificar funcionamiento del daemon con intervalo de 5 minutos
"""

import sys
import os
from datetime import datetime
import time

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_configuracion_daemon():
    """Test configuración del daemon"""
    print("🔍 === TEST CONFIGURACIÓN DAEMON ===")
    
    try:
        from core.config import config
        
        print(f"⏰ Intervalo configurado: {config.NOTIFICATION_INTERVAL} segundos")
        print(f"⏰ En minutos: {config.NOTIFICATION_INTERVAL/60:.1f} minutos")
        print(f"📋 Log level: {config.LOG_LEVEL}")
        print(f"🚂 Railway optimizado: {config.RAILWAY_SLEEP_OPTIMIZED}")
        print(f"⌛ Intervalo idle: {config.IDLE_CHECK_INTERVAL} segundos")
        print(f"⚡ Intervalo activo: {config.ACTIVE_CHECK_INTERVAL} segundos")
        
        # Verificar que sea exactamente 5 minutos
        if config.NOTIFICATION_INTERVAL == 300:
            print("✅ Intervalo correcto: 5 minutos (300 segundos)")
        else:
            print(f"❌ Intervalo incorrecto: {config.NOTIFICATION_INTERVAL} segundos")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_importacion_daemon():
    """Test importación del daemon"""
    print("\n🔍 === TEST IMPORTACIÓN DAEMON ===")
    
    try:
        from services.daemon import INTERVALO_SEGUNDOS, KEEP_ALIVE_INTERVAL
        
        print(f"⏰ INTERVALO_SEGUNDOS: {INTERVALO_SEGUNDOS}")
        print(f"🔄 KEEP_ALIVE_INTERVAL: {KEEP_ALIVE_INTERVAL}")
        
        if INTERVALO_SEGUNDOS == 300:
            print("✅ Daemon configurado con 5 minutos correctamente")
        else:
            print(f"❌ Daemon mal configurado: {INTERVALO_SEGUNDOS} segundos")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error importando daemon: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scripts_sender():
    """Test existencia de scripts sender"""
    print("\n🔍 === TEST SCRIPTS SENDER ===")
    
    script_path = os.path.join(os.path.dirname(__file__), 'src', 'bots', 'senders', 'bot_sender.py')
    print(f"📁 Script path: {script_path}")
    print(f"📁 Existe: {os.path.exists(script_path)}")
    
    if os.path.exists(script_path):
        print("✅ Script bot_sender.py existe")
        
        # Verificar que se puede importar
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'bots', 'senders'))
            import bot_sender
            print("✅ Script bot_sender.py se puede importar")
            return True
        except Exception as e:
            print(f"❌ Error importando bot_sender: {e}")
            return False
    else:
        print("❌ Script bot_sender.py no existe")
        return False

def test_simulacion_ciclo_daemon():
    """Simular un ciclo del daemon (sin ejecutar realmente)"""
    print("\n🔍 === SIMULACIÓN CICLO DAEMON ===")
    
    try:
        from services.daemon import INTERVALO_SEGUNDOS
        
        print(f"🔄 Simulando ciclo del daemon...")
        print(f"⏰ Intervalo configurado: {INTERVALO_SEGUNDOS} segundos")
        
        # Simular el proceso que haría el daemon
        inicio = time.time()
        print(f"🕐 Inicio simulación: {datetime.now().strftime('%H:%M:%S')}")
        
        # En lugar de esperar 5 minutos, solo simulamos
        print(f"⏳ En producción esperaría {INTERVALO_SEGUNDOS} segundos...")
        print(f"📨 Luego ejecutaría: python src/bots/senders/bot_sender.py")
        
        # Verificar que el tiempo de espera es razonable
        if INTERVALO_SEGUNDOS <= 600:  # Máximo 10 minutos
            print("✅ Intervalo de tiempo razonable para Railway")
        else:
            print("⚠️  Intervalo muy largo para Railway (>10 min)")
        
        print(f"🕐 Fin simulación: {datetime.now().strftime('%H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        return False

def test_variables_entorno():
    """Test variables de entorno relacionadas con daemon"""
    print("\n🔍 === TEST VARIABLES ENTORNO ===")
    
    variables_daemon = [
        'NOTIFICATION_INTERVAL',
        'LOG_LEVEL',
        'RAILWAY_SLEEP_OPTIMIZED',
        'IDLE_CHECK_INTERVAL', 
        'ACTIVE_CHECK_INTERVAL'
    ]
    
    for var in variables_daemon:
        valor = os.environ.get(var)
        if valor:
            print(f"✅ {var}: {valor}")
        else:
            print(f"⚠️  {var}: No configurado (usando default)")
    
    # Variables específicas de Railway
    railway_vars = [
        'RAILWAY_STATIC_URL',
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_SERVICE_NAME'
    ]
    
    railway_detectado = any(os.environ.get(var) for var in railway_vars)
    print(f"\n🚂 Railway detectado: {'✅' if railway_detectado else '❌'}")
    
    if railway_detectado:
        for var in railway_vars:
            valor = os.environ.get(var)
            if valor:
                print(f"   {var}: {valor}")
    
    return True

def main():
    print("🤖 === TEST DAEMON 5 MINUTOS ===")
    print(f"📅 Fecha: {datetime.now()}")
    print("=" * 60)
    
    tests = [
        ("Configuración daemon", test_configuracion_daemon),
        ("Importación daemon", test_importacion_daemon),
        ("Scripts sender", test_scripts_sender),
        ("Simulación ciclo", test_simulacion_ciclo_daemon),
        ("Variables entorno", test_variables_entorno),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        print(f"\n{'='*20} {nombre.upper()} {'='*20}")
        resultado = test_func()
        resultados.append(resultado)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    for i, (nombre, _) in enumerate(tests):
        estado = "✅ PASS" if resultados[i] else "❌ FAIL"
        print(f"   {estado} {nombre}")
    
    if all(resultados):
        print("\n🎉 DAEMON CONFIGURADO CORRECTAMENTE")
        print("⏰ Intervalo: 5 minutos (300 segundos)")
        print("🚀 Listo para Railway")
    else:
        print("\n❌ PROBLEMAS DETECTADOS EN DAEMON")
        print("🔧 Revisar errores específicos arriba")
    
    return all(resultados)

if __name__ == "__main__":
    main()
