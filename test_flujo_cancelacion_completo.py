#!/usr/bin/env python3
"""
Test completo del flujo de cancelación desde panel admin
Simula exactamente lo que pasa en Railway
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_paso_1_buscar_turno():
    """Paso 1: Simular búsqueda de turno en el panel"""
    print("🔍 === PASO 1: BUSCAR TURNO ===")
    
    try:
        from core.database import obtener_todos_los_turnos
        
        # Simular lo que hace el panel
        turnos = obtener_todos_los_turnos()
        print(f"📊 Turnos encontrados en BD: {len(turnos)}")
        
        if turnos:
            # Mostrar algunos turnos
            for i, turno in enumerate(turnos[:3], 1):
                turno_id, nombre, fecha, hora, telefono = turno
                print(f"   {i}. ID:{turno_id} - {nombre} - {fecha} {hora} - {telefono}")
            
            # Simular selección del primer turno
            turno_a_eliminar = turnos[0]
            print(f"✅ Turno seleccionado para cancelar: {turno_a_eliminar}")
            return turno_a_eliminar
        else:
            print("❌ No hay turnos en la base de datos")
            return None
            
    except Exception as e:
        print(f"❌ Error buscando turnos: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_paso_2_eliminar_turno(turno_a_eliminar):
    """Paso 2: Simular eliminación del turno"""
    print("\n🗑️ === PASO 2: ELIMINAR TURNO ===")
    
    if not turno_a_eliminar:
        print("❌ No hay turno para eliminar")
        return False
    
    try:
        from core.database import eliminar_turno_admin
        
        turno_id = turno_a_eliminar[0]
        print(f"🔄 Eliminando turno ID: {turno_id}")
        
        # CRÍTICO: Esta es la función exacta que usa el panel
        resultado = eliminar_turno_admin(turno_id)
        print(f"✅ Resultado eliminación: {resultado}")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error eliminando turno: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_paso_3_notificar_cancelacion(turno_a_eliminar):
    """Paso 3: Simular notificación de cancelación (CRÍTICO)"""
    print("\n📨 === PASO 3: NOTIFICAR CANCELACIÓN ===")
    
    if not turno_a_eliminar:
        print("❌ No hay turno para notificar")
        return False
    
    try:
        # Extraer datos exactamente como lo hace el panel
        turno_id, nombre, fecha, hora, telefono = turno_a_eliminar
        
        print(f"📋 Datos para notificación:")
        print(f"   ID: {turno_id}")
        print(f"   Nombre: {nombre}")
        print(f"   Fecha: {fecha}")
        print(f"   Hora: {hora}")
        print(f"   Teléfono: {telefono}")
        
        # CRÍTICO: Esta es la función exacta que usa el panel
        from services.notifications import notificar_cancelacion_turno
        
        print(f"🔄 Llamando notificar_cancelacion_turno...")
        resultado = notificar_cancelacion_turno(turno_id, nombre, fecha, hora, telefono)
        
        print(f"✅ Notificación registrada:")
        print(f"   Timestamp: {resultado.get('timestamp', 'N/A')}")
        print(f"   Teléfono: {resultado.get('telefono', 'N/A')}")
        print(f"   Tipo: {resultado.get('tipo', 'N/A')}")
        print(f"   Enviado: {resultado.get('enviado', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error notificando cancelación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_paso_4_verificar_notificacion():
    """Paso 4: Verificar que la notificación se guardó"""
    print("\n📋 === PASO 4: VERIFICAR NOTIFICACIÓN ===")
    
    try:
        from services.notifications import obtener_notificaciones_pendientes
        
        notifs = obtener_notificaciones_pendientes()
        print(f"📊 Total notificaciones pendientes: {len(notifs)}")
        
        # Buscar notificaciones de cancelación recientes
        cancelaciones = [n for n in notifs if n.get('tipo') == 'cancelacion_turno']
        print(f"📊 Notificaciones de cancelación: {len(cancelaciones)}")
        
        if cancelaciones:
            print("📋 Últimas cancelaciones:")
            for i, notif in enumerate(cancelaciones[-3:], 1):
                timestamp = notif.get('timestamp', 'N/A')
                telefono = notif.get('telefono', 'N/A')
                enviado = notif.get('enviado', 'N/A')
                print(f"   {i}. {telefono} - {timestamp[:19]} - Enviado: {enviado}")
            
            return True
        else:
            print("❌ No hay notificaciones de cancelación")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando notificaciones: {e}")
        return False

def test_paso_5_simular_daemon():
    """Paso 5: Simular lo que hace el daemon"""
    print("\n🤖 === PASO 5: SIMULAR DAEMON ===")
    
    try:
        from services.notifications import obtener_notificaciones_pendientes
        
        # Obtener notificaciones como lo hace el daemon
        notificaciones = obtener_notificaciones_pendientes()
        
        print(f"📊 Daemon ve {len(notificaciones)} notificaciones pendientes")
        
        # Filtrar solo cancelaciones para el test
        cancelaciones = [n for n in notificaciones if n.get('tipo') == 'cancelacion_turno']
        
        if cancelaciones:
            print(f"🔄 Daemon procesaría {len(cancelaciones)} cancelaciones:")
            
            for i, notif in enumerate(cancelaciones, 1):
                telefono = notif.get('telefono', 'N/A')
                tipo = notif.get('tipo', 'N/A')
                enviado = notif.get('enviado', False)
                
                if not enviado:
                    print(f"   {i}. 📨 Enviaría WhatsApp a {telefono}: {tipo}")
                else:
                    print(f"   {i}. ✅ Ya enviado a {telefono}: {tipo}")
            
            return len([n for n in cancelaciones if not n.get('enviado', False)]) > 0
        else:
            print("❌ Daemon no ve notificaciones de cancelación")
            return False
            
    except Exception as e:
        print(f"❌ Error simulando daemon: {e}")
        return False

def test_flujo_completo_panel():
    """Test completo del flujo como en el panel"""
    print("\n🎯 === FLUJO COMPLETO PANEL ===")
    
    try:
        # Simular datos de formulario del panel
        turno_id = 2  # Simular que viene del form
        
        print(f"📝 Panel recibe: turno_id = {turno_id}")
        
        # Paso 1: Buscar el turno (como hace el panel)
        from core.database import obtener_todos_los_turnos
        turnos = obtener_todos_los_turnos()
        turno_a_eliminar = None
        
        for turno in turnos:
            if turno[0] == turno_id:  # turno[0] es el ID
                turno_a_eliminar = turno
                break
        
        if not turno_a_eliminar:
            print(f"❌ No se encontró turno con ID {turno_id}")
            return False
        
        print(f"✅ Turno encontrado: {turno_a_eliminar}")
        
        # Paso 2: Eliminar el turno (como hace el panel)
        from core.database import eliminar_turno_admin
        if eliminar_turno_admin(turno_id):
            print(f"✅ Turno eliminado de BD")
            
            # Paso 3: Notificar (como hace el panel)
            turno_id, nombre, fecha, hora, telefono = turno_a_eliminar
            
            from services.notifications import notificar_cancelacion_turno
            resultado = notificar_cancelacion_turno(turno_id, nombre, fecha, hora, telefono)
            
            print(f"✅ Notificación enviada a {telefono} por cancelación de turno")
            print(f"📋 Resultado: {resultado}")
            
            return True
        else:
            print(f"❌ Error eliminando turno")
            return False
            
    except Exception as e:
        print(f"❌ Error en flujo completo: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_archivos_notificaciones():
    """Verificar estado de archivos de notificaciones"""
    print("\n📁 === VERIFICAR ARCHIVOS ===")
    
    archivos = [
        'data/notifications_log.json',
        'data/admin_notifications.json'
    ]
    
    for archivo in archivos:
        path = os.path.join(os.path.dirname(__file__), archivo)
        existe = os.path.exists(path)
        print(f"📁 {archivo}: {'✅ Existe' if existe else '❌ No existe'}")
        
        if existe:
            try:
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"   📊 Registros: {len(data)}")
                
                # Contar cancelaciones
                if 'notifications_log' in archivo:
                    cancelaciones = [n for n in data if n.get('tipo') == 'cancelacion_turno']
                    print(f"   🚫 Cancelaciones: {len(cancelaciones)}")
                    
            except Exception as e:
                print(f"   ❌ Error leyendo archivo: {e}")

def main():
    print("🚫 === TEST COMPLETO FLUJO CANCELACIÓN PANEL ===")
    print(f"📅 Fecha: {datetime.now()}")
    print(f"🚂 Simulando comportamiento en Railway")
    print("=" * 70)
    
    # Verificar archivos primero
    verificar_archivos_notificaciones()
    
    # Ejecutar flujo paso a paso
    print("\n" + "="*70)
    print("🔄 EJECUTANDO FLUJO PASO A PASO...")
    
    # Paso 1: Buscar turno
    turno_a_eliminar = test_paso_1_buscar_turno()
    
    if turno_a_eliminar:
        # Paso 2: Eliminar turno
        eliminado = test_paso_2_eliminar_turno(turno_a_eliminar)
        
        if eliminado:
            # Paso 3: Notificar
            notificado = test_paso_3_notificar_cancelacion(turno_a_eliminar)
            
            # Paso 4: Verificar
            verificado = test_paso_4_verificar_notificacion()
            
            # Paso 5: Simular daemon
            daemon_ok = test_paso_5_simular_daemon()
            
            print("\n" + "="*70)
            print("📊 RESUMEN:")
            print(f"   🔍 Buscar turno: {'✅' if turno_a_eliminar else '❌'}")
            print(f"   🗑️ Eliminar turno: {'✅' if eliminado else '❌'}")
            print(f"   📨 Notificar: {'✅' if notificado else '❌'}")
            print(f"   📋 Verificar: {'✅' if verificado else '❌'}")
            print(f"   🤖 Daemon: {'✅' if daemon_ok else '❌'}")
            
            if all([eliminado, notificado, verificado, daemon_ok]):
                print("\n🎉 ¡FLUJO COMPLETO EXITOSO!")
                print("✅ En Railway debería funcionar correctamente")
                print("🔍 Si no funciona en Railway, el problema es:")
                print("   - Variables de WhatsApp no configuradas")
                print("   - Daemon no ejecutándose")
                print("   - Problemas de conectividad")
            else:
                print("\n❌ PROBLEMAS DETECTADOS EN EL FLUJO")
                print("🔧 Revisar pasos que fallaron arriba")
    
    # Test adicional: flujo completo
    print("\n" + "="*70)
    print("🎯 TEST FLUJO COMPLETO:")
    flujo_ok = test_flujo_completo_panel()
    print(f"🎯 Flujo completo: {'✅' if flujo_ok else '❌'}")

if __name__ == "__main__":
    main()
