#!/bin/bash
# Script de inicio para Sistema de Turnos
# ACTUALIZADO PARA NUEVA ESTRUCTURA

echo "🚀 Iniciando Sistema de Turnos..."

# Obtener directorio raíz del proyecto (un nivel arriba de scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📁 Directorio del proyecto: $PROJECT_ROOT"

# Cambiar al directorio del proyecto
cd "$PROJECT_ROOT"

# Obtener IP local
IP=$(hostname -I | awk '{print $1}')

echo "📡 IP Local: $IP"
echo "🌐 Panel Web: http://$IP:9000"
echo "📱 Panel Móvil: http://$IP:9000/mobile"
echo ""

# Verificar que el archivo main.py existe
if [ ! -f "main.py" ]; then
    echo "❌ Error: No se encuentra main.py en $PROJECT_ROOT"
    exit 1
fi

echo "🔧 Usando nueva estructura organizada..."
echo "📦 Ejecutando desde: $PROJECT_ROOT"

# Iniciar el servidor usando main.py (nueva estructura)
python3 main.py
