#!/usr/bin/env python3
"""
Test específico para notificación de cancelación de turno desde panel admin
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_notificacion_cancelacion():
    """Test completo de notificación de cancelación"""
    print("🔍 === TEST NOTIFICACIÓN CANCELACIÓN TURNO ===")
    
    try:
        from services.notifications import notificar_cancelacion_turno
        
        # Datos de prueba (simulando lo que viene del panel)
        turno_id = 999
        nombre = "Usuario Test"
        fecha = "2025-08-05"
        hora = "10:30"
        telefono = "123456789"
        
        print(f"📋 Datos de prueba:")
        print(f"   ID: {turno_id}")
        print(f"   Nombre: {nombre}")
        print(f"   Fecha: {fecha}")
        print(f"   Hora: {hora}")
        print(f"   Teléfono: {telefono}")
        
        # Llamar a la función como lo hace el panel
        print(f"\n📨 Llamando notificar_cancelacion_turno...")
        resultado = notificar_cancelacion_turno(turno_id, nombre, fecha, hora, telefono)
        
        print(f"✅ Función ejecutada, resultado: {resultado}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en notificación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mensaje_cancelacion():
    """Test del mensaje específico de cancelación"""
    print("\n🔍 === TEST MENSAJE CANCELACIÓN ===")
    
    try:
        from services.notifications import NotificationManager
        
        manager = NotificationManager()
        nombre = "Usuario Test"
        fecha = "2025-08-05"
        hora = "10:30"
        
        mensaje = manager.crear_mensaje_cancelacion_admin(nombre, fecha, hora)
        
        print("📝 Mensaje generado:")
        print("-" * 40)
        print(mensaje)
        print("-" * 40)
        
        # Verificar que el mensaje contiene los elementos necesarios
        elementos_requeridos = [
            "Turno Cancelado",
            nombre,
            "cancelado",
            "administrativos",
            "hola"
        ]
        
        mensaje_ok = True
        for elemento in elementos_requeridos:
            if elemento not in mensaje:
                print(f"❌ Falta elemento: {elemento}")
                mensaje_ok = False
            else:
                print(f"✅ Contiene: {elemento}")
        
        return mensaje_ok
        
    except Exception as e:
        print(f"❌ Error generando mensaje: {e}")
        return False

def test_registro_notificacion():
    """Test del registro de notificación"""
    print("\n🔍 === TEST REGISTRO NOTIFICACIÓN ===")
    
    try:
        from services.notifications import NotificationManager
        
        manager = NotificationManager()
        
        # Simular registro de notificación
        resultado = manager.registrar_notificacion(
            telefono="123456789",
            mensaje="Test cancelación",
            tipo="cancelacion_turno",
            turno_id=999
        )
        
        print(f"📋 Notificación registrada: {resultado}")
        
        # Verificar que se guardó
        from admin.notifications import contar_notificaciones_pendientes
        pendientes = contar_notificaciones_pendientes()
        print(f"📊 Notificaciones pendientes: {pendientes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error registrando notificación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flujo_completo_panel():
    """Test simulando exactamente lo que hace el panel"""
    print("\n🔍 === TEST FLUJO COMPLETO PANEL ===")
    
    try:
        # Simular datos como los obtiene el panel
        turno_a_eliminar = (999, "Usuario Test", "2025-08-05", "10:30", "123456789")
        turno_id, nombre, fecha, hora, telefono = turno_a_eliminar
        
        print("📋 Simulando flujo del panel:")
        print(f"   1. Turno encontrado: {turno_a_eliminar}")
        print(f"   2. Extrayendo datos...")
        print(f"      ID: {turno_id}")
        print(f"      Nombre: {nombre}")
        print(f"      Fecha: {fecha}")
        print(f"      Hora: {hora}")
        print(f"      Teléfono: {telefono}")
        
        # Llamar exactamente como lo hace el panel
        from services.notifications import notificar_cancelacion_turno
        
        print(f"   3. Llamando notificar_cancelacion_turno...")
        resultado = notificar_cancelacion_turno(turno_id, nombre, fecha, hora, telefono)
        
        print(f"   4. Resultado: {resultado}")
        print(f"✅ Notificación enviada a {telefono} por cancelación de turno")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en flujo panel: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_verificar_notificaciones_creadas():
    """Verificar que las notificaciones se crearon correctamente"""
    print("\n🔍 === VERIFICAR NOTIFICACIONES CREADAS ===")
    
    try:
        from admin.notifications import obtener_notificaciones_pendientes, contar_notificaciones_pendientes
        
        count = contar_notificaciones_pendientes()
        print(f"📊 Total notificaciones pendientes: {count}")
        
        if count > 0:
            notifs = obtener_notificaciones_pendientes()
            print(f"📋 Últimas notificaciones:")
            for i, notif in enumerate(notifs[-3:], 1):  # Últimas 3
                tipo = notif.get('tipo', 'N/A')
                timestamp = notif.get('timestamp', 'N/A')
                telefono = notif.get('telefono', 'N/A')
                print(f"   {i}. {tipo} - {telefono} - {timestamp[:19]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando notificaciones: {e}")
        return False

def main():
    print("🚫 === TEST CANCELACIÓN TURNO DESDE PANEL ===")
    print(f"📅 Fecha: {datetime.now()}")
    print("=" * 60)
    
    tests = [
        ("Notificación cancelación", test_notificacion_cancelacion),
        ("Mensaje cancelación", test_mensaje_cancelacion),
        ("Registro notificación", test_registro_notificacion),
        ("Flujo completo panel", test_flujo_completo_panel),
        ("Verificar notificaciones", test_verificar_notificaciones_creadas),
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
        print("\n🎉 NOTIFICACIÓN DE CANCELACIÓN FUNCIONA")
        print("✅ El panel debería enviar notificaciones correctamente")
    else:
        print("\n❌ PROBLEMA EN NOTIFICACIÓN DE CANCELACIÓN")
        print("🔧 Revisar errores específicos arriba")
    
    return all(resultados)

if __name__ == "__main__":
    main()
