# 🎤 ColdTemplar - Asistente de Voz Inteligente en Español

Un asistente de voz conversacional en español, basado en IA local, con capacidades de procesamiento de lenguaje natural y síntesis de voz.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Language](https://img.shields.io/badge/language-Español-red.svg)]()

---

## 📋 Características

✅ **Reconocimiento de voz en español** - Transcripción de audio a texto con Whisper  
✅ **Procesamiento inteligente** - LLM local (Ollama + Llama3) para respuestas contextuales  
✅ **Síntesis de voz** - Voz femenina natural en español (Piper TTS)  
✅ **Detección de intenciones** - 6+ categorías de comandos en español  
✅ **Logging automático** - Todas las sesiones guardadas en JSON  
✅ **Sin conexión internet** - Funciona 100% local  
✅ **Hands-free** - Interacción pura por voz  

---

## 🚀 Inicio Rápido

### Requisitos
- Python 3.8+
- Ollama con modelo llama3
- Piper TTS
- ALSA/PulseAudio (para audio)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/coldtemplar/ColdTemplar-Labs.git
cd ColdTemplar-Labs

# Instalar dependencias Python
pip install -r requirements.txt

# Asegurar que Ollama está corriendo
ollama serve &  # En otra terminal
```

### Uso

```bash
# Opción 1: Alias (requiere tener configurado en .zshrc)
ct

# Opción 2: Script directo
python3 scripts/coldtemplar_asistente.py

# Opción 3: Launcher con opciones
bash scripts/launch.sh
```

---

## 📚 Documentación

- **[CASOS_DE_USO.md](CASOS_DE_USO.md)** - 10 escenarios y ejemplos reales
- **[CAMBIOS_REALIZADOS.md](CAMBIOS_REALIZADOS.md)** - Detalles técnicos de implementación
- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Referencia rápida y troubleshooting
- **[README_ASISTENTE.md](README_ASISTENTE.md)** - Guía detallada del asistente

---

## 🎤 Ejemplos de Uso

### Conversación Básica
```
Usuario: "¿Qué es la inteligencia artificial?"
ColdTemplar: "La IA simula el pensamiento humano mediante algoritmos. Se usa en recomendaciones, reconocimiento facial, y análisis de datos."
```

### Comandos Especiales
```
Usuario: "Ayuda"           → Lista funciones disponibles
Usuario: "Reporte"         → Estado del sistema
Usuario: "Adiós"           → Termina sesión y guarda logs
```

### Casos de Uso Real
- 📊 Consultas de datos y análisis
- 💻 Ayuda con programación
- 📚 Tutoring académico
- 🎓 Brainstorming creativo
- 🏃 Orientación personal

---

## 🏗️ Arquitectura

```
ColdTemplar-Labs/
├── scripts/
│   ├── coldtemplar_asistente.py    # Script principal
│   ├── habla_coldtemplar.sh         # Motor TTS
│   ├── launch.sh                    # Launcher interactivo
│   └── escucha_inteligente_*.py     # Versiones alternativas
├── logs/                             # Sesiones guardadas (JSON)
├── voice_models/                     # Modelos de voz
├── CASOS_DE_USO.md                  # 10 escenarios
├── CAMBIOS_REALIZADOS.md            # Detalles técnicos
├── GUIA_RAPIDA.md                   # Referencia rápida
└── README.md                         # Este archivo
```

---

## 🔧 Configuración Avanzada

### Cambiar Modelo de IA
En `scripts/coldtemplar_asistente.py`, línea ~100:
```python
# Cambiar de llama3 a:
'neural-chat'    # Ligero y rápido
'mistral'        # Más potente
'openchat'       # Equilibrado
```

### Cambiar Voz
En `scripts/habla_coldtemplar.sh`:
```bash
VOZ="$HOME/ia-tools/es_ES-gama-female.onnx"    # Femenina (actual)
VOZ="$HOME/ia-tools/es_ES-gama-medium.onnx"    # Neutra
VOZ="$HOME/ia-tools/es_ES-gama-male.onnx"      # Masculina
```

### Ajustar Tiempo de Escucha
En `coldtemplar_asistente.py`, línea ~26:
```python
self.listen_seconds = 5    # Cambiar a 10 para más tiempo
```

---

## 📊 Dependencias

| Componente | Versión | Propósito |
|-----------|---------|----------|
| Python | 3.8+ | Runtime |
| faster-whisper | Última | Transcripción STT |
| sounddevice | Última | Captura de audio |
| scipy | Última | Procesamiento de señal |
| ollama | Última | LLM local |
| piper-tts | Última | Síntesis de voz |

```bash
pip install -r requirements.txt
```

---

## 📊 Estadísticas de Rendimiento

| Métrica | Valor |
|---------|-------|
| Tiempo grabación | 5 segundos |
| Transcripción | 2-5 seg |
| Procesamiento LLM | 5-15 seg |
| Síntesis de voz | 2-5 seg |
| **Total** | **15-30 seg** |
| Precisión (español) | ~95% |
| Reconocimiento intenciones | ~90% |

---

## 🐛 Troubleshooting

### Micrófono no funciona
```bash
# Listar dispositivos
arecord -l

# Ajustar volumen
alsamixer
```

### Ollama no responde
```bash
# Iniciar Ollama (otra terminal)
ollama serve

# Verificar modelos
ollama list
```

### Voz no es femenina
```bash
# Verificar archivo existe
ls -la ~/ia-tools/es_ES-gama-*.onnx

# Hacer test manual
echo "Hola" | ~/ia-tools/piper/piper --model ~/ia-tools/es_ES-gama-female.onnx --output_file test.wav && aplay test.wav
```

---

## 🔮 Roadmap Futuro

- [ ] Memoria de conversación (recordar contexto largo)
- [ ] Búsqueda en internet integrada
- [ ] Generación de imágenes
- [ ] Control de Home Automation
- [ ] API REST para integración
- [ ] Interfaz Web/Móvil
- [ ] Soporte multi-idioma simultáneo
- [ ] Control de aplicaciones del sistema

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios grandes, abre un issue primero o envía un pull request.

### Cómo Contribuir
1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**Rober (ColdTemplar)**
- GitHub: [@coldtemplar](https://github.com/coldtemplar)

---

## 📞 Soporte

Para problemas o sugerencias:
1. Abre un [Issue](https://github.com/coldtemplar/ColdTemplar-Labs/issues)
2. Consulta la [Guía Rápida](GUIA_RAPIDA.md)
3. Lee la [Documentación de Casos de Uso](CASOS_DE_USO.md)

---

## 🎉 Agradecimientos

- **Whisper** por transcripción de audio
- **Ollama** por LLM local
- **Piper** por síntesis de voz
- **SoundDevice** por captura de audio

---

**Hecho con ❤️ en español - ColdTemplar Labs 2026**
