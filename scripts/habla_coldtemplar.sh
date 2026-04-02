#!/bin/bash
AUDIO="$HOME/ia-tools/ct_respuesta.wav"
PIPER="$HOME/ia-tools/piper/piper"
# Usa voz en español con timbre femenino (si está disponible)
VOZ="$HOME/ia-tools/es_ES-gama-female.onnx"
if [ ! -f "$VOZ" ]; then
    VOZ="$HOME/ia-tools/es_ES-gama-medium.onnx"
fi

# --- Lógica de Intenciones ---
if [[ "$1" == *"trabajar"* ]] || [[ "$1" == *"modo trabajo"* ]]; then
    bash ~/.coldtemplar_dev.sh > /dev/null 2>&1 &
    RESPUESTA="Entendido, Rober. Iniciando entorno blindado de desarrollo."
elif [[ "$1" == *"reporte"* ]] || [[ "$1" == *"estado"* ]]; then
    # Ejecutamos el script de auditoría que creamos antes
    RESPUESTA=$(bash ~/ia-tools/auditar_voz.sh --text-only)
elif [[ "$1" == *"raspberry"* ]] || [[ "$1" == *"estado de la pi"* ]]; then
    REPORTE=$(bash ~/ia-tools/auditar_pi.sh)
    RESPUESTA="Rober, he auditado la Raspberry. La temperatura está estable y no hay reportes de caída de voltaje. El disco SD tiene un 20% de espacio libre."
else
    CONTEXTO="Eres ColdTemplar, una IA eficiente. Responde en máximo 2 frases: $1"
    RESPUESTA=$(ollama run llama3 "$CONTEXTO")
fi

# --- Motor de Voz Optimizado ---
# --length_scale 0.8: Reduce el tiempo (0.8 = 20% más rápido, 1.0 es normal)
# --sentence_silence 0.05: Reduce pausas entre puntos y comas
echo "$RESPUESTA" | tee /dev/tty | $PIPER \
  --model $VOZ \
  --length_scale 0.78 \
  --sentence_silence 0.05 \
  --output_file $AUDIO && aplay $AUDIO
