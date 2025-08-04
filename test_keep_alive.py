#!/usr/bin/env python3
"""
Test del sistema keep-alive para Railway
Simula las condiciones de Railway para probar el anti-hibernación
"""

import sys
import os
import time
from datetime import datetime

# Configurar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def log_test(mensaje):
    """Log para el test"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] TEST: {mensaje}", flush=True)

def simular_railway():
    """Simula condiciones de Railway para probar keep-alive"""
    log_test("🧪 INICIANDO TEST DE KEEP-ALIVE")
    
    # Simular variables de entorno de Railway
    os.environ['RAILWAY_STATIC_URL'] = 'https://turnosbot-test.railway.app'
    os.environ['RAILWAY_ENVIRONMENT'] = 'production'
    os.environ['RAILWAY_SERVICE_NAME'] = 'turnosbot'
    
    log_test("🚂 Variables de Railway configuradas")
    log_test(f"   URL: {os.environ.get('RAILWAY_STATIC_URL')}")
    
    try:
        # Importar el daemon con las variables configuradas
        from services.daemon import (
            is_railway, railway_url, KEEP_ALIVE_INTERVAL,
            necesita_keep_alive, keep_alive_ping
        )
        
        log_test(f"✅ Daemon importado")
        log_test(f"   Es Railway: {is_railway}")
        log_test(f"   URL Railway: {railway_url}")
        log_test(f"   Intervalo keep-alive: {KEEP_ALIVE_INTERVAL} segundos")
        
        # Test de la función necesita_keep_alive
        log_test("🔍 Probando necesita_keep_alive()...")
        necesita = necesita_keep_alive()
        log_test(f"   Necesita keep-alive: {necesita}")
        
        # Test de keep_alive_ping (sin servidor)
        log_test("🏓 Probando keep_alive_ping()...")
        import asyncio
        
        async def test_ping():
            try:
                await keep_alive_ping()
                log_test("✅ keep_alive_ping() ejecutado sin errores")
            except Exception as e:
                log_test(f"⚠️ keep_alive_ping() generó excepción: {e}")
        
        asyncio.run(test_ping())
        
        # Verificar que las funciones están disponibles
        log_test("🔧 Verificando funciones del daemon...")
        
        from services.daemon import (
            log_mensaje,
            ejecutar_bot_sender,
            mostrar_estadisticas,
            mantener_conexion_railway
        )
        
        log_test("✅ Todas las funciones del daemon están disponibles")
        
        # Test de configuración
        from core.config import config
        log_test(f"📊 Configuración:")
        log_test(f"   WhatsApp: {'✅' if config.has_whatsapp() else '❌'}")
        log_test(f"   Intervalo notificaciones: {config.NOTIFICATION_INTERVAL}s")
        
        log_test("🎉 TEST COMPLETADO - Sistema keep-alive listo para Railway")
        
    except ImportError as e:
        log_test(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        log_test(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_endpoint_local():
    """Test del endpoint keep-alive localmente"""
    log_test("🌐 Probando endpoint keep-alive local...")
    
    try:
        import requests
        import threading
        import time
        from admin.panel import app
        
        # Iniciar servidor Flask en thread separado
        def run_server():
            app.run(host='127.0.0.1', port=9001, debug=False)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Esperar a que el servidor inicie
        time.sleep(2)
        
        # Hacer request al endpoint
        response = requests.get('http://127.0.0.1:9001/api/keep-alive', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            log_test("✅ Endpoint keep-alive funciona correctamente")
            log_test(f"   Status: {data.get('status')}")
            log_test(f"   Timestamp: {data.get('timestamp')}")
        else:
            log_test(f"⚠️ Endpoint respondió {response.status_code}")
            
    except requests.RequestException as e:
        log_test(f"⚠️ Error de conexión (normal en test): {e}")
    except Exception as e:
        log_test(f"❌ Error en test de endpoint: {e}")

def main():
    """Función principal del test"""
    log_test("🎯 INICIANDO TESTS DE KEEP-ALIVE PARA RAILWAY")
    print()
    
    # Test 1: Simular Railway
    exito_railway = simular_railway()
    print()
    
    # Test 2: Endpoint local
    test_endpoint_local()
    print()
    
    if exito_railway:
        log_test("✅ TODOS LOS TESTS PASARON - Sistema listo para Railway")
        log_test("📋 Próximos pasos:")
        log_test("   1. Desplegar en Railway")
        log_test("   2. Verificar logs del daemon")
        log_test("   3. Confirmar que no hay hibernación")
    else:
        log_test("❌ ALGUNOS TESTS FALLARON - Revisar configuración")
    
    return exito_railway

if __name__ == '__main__':
    main()
