#!/usr/bin/env python3
"""
Diagnóstico específico del problema de notificaciones directas por WhatsApp
cuando se cancela un turno desde el panel móvil en Railway
"""

import os
import sys
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_1_verificar_endpoint_cancelacion():
    """Verificar que el endpoint de cancelación esté usando la función correcta"""
    print("🔍 TEST 1: ENDPOINT DE CANCELACIÓN")
    print("-" * 40)
    
    try:
        # Leer el código del panel para verificar el endpoint
        with open('src/admin/panel.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el endpoint eliminar
        lines = content.split('\n')
        in_eliminar_function = False
        function_lines = []
        
        for i, line in enumerate(lines):
            if '@app.route(\'/eliminar/<int:turno_id>\', methods=[\'POST\'])' in line:
                in_eliminar_function = True
                function_lines.append(f"{i+1}: {line}")
                continue
            
            if in_eliminar_function:
                function_lines.append(f"{i+1}: {line}")
                
                # Salir cuando encontremos el próximo @app.route
                if line.strip().startswith('@app.route') and 'eliminar' not in line:
                    break
                # O cuando encontremos una función que no esté indentada
                if line.strip() and not line.startswith(' ') and not line.startswith('\t') and 'def ' in line:
                    break
        
        print("📋 Código del endpoint eliminar:")
        for line in function_lines[-20:]:  # Mostrar últimas 20 líneas relevantes
            print(f"   {line}")
        
        # Verificar elementos clave
        function_code = '\n'.join([line.split(': ', 1)[1] for line in function_lines])
        
        checks = {
            'Usa notificar_admin_cancelacion_directa': 'notificar_admin_cancelacion_directa(' in function_code,
            'Tiene fallback sistema diferido': 'notificar_cancelacion_turno(' in function_code,
            'Obtiene datos del turno': 'turno_a_eliminar' in function_code,
            'Extrae telefono': 'telefono' in function_code
        }
        
        print(f"\n📊 Verificaciones:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_2_funcion_directa():
    """Probar la función de envío directo directamente"""
    print("\n🔍 TEST 2: FUNCIÓN ENVÍO DIRECTO")
    print("-" * 40)
    
    try:
        from admin.notifications import enviar_whatsapp_directo_cancelacion
        
        # Datos de prueba (cambiar el número por uno real)
        nombre = "Usuario Test Railway"
        fecha = "2024-12-31"
        hora = "10:00"
        telefono = "5491123456789"  # ⚠️ CAMBIAR POR NÚMERO REAL
        
        print(f"📱 Probando envío directo:")
        print(f"   Nombre: {nombre}")
        print(f"   Fecha: {fecha}")
        print(f"   Hora: {hora}")
        print(f"   Teléfono: {telefono}")
        print()
        
        print("🚀 Ejecutando enviar_whatsapp_directo_cancelacion()...")
        resultado = enviar_whatsapp_directo_cancelacion(nombre, fecha, hora, telefono)
        
        if resultado:
            print("✅ FUNCIÓN EJECUTADA EXITOSAMENTE")
            print("   Si tienes WhatsApp configurado, deberías recibir el mensaje")
        else:
            print("❌ FUNCIÓN FALLÓ")
            print("   Revisar logs arriba para ver el error específico")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error ejecutando función: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_whatsapp_config():
    """Verificar configuración de WhatsApp en Railway"""
    print("\n🔍 TEST 3: CONFIGURACIÓN WHATSAPP")
    print("-" * 40)
    
    try:
        # Verificar variables de entorno
        whatsapp_vars = {
            'WHATSAPP_TOKEN': os.getenv('WHATSAPP_TOKEN'),
            'WHATSAPP_PHONE_ID': os.getenv('WHATSAPP_PHONE_ID'),
            'META_API_VERSION': os.getenv('META_API_VERSION', 'v17.0'),
            'WHATSAPP_ACCESS_TOKEN': os.getenv('WHATSAPP_ACCESS_TOKEN'),
            'WHATSAPP_PHONE_NUMBER_ID': os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        }
        
        print("🔑 Variables de entorno:")
        configured_count = 0
        for var, val in whatsapp_vars.items():
            if val:
                display = f"{val[:4]}***{val[-4:]}" if len(val) > 8 else "***"
                print(f"   ✅ {var}: {display}")
                configured_count += 1
            else:
                print(f"   ❌ {var}: NO CONFIGURADA")
        
        print(f"\n📊 Variables configuradas: {configured_count}/{len(whatsapp_vars)}")
        
        # Verificar que al menos un conjunto esté configurado
        set1_ok = whatsapp_vars['WHATSAPP_TOKEN'] and whatsapp_vars['WHATSAPP_PHONE_ID']
        set2_ok = whatsapp_vars['WHATSAPP_ACCESS_TOKEN'] and whatsapp_vars['WHATSAPP_PHONE_NUMBER_ID']
        
        if set1_ok or set2_ok:
            print("✅ Al menos un conjunto de credenciales está configurado")
            return True
        else:
            print("❌ Faltan credenciales de WhatsApp")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_4_whatsapp_sender():
    """Probar WhatsAppSender directamente"""
    print("\n🔍 TEST 4: WHATSAPP SENDER DIRECTO")
    print("-" * 40)
    
    try:
        from bots.senders.whatsapp_sender import WhatsAppSender
        
        print("📱 Creando instancia WhatsAppSender...")
        sender = WhatsAppSender()
        print("✅ WhatsAppSender creado exitosamente")
        
        # Test de número
        test_number = "5491123456789"  # ⚠️ CAMBIAR POR NÚMERO REAL
        cleaned = sender.clean_phone_number(test_number)
        print(f"🧹 Número limpio: {test_number} → {cleaned}")
        
        # Test de mensaje directo
        mensaje = f"🧪 TEST DIRECTO RAILWAY - {datetime.now().strftime('%H:%M')}\n\nSi recibes esto, el envío directo funciona!"
        
        print(f"📤 Enviando mensaje de prueba a {cleaned}...")
        resultado = sender.send_message(cleaned, mensaje)
        
        if resultado:
            print("✅ MENSAJE ENVIADO EXITOSAMENTE")
            print("   Deberías recibir el mensaje de prueba por WhatsApp")
        else:
            print("❌ ERROR ENVIANDO MENSAJE")
            print("   Revisar logs para ver el error específico")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error con WhatsAppSender: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_simular_cancelacion_completa():
    """Simular el flujo completo de cancelación"""
    print("\n🔍 TEST 5: SIMULACIÓN CANCELACIÓN COMPLETA")
    print("-" * 40)
    
    try:
        from admin.notifications import notificar_admin_cancelacion_directa
        
        # Datos de prueba
        nombre = "Usuario Simulación"
        fecha = "2024-12-31"
        hora = "11:30"
        telefono = "5491123456789"  # ⚠️ CAMBIAR POR NÚMERO REAL
        
        print(f"🎭 Simulando cancelación desde panel móvil:")
        print(f"   Nombre: {nombre}")
        print(f"   Fecha: {fecha}")
        print(f"   Hora: {hora}")
        print(f"   Teléfono: {telefono}")
        print()
        
        print("🚀 Ejecutando notificar_admin_cancelacion_directa()...")
        resultado = notificar_admin_cancelacion_directa(nombre, fecha, hora, telefono)
        
        if resultado:
            print("✅ SIMULACIÓN EXITOSA")
            print("   ✓ Admin debería ser notificado (diferido)")
            print("   ✓ Usuario debería recibir WhatsApp (inmediato)")
        else:
            print("⚠️ SIMULACIÓN PARCIAL")
            print("   ✓ Admin fue notificado")
            print("   ❌ WhatsApp al usuario falló")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar diagnóstico completo"""
    print("🚀 DIAGNÓSTICO NOTIFICACIONES DIRECTAS RAILWAY")
    print("=" * 60)
    print("Diagnosticando por qué no llegan las notificaciones")
    print("por WhatsApp cuando se cancela desde panel móvil")
    print("=" * 60)
    
    # Lista de tests
    tests = [
        ("Endpoint Cancelación", test_1_verificar_endpoint_cancelacion),
        ("Función Envío Directo", test_2_funcion_directa),
        ("Configuración WhatsApp", test_3_whatsapp_config),
        ("WhatsApp Sender", test_4_whatsapp_sender),
        ("Simulación Completa", test_5_simular_cancelacion_completa)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        print(f"\n{'='*20} {nombre.upper()} {'='*20}")
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"💥 ERROR: {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print(f"\n{'='*20} RESUMEN DIAGNÓSTICO {'='*20}")
    
    pasaron = 0
    for nombre, ok in resultados:
        status = "✅" if ok else "❌"
        print(f"{status} {nombre}: {'OK' if ok else 'FALLO'}")
        if ok:
            pasaron += 1
    
    total = len(resultados)
    print(f"\n📈 RESULTADO: {pasaron}/{total} tests pasaron")
    
    # Diagnóstico específico
    print(f"\n🎯 DIAGNÓSTICO:")
    print("-" * 20)
    
    if pasaron == 0:
        print("❌ PROBLEMA GRAVE: Ningún test pasó")
        print("   → Verificar configuración básica de WhatsApp")
        print("   → Verificar variables de entorno en Railway")
    elif pasaron == 1:
        print("⚠️ PROBLEMA DE CONFIGURACIÓN")
        print("   → El endpoint está bien pero falla WhatsApp")
        print("   → Revisar credenciales de WhatsApp en Railway")
    elif pasaron == 2:
        print("⚠️ PROBLEMA EN WHATSAPP SENDER")
        print("   → La función existe pero WhatsAppSender falla")
        print("   → Revisar implementación de WhatsAppSender")
    elif pasaron >= 3:
        print("🤔 PROBLEMA DE INTEGRACIÓN")
        print("   → Los componentes funcionan individualmente")
        print("   → Problema en el flujo del panel móvil")
        print("   → Verificar que el endpoint se ejecute correctamente")
    
    if pasaron == total:
        print("🎉 TODO FUNCIONA EN TESTING")
        print("   → El problema puede ser específico del panel móvil")
        print("   → Verificar que se esté llamando la función correcta")
        print("   → Revisar logs del panel cuando cancelas un turno")

if __name__ == "__main__":
    main()
