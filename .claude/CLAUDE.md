# 🤖 ColdTemplar - Configuración Claude Code

**Versión:** 2.0  
**Actualizado:** 2 de abril de 2026  
**Autor:** Rober (ColdTemplar)

---

## 📋 Estructura del Proyecto

```
ColdTemplar-Labs/
├── .claude/                    ← Configuración Claude Code
│   ├── CLAUDE.md              ← Este archivo
│   ├── skills/                ← Comandos reutilizables
│   ├── agents/                ← Agentes especializados
│   ├── docs/                  ← Documentación interna
│   └── resources/             ← Recursos de referencia
├── scripts/                   ← Código ejecutable
├── docs/ (en root)           ← Documentación pública
├── logs/                      ← Sesiones grabadas
└── .git/                      ← Control de versiones
```

---

## 🎯 Instrucciones Principales para Claude

### 1. **Enfoque Español**
- SIEMPRE responder en español latino
- Documentación en español
- Prompts y ejemplos en español

### 2. **Estructura de Proyecto**
- Código limpio y documentado
- Tests y validaciones incluidas
- Logs automáticos de todo

### 3. **Mejores Prácticas**
- No crear archivos sin necessidad
- Usar tools existentes antes de crear nuevos
- Mantener compatibilidad con versiones anteriores
- Documentar todos los cambios

### 4. **Flujo de Trabajo**
1. **Analizar** → Leer contexto
2. **Planificar** → Crear plan si es multi-paso
3. **Ejecutar** → Cambios concretos
4. **Validar** → Tests / verificación
5. **Documentar** → Actualizar docs

---

## 🔧 Skills Disponibles

**Skills** son comandos reutilizables guardados en `.claude/skills/`.

Cada skill es un archivo `.md` con instrucciones específicas.

### Skills Actuales:
- `git-workflow.md` - Workflow de Git
- `audio-troubleshooting.md` - Diagnosticar audio
- `ollama-setup.md` - Configuración de Ollama
- `spanish-validation.md` - Validar respuestas en español

---

## 🤖 Agentes Disponibles

**Agentes** son roles especializados definidos en `.claude/agents/`.

Cada agente tiene un propósito específico.

### Agentes Disponibles:
- `asistente-voz.md` - Experto en asistente de voz
- `devops.md` - Experto en deployment y infraestructura

---

## 📚 Conocimiento Base

### Sobre el Proyecto
- **Propósito:** Asistente de voz IA en español
- **Tech Stack:** Python + Whisper + Ollama + Piper
- **Estado:** Producción ready
- **Audiencia:** Developers, Students, Executives

### Módulos Principales
1. **STT** (Speech-to-Text) → Whisper
2. **LLM** (Language Model) → Ollama + Llama3
3. **TTS** (Text-to-Speech) → Piper (voz femenina)
4. **Intent Detection** → Custom NLP en español
5. **Autonomous Agent** → n8n (Integración con APIs, Email, Notion, etc.)

---

## 🔍 Recursos de Referencia

Ver archivo: `.claude/resources/RECURSOS_GITHUB.md`

### Repositorios Recomendados:
1. **GetShitDone** - Meta-prompting para Claude Code
2. **Antigravity Awesome Skills** - 1.300+ skills instalables
3. **Awesome Claude Code Toolkit** - 135 agentes + toolkits

