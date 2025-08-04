#!/usr/bin/env python3
"""
Test final completo para verificar que TurnosBot está funcionando después del fix
"""

import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.core.config import BotConfig
    from src.core.bot_core import obtener_fechas_disponibles, obtener_horarios_disponibles
    print("✅ Imports exitosos")
except ImportError as e:
    print(f"❌ Error en imports: {e}")
    sys.exit(1)

def test_config():
    """Test configuración"""
    try:
        config = BotConfig()
        print("✅ Config inicializada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en config: {e}")
        return False

def test_fechas():
    """Test fechas disponibles"""
    try:
        fechas = obtener_fechas_disponibles()
        print(f"✅ Fechas disponibles: {len(fechas)}")
        for fecha in fechas[:3]:  # Mostrar solo las primeras 3
            print(f"   📅 {fecha}")
        return len(fechas) > 0
    except Exception as e:
        print(f"❌ Error en fechas: {e}")
        return False

def test_horarios_hoy():
    """Test horarios para hoy"""
    try:
        hoy = datetime.now().strftime('%Y-%m-%d')
        horarios = obtener_horarios_disponibles(hoy)
        print(f"✅ Horarios para hoy ({hoy}): {len(horarios)}")
        for i, horario in enumerate(horarios, 1):
            print(f"   ⏰ {i}. {horario}")
        return len(horarios) > 0
    except Exception as e:
        print(f"❌ Error en horarios hoy: {e}")
        return False

def test_horarios_manana():
    """Test horarios para mañana"""
    try:
        manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        horarios = obtener_horarios_disponibles(manana)
        print(f"✅ Horarios para mañana ({manana}): {len(horarios)}")
        return len(horarios) > 0
    except Exception as e:
        print(f"❌ Error en horarios mañana: {e}")
        return False

def main():
    print("🔍 TEST FINAL COMPLETO - TURNOSBOT")
    print("=" * 50)
    
    tests = [
        ("Configuración", test_config),
        ("Fechas disponibles", test_fechas),
        ("Horarios hoy", test_horarios_hoy),
        ("Horarios mañana", test_horarios_manana),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        print(f"\n📋 {nombre}:")
        resultado = test_func()
        resultados.append(resultado)
    
    print("\n" + "=" * 50)
    if all(resultados):
        print("🎉 TODOS LOS TESTS PASARON")
        print("✅ TurnosBot está funcionando correctamente")
        print("🚀 Listo para desplegar en Railway")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔧 Revisar los errores arriba")
    
    return all(resultados)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
