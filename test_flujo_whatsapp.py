#!/usr/bin/env python3
"""
Test específico para simular el flujo exacto del bot de WhatsApp
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_flujo_bot_whatsapp():
    """Simular exactamente lo que hace el bot de WhatsApp"""
    print("🤖 === SIMULACIÓN FLUJO BOT WHATSAPP ===")
    
    try:
        from core.bot_core import obtener_fechas_disponibles, obtener_horarios_disponibles
        
        # Paso 1: Usuario pide reservar turno
        print("👤 Usuario: Selecciona opción 1 (Reservar turno)")
        print("🤖 Bot: Pide nombre")
        
        # Paso 2: Usuario ingresa nombre  
        print("👤 Usuario: Ingresa nombre")
        print("🤖 Bot: Muestra fechas disponibles")
        
        # Obtener fechas (lo que hace el bot)
        fechas = obtener_fechas_disponibles()
        print(f"📅 Fechas obtenidas por el bot: {len(fechas)}")
        
        for i, fecha in enumerate(fechas, 1):
            print(f"   {i}) {fecha['etiqueta'].title()} ({fecha['fecha_legible']})")
        
        if len(fechas) == 0:
            print("❌ PROBLEMA: Bot no obtiene fechas")
            return False
        
        # Paso 3: Usuario selecciona hoy (opción 1)
        print("\n👤 Usuario: Selecciona opción 1 (hoy)")
        opcion = 1
        if 1 <= opcion <= len(fechas):
            fecha_seleccionada = fechas[opcion-1]['fecha']
            print(f"📅 Fecha seleccionada: {fecha_seleccionada}")
            
            # Paso 4: Bot obtiene horarios para esa fecha
            print("🤖 Bot: Obteniendo horarios disponibles...")
            horarios = obtener_horarios_disponibles(fecha_seleccionada)
            print(f"⏰ Horarios obtenidos: {len(horarios)}")
            
            if horarios:
                print("✅ Bot mostraría horarios:")
                for i, hora in enumerate(horarios, 1):
                    print(f"   {i}) {hora}")
                return True
            else:
                print(f"❌ PROBLEMA: Bot dice 'No hay horarios disponibles para {fechas[opcion-1]['fecha_legible']}'")
                print("🔍 Investigando causa...")
                
                # Debug adicional
                print(f"🔍 Fecha exacta enviada a obtener_horarios_disponibles: '{fecha_seleccionada}'")
                print(f"🔍 Tipo de fecha: {type(fecha_seleccionada)}")
                
                return False
        else:
            print("❌ Opción de fecha inválida")
            return False
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_horarios_directos():
    """Test directo de la función obtener_horarios_disponibles"""
    print("\n🔍 === TEST DIRECTO HORARIOS ===")
    
    try:
        from core.bot_core import obtener_horarios_disponibles
        
        # Test con fecha de hoy en diferentes formatos
        hoy = datetime.now().strftime('%Y-%m-%d')
        print(f"📅 Probando con fecha hoy: '{hoy}'")
        
        horarios1 = obtener_horarios_disponibles(hoy)
        print(f"⏰ Resultado 1: {len(horarios1)} horarios")
        for h in horarios1:
            print(f"   - {h}")
            
        # Test con fecha como string exactamente como la devuelve obtener_fechas_disponibles
        from core.bot_core import obtener_fechas_disponibles
        fechas = obtener_fechas_disponibles()
        if fechas:
            fecha_hoy_desde_fechas = fechas[0]['fecha']
            print(f"\n📅 Probando con fecha desde obtener_fechas_disponibles: '{fecha_hoy_desde_fechas}'")
            horarios2 = obtener_horarios_disponibles(fecha_hoy_desde_fechas)
            print(f"⏰ Resultado 2: {len(horarios2)} horarios")
            for h in horarios2:
                print(f"   - {h}")
                
            if len(horarios1) != len(horarios2):
                print("⚠️  DIFERENCIA detectada entre formatos de fecha!")
                return False
        
        return len(horarios1) > 0
        
    except Exception as e:
        print(f"❌ Error en test directo: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_debug_obtener_horarios():
    """Debug profundo de la función obtener_horarios_disponibles"""
    print("\n🔍 === DEBUG PROFUNDO OBTENER_HORARIOS ===")
    
    try:
        # Importar e inspeccionar la función
        import inspect
        from core.bot_core import obtener_horarios_disponibles
        
        # Ver el código de la función
        source = inspect.getsource(obtener_horarios_disponibles)
        print("📄 Código de obtener_horarios_disponibles:")
        print("-" * 50)
        print(source[:500] + "..." if len(source) > 500 else source)
        print("-" * 50)
        
        # Test paso a paso
        hoy = datetime.now().strftime('%Y-%m-%d')
        print(f"\n🔍 Ejecutando para fecha: {hoy}")
        
        # Llamar con debugging
        horarios = obtener_horarios_disponibles(hoy)
        print(f"✅ Resultado final: {len(horarios)} horarios")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en debug: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 === TEST FLUJO WHATSAPP BOT ===")
    print(f"📅 Fecha: {datetime.now()}")
    print("=" * 60)
    
    tests = [
        ("Flujo completo bot WhatsApp", test_flujo_bot_whatsapp),
        ("Test directo horarios", test_horarios_directos),
        ("Debug obtener_horarios", test_debug_obtener_horarios),
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
        print("\n🎉 TODO FUNCIONA - El problema debe ser otro")
    else:
        print("\n❌ PROBLEMA IDENTIFICADO - Ver detalles arriba")
    
    return all(resultados)

if __name__ == "__main__":
    main()
