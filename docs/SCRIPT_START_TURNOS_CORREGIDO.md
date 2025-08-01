# ✅ SCRIPT start_turnos.sh CORREGIDO

## 🐛 **PROBLEMA ORIGINAL**
```bash
./start_turnos.sh: line 14: cd: /src/admin: No such file or directory
python3: can't open file 'panel.py': [Errno 2] No such file or directory
```

## 🔧 **CORRECCIONES REALIZADAS**

### **1. Actualización de Rutas**
- ❌ **Antes**: `cd /src/admin` y `python3 panel.py` 
- ✅ **Después**: Detección automática del proyecto y `python3 main.py`

### **2. Detección Automática del Proyecto**
```bash
# Obtener directorio raíz del proyecto (un nivel arriba de scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
```

### **3. Verificación de Archivos**
```bash
# Verificar que el archivo main.py existe
if [ ! -f "main.py" ]; then
    echo "❌ Error: No se encuentra main.py en $PROJECT_ROOT"
    exit 1
fi
```

### **4. Corrección de Imports en bot_sender.py**
- **Problema**: `ModuleNotFoundError: No module named 'src'`
- **Solución**: Agregado path dinámico cuando se ejecuta como script independiente
```python
# Agregar la raíz del proyecto al path cuando se ejecuta como script independiente
if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    sys.path.insert(0, os.path.join(project_root, 'src'))
```

### **5. Corrección de Imports en services/notifications.py**
- **Problema**: Imports que no funcionaban cuando se llamaban desde script independiente
- **Solución**: Imports con fallback automático
```python
try:
    from core.database import obtener_turnos_por_fecha, obtener_todos_los_turnos
except ImportError:
    # Fallback para ejecución como script independiente
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, os.path.join(project_root, 'src'))
    from core.database import obtener_turnos_por_fecha, obtener_todos_los_turnos
```

## ✅ **RESULTADO FINAL**

### **Script Funcionando Correctamente**
```bash
./scripts/start_turnos.sh
🚀 Iniciando Sistema de Turnos...
📁 Directorio del proyecto: /home/santi/Documents/personal/turnosBot
📡 IP Local: 192.168.1.7
🌐 Panel Web: http://192.168.1.7:9000
📱 Panel Móvil: http://192.168.1.7:9000/mobile

🔧 Usando nueva estructura organizada...
📦 Ejecutando desde: /home/santi/Documents/personal/turnosBot
[MAIN] 🚀 Iniciando TurnosBot en Railway... (NUEVA ESTRUCTURA)
[MAIN] ✅ Daemon iniciado
[MAIN] ✅ Todos los servicios iniciados
[MAIN] 🌐 Panel disponible en puerto 9000
```

### **Servicios Iniciados**
- ✅ **Daemon de notificaciones** ejecutándose en thread separado
- ✅ **Panel de administración** funcionando en puerto 9000
- ✅ **Bot WhatsApp** (si está configurado)
- ✅ **Base de datos** inicializada correctamente

### **URLs Disponibles**
- 🌐 **Panel Web**: http://192.168.1.7:9000
- 📱 **Panel Móvil**: http://192.168.1.7:9000/mobile

## 🎯 **VENTAJAS DEL SCRIPT CORREGIDO**

1. **✅ Detección Automática**: Encuentra el proyecto sin importar desde dónde se ejecute
2. **✅ Verificación de Errores**: Confirma que los archivos existen antes de ejecutar
3. **✅ Nueva Estructura**: Usa la estructura organizada con `main.py`
4. **✅ Imports Robustos**: Los módulos funcionan tanto importados como scripts independientes
5. **✅ Información Clara**: Muestra rutas, IPs y URLs de acceso

**🚀 El script `start_turnos.sh` ahora está completamente adaptado a la nueva estructura y funciona perfectamente!**
