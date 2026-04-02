#!/bin/bash
#
# ColdTemplar Asistente de Voz - Script de Inicio Rápido
# Autor: ColdTemplar Labs
# Versión: 1.0 (Mejorada)
# 
# Este script facilita el lanzamiento de tu asistente de voz
# Soporta múltiples modos de operación
#

# Colores para salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Banner
echo -e "${BLUE}"
cat << 'BANNER'
╔════════════════════════════════════════════════╗
║     🎤 COLDTEMPLAR ASISTENTE DE VOZ 🎤       ║
║         Versión Mejorada 2026.04.01           ║
╚════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

# Verificar si Ollama está corriendo
echo -e "${YELLOW}📋 Verificando dependencias...${NC}"

if ! command -v ollama &>/dev/null; then
    echo -e "${RED}❌ ERROR: Ollama no está instalado${NC}"
    exit 1
fi

if ! timeout 2 ollama list &>/dev/null; then
    echo -e "${YELLOW}⚠️  Ollama no está ejecutándose${NC}"
    echo -e "${BLUE}💡 Inicia Ollama en otra terminal:${NC}"
    echo -e "   ${GREEN}ollama serve${NC}"
    echo ""
    read -p "¿Deseas que lo inicie automáticamente? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        nohup ollama serve &>/tmp/ollama.log &
        echo -e "${GREEN}✅ Ollama iniciado en background${NC}"
        sleep 3
    else
        echo -e "${RED}Abortado. Inicia Ollama manualmente.${NC}"
        exit 1
    fi
fi

if ! command -v piper &>/dev/null; then
    echo -e "${RED}❌ ERROR: Piper TTS no está instalado${NC}"
    exit 1
fi

if ! python3 -c "import sounddevice, scipy, faster_whisper" 2>/dev/null; then
    echo -e "${RED}❌ ERROR: Dependencias Python incompletas${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Todas las dependencias verificadas${NC}"
echo ""

# Modo de operación
echo -e "${BLUE}Elige modo de operación:${NC}"
echo "  1) Interactivo (por defecto)"
echo "  2) Modo demo (pregunta de prueba)"
echo "  3) Modo background (sin TTY)"
echo ""
read -p "Opción [1-3]: " -n 1 -r mode
mode=${mode:-1}
echo ""
echo ""

# Ejecutar según el modo
case $mode in
    1)
        echo -e "${GREEN}🚀 Iniciando modo interactivo...${NC}"
        python3 ~/ColdTemplar-Labs/scripts/coldtemplar_asistente.py
        ;;
    2)
        echo -e "${GREEN}🚀 Iniciando modo demo...${NC}"
        python3 ~/ColdTemplar-Labs/scripts/coldtemplar_asistente.py --demo
        ;;
    3)
        echo -e "${GREEN}🚀 Iniciando en background...${NC}"
        nohup python3 ~/ColdTemplar-Labs/scripts/coldtemplar_asistente.py >/tmp/coldtemplar.log 2>&1 &
        echo -e "${GREEN}✅ Proceso iniciado (PID: $!)${NC}"
        echo -e "${BLUE}📝 Logs en: /tmp/coldtemplar.log${NC}"
        ;;
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}¡Disfruta tu asistente de voz!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
