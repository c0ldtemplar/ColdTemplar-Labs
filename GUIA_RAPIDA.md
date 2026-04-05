# 🎤 ColdTemplar - Guía Rápida de Referencia

## Ejecución Instant

```bash
ct
```

---

## 📋 Ejemplos Listos para Copiar/Pegar

### Productividad
```
"¿Cuál es la mejor práctica para trabajar remoto?"
"Dame 5 consejos para ser más productivo"
"¿Cómo hago un plan de estudio para aprender Python?"
"¿Cuál es el método Pomodoro?"
```

### Técnico/Programación
```
"¿Cómo hago un GET request en Python?"
"Explica qué es REST API"
"¿Cuál es la diferencia entre let, const y var en JavaScript?"
"¿Cómo subo un proyecto a GitHub?"
"¿Qué es Docker?"
"Ayuda con errores de sintaxis en Python"
```

### Académico/Educación
```
"¿Quién fue Albert Einstein?"
"Explica la teoría de la relatividad"
"¿Cómo resuelvo una derivada?"
"¿Qué es el método científico?"
"¿Cuáles son las eras geológicas?"
```

### General/Curiosidad
```
"¿Cuáles son los beneficios del ejercicio?"
"¿Qué es la sostenibilidad?"
"¿Cuál es el futuro de la IA?"
"¿Cómo aprender nuevo idioma rápido?"
"¿Qué es la inversión en bolsa?"
```

### Casa/Vida Cotidiana
```
"¿Cómo preparo un buen café?"
"¿Qué plantas son buenas para el hogar?"
"¿Cómo organizó mejor mi habitación?"
"¿Qué ejercicios puedo hacer en casa?"
"¿Recetas rápidas para la cena?"
```

### Control del Asistente
```
"Ayuda"              → Muestra funciones
"Reporte"            → Estado del sistema
"Adiós"              → Cierra sesión
"Hasta luego"        → Cierra sesión
"Terminar"           → Cierra sesión
```

---

## 🎯 Respuestas Esperadas

### Usuario: "¿Qué puedes hacer?"
**ColdTemplar:** "Puedo responder preguntas, consultar estado del sistema, abrir navegador, reproducir música. ¿En qué puedo ayudarte?"

### Usuario: "Explica inteligencia artificial"
**ColdTemplar:** "La inteligencia artificial simula el pensamiento humano mediante algoritmos. Se usa en recomendaciones (Netflix), reconocimiento facial, y análisis de datos."

### Usuario: "Dame un chiste"
**ColdTemplar:** "¿Por qué los programadores prefieren el dark mode? Porque la luz atrae bugs."

### Usuario: "Reporte"
**ColdTemplar:** "Sistema en línea y estable. CPU al 35%, RAM al 60%, disco con espacio disponible."

---

## 🛠️ Solución Rápida si Algo No Funciona

### Micrófono no captura
```bash
# Verifica niveles
alsamixer     # Ajusta volumen de capture
# O verifica dispositivo
arecord -l
```

### Voz no se escucha
```bash
# Verifica altavoces
aplay -l
# Test rápido
echo "Hola" | ~/ia-tools/piper/piper --model ~/ia-tools/es_ES-gama-female.onnx --output_file test.wav && aplay test.wav
```

### Ollama no responde
```bash
# Inicia Ollama (otra terminal, deja abierta)
ollama serve
```

### No reconoce comandos en español
```bash
# Intenta ser más claro
❌ "Ayudaaa"
✅ "Ayuda"

❌ "Adia"
✅ "Adiós"
```

---

## 📊 Ver Historial de Sesiones

```bash
# Lista todas las sesiones
ls -lh ~/ColdTemplar-Labs/logs/

# Ver última sesión
cat ~/ColdTemplar-Labs/logs/sesion_*.json | tail -1

# Ver contenido formateado
cat ~/ColdTemplar-Labs/logs/sesion_*.json | jq .
```

---

## 🔊 Calidad de Audio

- **Micrófono ideal:** Conversación normal (no muy fuerte, no muy bajo)
- **Ambiente:** Menos ruido = mejor
- **Distancia:** A 20-30cm del micrófono
- **Velocidad:** Habla normal (no muy rápido)

---

## 🌍 Idiomas Soportados

Actualmente: **Español** principalmente  
Nota: Ollama + Whisper soportan otros idiomas, pero responden mejor en español por configuración.

---

## ⏱️ Tiempos de Respuesta

| Etapa | Tiempo |
|-------|--------|
| Grabación | 5 seg |
| Transcripción | 2-5 seg |
| Procesamiento LLM | 5-15 seg |
| Síntesis de voz | 2-5 seg |
| **Total** | **15-30 seg** |

---

## 🎨 Personalización Opcional

### Cambiar tiempo de escucha
En `coldtemplar_asistente.py`, línea ~26:
```python
self.listen_seconds = 5  # Cambiar a 10 para más tiempo
```

### Cambiar modelo de IA
```python
# Línea ~100, cambiar de llama3 a:
['ollama', 'run', 'neural-chat', prompt]  # Alternativa ligera
['ollama', 'run', 'mistral', prompt]      # Más potente
```

### Cambiar voz
En `habla_coldtemplar.sh`:
```bash
VOZ="$HOME/ia-tools/es_ES-gama-male.onnx"      # Masculina (si existe)
VOZ="$HOME/ia-tools/es_ES-gama-medium.onnx"    # Neutra
```

---

## 💾 Backup automático

Cada sesión se guarda en JSON:
```bash
~/ColdTemplar-Labs/logs/sesion_YYYYMMDD_HHMMSS.json
```

Nunca se pierden tus interacciones.

---

## 🚀 Próxima Generación (Roadmap)

- [ ] Memoria de conversación (recordar contexto)
- [ ] Búsqueda en internet integrada
- [ ] Generación de imágenes
- [ ] Control de Home Automation
- [ ] Soporte Web/Móvil
- [ ] Múltiples idiomas simultáneamente

---

## 📞 Comandos de Emergencia

| Comando | Atajo |
|---------|-------|
| Interrumpir | **Ctrl+C** |
| Matar proceso | `pkill -f coldtemplar` |
| Ver logs en vivo | `tail -f /tmp/coldtemplar.log` |

---

## ✨ Tips Profesionales

1. **Para mejores resultados, sé natural:** Habla como hablarías con un amigo.
2. **Reformula si no entendió:** No es un fracaso del asistente, improve tú el pregunta.
3. **Usa para lluvia de ideas:** ColdTemplar es excelente para brainstorming.
4. **Integra en tu workflow:** Úsalo mientras trabajas (hands-free).
5. **Archiva sesiones importantes:** Los JSONs están listos para análisis.

---

## 🎉 ¡Listo para Empezar!

```bash
ct
```

**Y disfruta tu asistente inteligente en español.**