### Documentación Oficial:
- [Anthropic Claude Docs](https://docs.anthropic.com)
- [GitHub CLI Docs](https://cli.github.com/)
- [Ollama Documentation](https://ollama.ai)

---

## 📍 Convenciones del Código

### Nombrado de Archivos
```
scripts/coldtemplar_*.py      ← Scripts principales
scripts/test_*.py              ← Tests
.claude/skills/*.md            ← Skills
.claude/agents/*.md            ← Agentes
.claude/docs/*.md              ← Documentación interna
```

### Commits
```
[feature] Nueva funcionalidad
[fix] Corrección de bug
[docs] Actualización de documentación
[refactor] Mejora de código
[perf] Optimización de rendimiento
```

### Docstrings Python
```python
def funcion():
    """Descripción corta.
    
    Descripción larga si es necesaria.
    
    Args:
        param1: Descripción
        
    Returns:
        Descripción del retorno
        
    Example:
        >>> funcion()
        resultado
    """
```

---

## ⚙️ Configuración de Entorno

### Variables Importantes
```bash
COLDTEMPLAR_HOME=~/ColdTemplar-Labs
OLLAMA_MODELS=~/.ollama/models
PIPER_TTS=$HOME/ia-tools/piper/piper
AUDIO_DEVICE_ID=2  # Default fallback
```

### Rutas Críticas
```
~/ia-tools/              ← Herramientas externas (TTS, etc)
~/ColdTemplar-Labs/logs/ ← Sesiones guardadas (JSON)
/tmp/orden_coldtemplar.wav ← Audio temporal
```

---

## 🚀 Comandos Frecuentes

```bash
# Iniciar asistente
ct

# Ver logs
ls ~/ColdTemplar-Labs/logs/

# Git workflow
git status
git add .
git commit -m "[feature] Descripción"
git push origin main

# Tests
python3 -m pytest scripts/test_*.py

# Actualizar docs
./scripts/generate_docs.sh
```

---

## 📊 Tracking y Control

Hay un **CHECKLIST_RECURSOS.md** en `.claude/docs/` para tracking de:
- ✅ Repositorios revisados
- 📝 Recursos por implementar
- 🔄 Skills instalados
- 🎯 Agentes activos

Ver: `.claude/docs/CHECKLIST_RECURSOS.md`

---

## 📞 Puntos de Contacto

### Problemas Comunes
1. **Micrófono no funciona**
   - Ver: `.claude/skills/audio-troubleshooting.md`
   - Comando: `arecord -l && alsamixer`

2. **Ollama no responde**
   - Ver: `.claude/skills/ollama-setup.md`
   - Comando: `ollama serve` (otra terminal)

3. **Respuestas en inglés**
   - Ver: `.claude/skills/spanish-validation.md`
   - Revisar prompts en `coldtemplar_asistente.py`

---

## 🔐 Seguridad y Privacidad

- ✅ Todas las operaciones son locales (sin internet)
- ✅ Logs guardados solo en máquina local
- ✅ No se envían datos a servidores externos
- ✅ Audio grabado se procesa y descarta inmediatamente

---

## 📈 Roadmap Futuro

- [ ] Integración con más LLMs (GPT, Claude, etc)
- [ ] Soporte multi-idioma
- [ ] API REST para integración
- [ ] Dashboard web
- [ ] Control de Home Automation
- [ ] Mobile app
- [x] Integración como Agente Autónomo (n8n)

---

## 📝 Logs de Cambios

### v2.1 (Abril 2026)
- ✅ Integración con n8n para tareas digitales automatizadas
- ✅ Docker Compose para infraestructura de automatización local
- ✅ Capacidad de enviar correos y gestionar tareas vía voz

### v2.0 (2 de abril de 2026)
- ✅ Español nativo completo
- ✅ Voz femenina integrada
- ✅ Detección inteligente de intenciones
- ✅ Repositorio en GitHub
- ✅ Estructura .claude/ iniciada

### v1.0 (25 de marzo de 2026)
- ✅ Asistente básico de voz
- ✅ Reconocimiento STT
- ✅ LLM local con Ollama
- ✅ TTS con Piper

---

## 🎓 Cómo Usar Este Archivo

Este archivo (`CLAUDE.md`) será **leído automáticamente por Claude** cada vez que trabaje en el proyecto.

Úsalo para:
1. **Recordar instrucciones** - Contexto global
2. **Referenciar estructura** - Dónde están las cosas
3. **Coordinar trabajo** - Convenciones y flujos
4. **Gestionar recursos** - Qué tenemos disponible

---

**Versión actual: 2.0**  
**Última actualización: 2 de abril de 2026**  
**Mantenedor: Rober (ColdTemplar)**

---

*Este archivo es parte del repositorio ColdTemplar-Labs y está bajo licencia MIT.*
