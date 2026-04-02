#!/bin/bash
echo "==========================================="
echo "   🛡️ RADIOGRAFÍA DEL SISTEMA COLD-OPS 🛡️"
echo "==========================================="

echo -e "\n[1/5] HARDWARE & KERNEL"
uname -a
echo "Uptime: $(uptime -p)"
lsmod | grep -E "nvme|nvidia" | head -n 5

echo -e "\n[2/5] PARÁMETROS DE ARRANQUE (GRUB)"
cat /proc/cmdline

echo -e "\n[3/5] ESTADO DE DISCO (NVMe)"
if command -v smartctl &> /dev/null; then
    sudo smartctl -a /dev/nvme0n1 | grep -E "Percentage Used|Critical Warning|Temperature"
else
    echo "Instala smartmontools para ver salud de disco: sudo nala install smartmontools"
fi

echo -e "\n[4/5] RED & PUERTOS (JENKINS/DOCKER)"
ss -tulpn | grep LISTEN | grep -E "8080|50000|3000"

echo -e "\n[5/5] VERSIONES DEV (MISE)"
mise ls 2>/dev/null || echo "Mise no detectado en este shell"

echo "==========================================="
