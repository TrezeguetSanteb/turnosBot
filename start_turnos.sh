#!/bin/bash
# Script de inicio para Sistema de Turnos

echo "🚀 Iniciando Sistema de Turnos..."

# Obtener IP local
IP=$(hostname -I | awk '{print $1}')

echo "📡 IP Local: $IP"
echo "🌐 Panel Web: http://$IP:9000"
echo "📱 Panel Móvil: http://$IP:9000/mobile"

# Iniciar el servidor
cd /home/santi/Documents/personal/turnosBot
python3 admin_panel.py
