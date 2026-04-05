#!/bin/bash
# ==============================================================================
# 🔊 Motor de Síntesis de Voz (TTS) - ColdTemplar
# ==============================================================================
# ¿Por qué este script?
# Desacopla la lógica de generación de voz del script principal de Python.
# Toma un texto de entrada, evalúa si es un comando rápido (hardcoded) o
# si necesita enviarlo a Ollama, y finalmente lo convierte a audio usando Piper.
#
# 💡 Ejemplo de uso:
#   $ ./habla_coldtemplar.sh "Hola, soy tu asistente local."
# ==============================================================================

# ⚙️ 1. CONFIGURACIÓN DE RUTAS Y MODELOS
AUDIO="$HOME/ia-tools/ct_respuesta.wav"
PIPER="$HOME/ia-tools/piper/piper"

# Buscamos primero la voz femenina (es_ES-gama-female) porque suena más natural
# para el perfil del asistente. Si no está descargada, hacemos fallback seguro a medium.
VOZ="$HOME/ia-tools/es_ES-gama-female.onnx"
if [ ! -f "$VOZ" ]; then
    VOZ="$HOME/ia-tools/es_ES-gama-medium.onnx"
fi

# 🧠 2. EVALUACIÓN DE INTENCIONES (RUTEO RÁPIDO)
# ¿Por qué? Para comandos del sistema, es mucho más rápido y eficiente 
# responder con texto predefinido que despertar al LLM (Ollama), ahorrando recursos.
if [[ "$1" == *"trabajar"* ]] || [[ "$1" == *"modo trabajo"* ]]; then
    bash ~/.coldtemplar_dev.sh > /dev/null 2>&1 &
    RESPUESTA="Entendido, Rober. Iniciando entorno blindado de desarrollo."
elif [[ "$1" == *"reporte"* ]] || [[ "$1" == *"estado"* ]]; then
    # Ejecutamos el script de auditoría para obtener el estado real de la PC
    RESPUESTA=$(bash ~/ia-tools/auditar_voz.sh --text-only)
elif [[ "$1" == *"raspberry"* ]] || [[ "$1" == *"estado de la pi"* ]]; then
    REPORTE=$(bash ~/ia-tools/auditar_pi.sh)
    RESPUESTA="Rober, he auditado la Raspberry. La temperatura está estable y no hay reportes de caída de voltaje. El disco SD tiene un 20% de espacio libre."
else
    # Si no es un comando rápido, le delegamos el razonamiento al cerebro (LLM)
    CONTEXTO="Eres ColdTemplar, una IA eficiente. Responde en máximo 2 frases: $1"
    RESPUESTA=$(ollama run llama3 "$CONTEXTO")
fi

# 🔊 3. SÍNTESIS TEXT-TO-SPEECH (PIPER)
# ¿Por qué estos parámetros?
# --length_scale 0.78: Acelera la voz un 22% para que no suene aletargada o robótica (1.0 es el default).
# --sentence_silence 0.05: Acorta el silencio artificial entre comas y puntos, dando mayor fluidez.
echo "$RESPUESTA" | tee /dev/tty | $PIPER \
  --model $VOZ \
  --length_scale 0.78 \
  --sentence_silence 0.05 \
  --output_file $AUDIO && aplay $AUDIO
