#!/bin/bash
set -euo pipefail

# Motor TTS literal para ColdTemplar.
# Solo sintetiza el texto recibido; no reinterpreta comandos ni llama al LLM.

TEXT="${1:-}"
AUDIO="$HOME/ia-tools/ct_respuesta.wav"
PIPER="$HOME/ia-tools/piper/piper"

if [ -z "$TEXT" ]; then
    exit 0
fi

if [ ! -x "$PIPER" ]; then
    echo "⚠️  Piper no está disponible en $PIPER"
    exit 1
fi

VOICE="$HOME/ia-tools/es_ES-gama-female.onnx"
if [ ! -f "$VOICE" ]; then
    VOICE="$HOME/ia-tools/es_ES-gama-medium.onnx"
fi

if [ ! -f "$VOICE" ]; then
    echo "⚠️  No encontré un modelo de voz de Piper"
    exit 1
fi

SPEAKER_ARG=""
if [[ "$VOICE" == *"female"* ]]; then
    SPEAKER_ARG="--speaker 1"
fi

printf '%s\n' "$TEXT" | "$PIPER" \
  --model "$VOICE" \
  $SPEAKER_ARG \
  --length_scale 0.9 \
  --sentence_silence 0.08 \
  --output_file "$AUDIO"

aplay "$AUDIO"
