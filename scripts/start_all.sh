#!/bin/bash
# ==============================================================================
# 🚀 Lanzador Maestro - Ecosistema ColdTemplar v2.1
# ==============================================================================
# ¿Por qué este script?
# Automatiza el arranque secuencial de todos los servicios locales necesarios
# para que el asistente funcione con capacidades de IA y automatización,
# evitando abrir múltiples terminales manualmente.
#
# 💡 Ejemplo de uso:
#   $ ./start_all.sh
#   (O simplemente escribe 'ctall' en la terminal si configuraste el alias)
# ==============================================================================

echo "======================================================="
echo "🚀 Iniciando el ecosistema ColdTemplar v2.1..."
echo "======================================================="

# 🧠 1. MOTOR DE IA (OLLAMA)
# Verificamos primero si el proceso existe (pgrep) para no agotar la memoria RAM
# intentando levantar instancias duplicadas del LLM local.
echo -e "\n🧠 1. Verificando motor de IA Local (Ollama)..."
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama ya está en ejecución."
else
    echo "🔄 Levantando Ollama en segundo plano..."
    # Redirigimos la salida a un log temporal para no ensuciar la terminal del usuario
    OLLAMA_MODELS=~/.ollama/models ollama serve > /tmp/ollama_ct.log 2>&1 &
    # Pausa táctica: Damos tiempo a que el servidor HTTP de Ollama esté listo para recibir peticiones
    sleep 3
    echo "✅ Ollama iniciado."
fi

# ⚡ 2. AGENTE AUTÓNOMO (n8n)
# Usamos modo detached (-d) para que los contenedores corran en el fondo
# y nos permitan seguir usando esta misma terminal para el script de Python.
echo -e "\n⚡ 2. Levantando Agente Autónomo (n8n)..."
cd ~/ColdTemplar-Labs || { echo "❌ Error: Directorio no encontrado"; exit 1; }
docker-compose up -d

# 🎤 3. INTERFAZ DE VOZ
# Pausa breve para asegurar que tanto Ollama como la red de Docker hayan asentado bien.
echo -e "\n🎤 3. Iniciando Asistente de Voz (ColdTemplar)..."
sleep 2
python3 ~/ColdTemplar-Labs/scripts/coldtemplar_asistente.py

echo -e "\n🛑 Interfaz de ColdTemplar finalizada. Iniciando apagado del ecosistema..."

# 🧹 4. LIMPIEZA: DOCKER
# ¿Por qué? Para liberar recursos de la computadora (RAM/CPU) cuando no usamos el asistente.
echo -e "⚡ Deteniendo Agente Autónomo (n8n)..."
docker-compose down

# 🧹 5. LIMPIEZA: OLLAMA
# Buscamos el proceso exacto (-x) y lo matamos de forma segura.
echo -e "🧠 Deteniendo motor de IA (Ollama)..."
pkill -x "ollama" && echo "✅ Ollama detenido correctamente." || echo "⚠️ Ollama ya estaba detenido."

echo -e "\n✅ Ecosistema ColdTemplar apagado por completo. ¡Hasta pronto!"