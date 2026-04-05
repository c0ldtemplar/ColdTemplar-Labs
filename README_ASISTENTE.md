# 🎤 ColdTemplar Assistant - Guía de Uso Rápido

## ⚡ Ejecución Instant (3 opciones)

### **Opción 1: Alias Rápido (RECOMENDADO)**
```bash
ct
```

O alternativamente:
```bash
coldtemplar
```

O la versión amigable:
```bash
hablar-con-coldtemplar
```

---

### **Opción 2: Script Directo**
```bash
bash ~/ct.sh
```

---

### **Opción 3: Python Explícito**
```bash
python3 ~/ColdTemplar-Labs/scripts/coldtemplar_asistente.py
```

---

## 🎯 Comandos Disponibles Durante la Sesión

| Comando | Resultado |
|---------|-----------|
| **Cualquier pregunta/orden** | La IA responde |
| **"reporte"** | Muestra estado del sistema |
| **"adiós"** | Termina la sesión |
| **"terminar"** | Termina la sesión |
| **Ctrl+C** | Interrupción de emergencia |

---

## 📝 Ejemplo de Sesión

```
⚙️  Cargando motores de IA local...
✅ Sistema listo.

============================================================
🟢 COLDTEMPLAR ASISTENTE - Modo Interactivo
============================================================

🎤 Escuchando (5 seg)...
💬 [Tú]: ¿Cuál es la capital de Francia?
🤔 Pensando...
🤖 [IA]: La capital de Francia es París.
[Se reproduce la respuesta por voz]

--- TURNO 2 ---
🎤 Escuchando (5 seg)...
...
```

---

## 📊 Logs & Datos

Cada sesión se guarda automáticamente en:
```
~/ColdTemplar-Labs/logs/sesion_YYYYMMDD_HHMMSS.json
```

**Contenido del log:**
- Número de turno
- Lo que dijiste exactamente
- La respuesta de la IA
- Timestamp de cada interacción

---

## 🔧 Requisitos y Dependencias

✅ Whisper (Transcripción de voz)
✅ Ollama + llama3 (Razonamiento IA)
✅ Piper TTS (Síntesis de voz)
✅ SoundDevice (Grabación de audio)

Para instalar las dependencias Python:
```bash
pip install sounddevice scipy faster-whisper requests
```

---

## 🐛 Troubleshooting

### "No se escucha el audio"
```bash
# Verifica que Piper esté en el PATH
which piper
```

### "Ollama no responde"
```bash
# Asegúrate de que Ollama esté corriendo
ollama serve &
```

### "Micrófono no funciona"
```bash
# Lista dispositivos de audio
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

---

## 🚀 Modo Avanzado: Automatización

Para ejecutar ColdTemplar en background:
```bash
nohup ct > ~/ct.log 2>&1 &
```

Para ejecutar en una sesión screen:
```bash
screen -S coldtemplar -d -m ct
```

---

**¡Listo! Ahora puedes hablar con tu computador.** 🎉
