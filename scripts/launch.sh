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
    echo -e "${BLUE} Levantando Ollama automáticamente (Zero-Touch)...${NC}"
    OLLAMA_MODELS=~/.ollama/models nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    echo -e "${GREEN}✅ Ollama iniciado en background${NC}"
fi

# Verificar si n8n está corriendo (opcional pero recomendado para automatización)
if curl -s http://localhost:5678/healthz > /dev/null; then
    echo -e "${GREEN}✅ n8n (Agente Autónomo) está EN LÍNEA${NC}"
else
    echo -e "${YELLOW}⚠️  n8n no está corriendo en el puerto 5678.${NC}"
    echo -e "${BLUE}🔄 Levantando n8n vía Docker...${NC}"
    if [ -f "$HOME/ColdTemplar-Labs/docker-compose.yml" ]; then
        cd "$HOME/ColdTemplar-Labs" && docker-compose up -d
        echo -e "${GREEN}✅ n8n iniciado en background.${NC}"
    else
        echo -e "${YELLOW}⚠️  No se encontró docker-compose.yml. Las tareas digitales no funcionarán.${NC}"
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
if [ -n "$1" ]; then
    mode=$1
    echo -e "${BLUE}ℹ️  Modo parametrizado detectado: $mode${NC}"
else
    echo -e "${BLUE}Elige modo de operación:${NC}"
    echo "  1) Interactivo (por defecto)"
    echo "  2) Modo demo (pregunta de prueba)"
    echo "  3) Modo background (sin TTY)"
    echo ""
    read -p "Opción [1-3]: " -n 1 -r mode
    mode=${mode:-1}
    echo ""
fi
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
