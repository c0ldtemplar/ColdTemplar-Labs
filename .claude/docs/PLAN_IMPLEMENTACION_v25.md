# 🎯 PLAN DE IMPLEMENTACIÓN: ColdTemplar v2.5

**Estado:** EN PLANIFICACIÓN  
**Versión del Plan:** 1.0  
**Actualizado:** 2 de abril de 2026  
**Horizonte:** 4 semanas (2-30 de abril)  

---

## 📋 Resumen Ejecutivo

**Objetivo Principal:** Integrar 3 grandes repositorios (GetShitDone, Antigravity, Awesome Toolkit) para:
- Mejorar manejo de contexto (tokens efficiency)
- Expandir soporte Spanish NLP
- Crear arquitectura multiagente
- Optimizar performance

**ROI Esperado:**
- 🚀 50% menos uso de tokens
- 🎯 90% precisión en intent detection (vs 60% actual)
- 🤖 5 agentes especializados (vs 1 actual)
- 📈 2x mejor calidad de respuestas

**Timeline:** 4 semanas  
**Esfuerzo Estimado:** 60 horas  
**Recursos Requeridos:** GetShitDone, Antigravity Skills, Awesome Toolkit  

---

## 🏗️ Arquitectura Target (v2.5)

```
┌─────────────────────────────────────────────────────────────┐
│            ColdTemplar v2.5 MULTIAGENTE                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         USUARIO (Voz / Texto)                          │ │
│  │       "¿Cuál es el estado del repo?"                   │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │                                               │
│  ┌────────────▼───────────────────────────────────────────┐ │
│  │  1. INPUT HANDLER (coldtemplar_asistente.py)           │ │
│  │     - Captura audio @ 44100 Hz                         │ │
│  │     - Resample → 16000 Hz                              │ │
│  │     - Whisper: Transcribe a español                    │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │ "cual es el estado del repo"                │
│               │                                               │
│  ┌────────────▼───────────────────────────────────────────┐ │
│  │  2. INTENT ROUTER (intent_detector_v2.py) [NEW]        │ │
│  │     - Spanish NLP: Antigravity skill                   │ │
│  │     - Intent: SYSTEM_STATUS / REPORT                   │ │
│  │     - Confidence: 0.92                                 │ │
│  │     - Entities: {repo: "ColdTemplar"}                  │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │                                               │
│  ┌────────────▼───────────────────────────────────────────┐ │
│  │ 3. AGENT DISPATCHER (agent_orchestrator.py) [NEW]      │ │
│  │    Evalúa: intent → agent especializado                │ │
│  │    Router:                                              │ │
│  │    - SYSTEM_STATUS → DevOps Agent                      │ │
│  │    - CODING → Code Review Agent                        │ │
│  │    - DOCUMENTATION → Doc Agent                         │ │
│  │    - SPANISH_CHAT → Voice Agent                        │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │ dispatch to DevOps Agent                     │
│               │                                               │
│  ┌────────────▼───────────────────────────────────────────┐ │
│  │ 4. SPECIALIZED AGENTS (agentes especializados)         │ │
│  │                                                          │ │
│  │  A) DevOps Agent                                        │ │
│  │     - Git status (GetShitDone: state.md)               │ │
│  │     - Branch info                                       │ │
│  │     - Test results                                      │ │
│  │                                                          │ │
│  │  B) Voice Assistant Agent                              │ │
│  │     - Conversación natural                              │ │
│  │     - Context window optimization                       │ │
│  │     - Multi-turn memory                                 │ │
│  │                                                          │ │
│  │  C) Code Review Agent                                   │ │
│  │     - PR analysis                                       │ │
│  │     - Test coverage                                     │ │
│  │     - Security audit                                    │ │
│  │                                                          │ │
│  │  D) Documentation Agent                                 │ │
│  │     - Generar docs automáticas                          │ │
│  │     - Mantenimiento de CHECKLISTs                      │ │
│  │                                                          │ │
│  │  E) Spanish NLP Agent (future)                         │ │
│  │     - Entity extraction                                 │ │
│  │     - Sentiment analysis                                │ │
│  │     - Dialect detection                                 │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │ "El repo está actualizado. 3 tests pasando"  │
│               │                                               │
│  ┌────────────▼───────────────────────────────────────────┐ │
│  │  5. OUTPUT HANDLER                                      │ │
│  │     - Format respuesta                                  │ │
│  │     - TTS: Piper (es_ES-gama-female)                   │ │
│  │     - Play audio                                        │ │
│  └────────────┬───────────────────────────────────────────┘ │
│               │                                               │
│  ┌────────────▼───────────────────────────────────────────┐ │
│  │         USUARIO (Audio output)                          │ │
│  │       [Audio con voz femenina en español]              │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  BACKGROUND (GetShitDone):                                  │
│  - STATE: .claude/state/{facts,plan,session}.md            │
│  - Logging a logs/                                          │
│  - Context compression cada 10 turnos                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 Fases de Implementación

### FASE 1: DISCOVERY & SETUP (2-3 de abril, ~4 horas)

**Objetivo:** Obtener repositorios, catalogar contenido, crear infraestructura

**Tareas:**

```
[ ] 1.1) Descargar GetShitDone
    - URL: https://lnkd.in/dpEG2dZV
    - Comando: git clone [repo] /tmp/get-shit-done
    - Revisar: docs/, patterns/, examples/
    - Tiempo: 30 min

[ ] 1.2) Descargar Antigravity Awesome Skills
    - URL: https://lnkd.in/dDhMmkGH
    - Comando: git clone [repo] /tmp/awesome-skills
    - Catalogar por categoria: voice/, nlp/, agents/, llm/
    - Tiempo: 45 min

[ ] 1.3) Descargar Awesome Claude Toolkit
    - URL: https://lnkd.in/dEAiwgcf
    - Comando: git clone [repo] /tmp/awesome-toolkit
    - Revisar estructura: agents/, skills/, prompts/, tools/
    - Tiempo: 45 min

[ ] 1.4) Crear estructura en .claude/
    - mkdir -p .claude/{skills/antigravity, skills/getshitdone, agents, resources}
    - cp /tmp/awesome-toolkit/skills/* .claude/skills/awesome-toolkit/
    - Tiempo: 30 min

[ ] 1.5) Catalogar en SKILLS_DISCOVERY.md
    - Tabla: 50+ skills encontrados
    - Filtrar por "APLICABLE" = SÍ
    - Ranquear por prioridad (ALTA, MEDIA, BAJA)
    - Tiempo: 1 hora

ENTREGABLE: `.claude/docs/SKILLS_DISCOVERY.md` con top 20
VALIDACIÓN: git log mostrando 3 reposllenados descargados
```

---

### FASE 2: FOUNDATION - CONTEXT OPTIMIZATION (4-5 de abril, ~8 horas)

**Objetivo:** Implementar GetShitDone patterns para manejo de contexto y estado

**Tareas:**

```
[ ] 2.1) Crear estructura de estado
    - mkdir -p .claude/state
    - Archivos:
      * facts.md     → Hechos confirmados (inmutable)
      * plan.md      → Plan actual + checkpoints
      * session.md   → Notas de sesión actual (volatile)
    - Tiempo: 30 min

[ ] 2.2) Implementar context compressor
    - Nuevo archivo: context_optimizer.py
    - Función: compress_context(history, limit=5000)
    - Método: Mantiene últimos N turnos + summary de previos
    - GetShitDone pattern: Cada 10 turnos, resumen a facts.md
    - Tiempo: 2 horas

[ ] 2.3) Integrar state management en asistente
    - Modificar coldtemplar_asistente.py:
      * load_state() al iniciar
      * save_state() después cada turno
      * compress_state() cada 10 turnos
    - Actualizar __init__: inicializar con state
    - Tiempo: 1.5 horas

[ ] 2.4) Crear state persistence en logs
    - Guardar facts.md en cada session log
    - Guardar plan.md si cambió
    - Validar: estado recuperable en próxima sesión
    - Tiempo: 1 hora

[ ] 2.5) Documentar patterns en .claude/
    - Crear: .claude/skills/getshitdone-integration.md
    - Template: Cómo usar facts/plan/session
    - Ejemplos: 3 casos de uso
    - Tiempo: 1 hora

[ ] 2.6) Pruebas
    - Test: Sesión de 30 turnos, verify compression
    - Test: Reiniciar, load facts, recuperar contexto
    - Test: Token count antes/después
    - Tiempo: 1 hora

ENTREGABLE: coldtemplar_asistente.py v2.1 + .claude/state/
VALIDACIÓN: Token usage 30% menor en pruebas
COMMIT: "[feat] AddGetShitDone context optimization"
```

---

### FASE 3: SPANISH NLP ENHANCEMENT (6-7 de abril, ~10 horas)

**Objetivo:** Integrar skills de Antigravity para mejor detección de intenciones en español

**Tareas:**

```
[ ] 3.1) Extraer top 5 Spanish NLP skills
    - Buscar en /tmp/awesome-skills/:
      * spanish-intent-extraction.md
      * spanish-entity-recognition.md
      * spanish-sentiment-analysis.md
      * spanish-grammar-correction.md
      * spanish-dialect-detection.md
    - Copiar a: .claude/skills/antigravity/
    - Tiempo: 1 hora

[ ] 3.2) Implementar Intent Detector v2
    - Nuevo archivo: intent_detector_v2.py
    - Basado en: spanish-intent-extraction.md
    - Características:
      * 6 categorías base + 6 nuevas (15 total)
      * Confidence scoring (0-1)
      * Entity extraction (quien, qué, dónde, cuándo)
      * Spanish-specific patterns (vosotros, diminutivos)
    - Modelos: TextBlob + spacy + custom patterns
    - Tiempo: 3 horas

[ ] 3.3) Implementar Entity Recognizer
    - Basado en: spanish-entity-recognition.md
    - Detectar: personas, lugares, conceptos, tiempos
    - Integrar en process_command()
    - Ejemplo: "Abre el archivo informe.txt"
      * Intent: OPEN_FILE
      * Entity: {type: archivo, value: informe.txt}
    - Tiempo: 2 horas

[ ] 3.4) Mejorar prompts para Ollama
    - Usar entity info en prompts
    - Ejemplo anterior: "El usuario quiere abrir el archivo informe.txt"
    - Aumentar contexto específico
    - Validar respuestas en español
    - Tiempo: 1.5 horas

[ ] 3.5) Crear mapping entity-command
    - Tabla: intent + entities → acción
    - Ejemplo:
      * Intent: OPEN_FILE, Entity: {tipo:archivo, nombre:test.py}
        → ejecutar: open_file("test.py")
    - 20+ mappings cubiertos
    - Tiempo: 1.5 horas

[ ] 3.6) Pruebas Spanish NLP
    - Test phrases: 50+ variaciones en español
    - Validate: Intent detection, confidence, entities
    - Coverage: 85%+ de frases comunes
    - Tiempo: 1 hora

ENTREGABLE: intent_detector_v2.py + entity_recognizer.py
VALIDACIÓN: 90% accuracy en test phrases
COMMIT: "[feat] Add Antigravity Spanish NLP integration"
```

---

### FASE 4: MULTIAGENT ARCHITECTURE (8-10 de abril, ~12 horas)

**Objetivo:** Crear sistema de agentes especializados basado en Awesome Toolkit

**Tareas:**

```
[ ] 4.1) Extraer agentes base del Awesome Toolkit
    - Copiar:
      * voice-assistant-agent.md → .claude/agents/
      * intent-recognizer.md → .claude/agents/
      * context-manager-agent.md → .claude/agents/
      * code-review-agent.md → .claude/agents/
      * documentation-agent.md → .claude/agents/
    - Adaptar ejemplos a ColdTemplar
    - Tiempo: 2 horas

[ ] 4.2) Crear Agent Base Class
    - Nuevo archivo: agent_base.py
    - Interfaz común:
      * def handle(input) → output
      * def think(prompt) → response (usa Ollama)
      * def speak(text) → audio
      * def get_context() → dict
    - Herencia: todos agentes heredan de Agent
    - Tiempo: 1.5 horas

[ ] 4.3) Implementar Agent Dispatcher
    - Nuevo archivo: agent_orchestrator.py
    - Lógica:
      * Recibe: intent, entities, confidence (de intent_detector_v2)
      * Selecciona agente más apropiado
      * Pasa contexto + estado
      * Recibe respuesta, formatea, retorna
    - Selección inteligente (>1 candidato → score)
    - Fallback a Voice Assistant si sin match
    - Tiempo: 2 horas

[ ] 4.4) Implementar 3 agentes específicos
    - Voice Assistant Agent (conversación general)
    - Code Review Agent (análisis de código)
    - DevOps Agent (estado del repo)
    - Cada uno: 200-300 líneas Python
    - Tiempo: 3 horas

[ ] 4.5) Integración en coldtemplar_asistente.py
    - Importar agent_orchestrator
    - Reemplazar think():
      * intent = detect_intent(text)
      * agent = dispatcher.select(intent)
      * response = agent.handle(text, context)
    - Mantener backwards compatibility
    - Tiempo: 1.5 horas

[ ] 4.6) Crear Agent Communication Protocol
    - Formato JSON para messages:
      {
        "intent": "OPEN_FILE",
        "entities": {},
        "confidence": 0.92,
        "context": {},
        "history": []
      }
    - Documentar en .claude/
    - Tiempo: 1 hora

[ ] 4.7) Pruebas multiagente
    - Test cada agente independientemente
    - Test dispatcher routing
    - Test fallback scenarios
    - Test context passing
    - Coverage: 80%+ de paths
    - Tiempo: 1.5 horas

ENTREGABLE: agent_orchestrator.py + 3 agent implementations + voice_assistant.py v2
VALIDACIÓN: Todos agents retornan respuestas válidas, routing funciona
COMMIT: "[feat] Add multiagent architecture from Awesome Toolkit"
```

---

### FASE 5: TESTING & OPTIMIZATION (11-12 de abril, ~8 horas)

**Objetivo:** Validar calidad, optimizar performance, documentar

**Tareas:**

```
[ ] 5.1) Suite de pruebas unitarias
    - intent_detector_v2_test.py (20+ tests)
    - entity_recognizer_test.py (15+ tests)
    - context_optimizer_test.py (10+ tests)
    - agent_orchestrator_test.py (20+ tests)
    - Coverage: 85%+ código total
    - Tiempo: 2 horas

[ ] 5.2) Pruebas de integración
    - End-to-end: audio → respuesta
    - 50+ frases de prueba
    - Medir: accuracy, latency, correctness
    - Validar cálculo de tokens
    - Tiempo: 2 horas

[ ] 5.3) Performance profiling
    - Identificar bottlenecks
    - Medir latency de cada componente
    - Optimizar hot paths
    - Target: <2 segundos total latency
    - Tiempo: 1.5 horas

[ ] 5.4) Documentation
    - Actualizar README.md con nueva arquitectura
    - Crear architecture.md detallado
    - Actualizar CLAUDE.md
    - Crear examples/ con 10+ casos de uso
    - Tiempo: 1.5 hora

[ ] 5.5) Crear release notes
    - v2.5 changelog
    - Feature highlights
    - Breaking changes: NINGUNO (backwards compatible)
    - Upgrade path: Automático
    - Tiempo: 1 hora

ENTREGABLE: test suite + release v2.5
VALIDACIÓN: 95%+ tests passing, <2s latency
COMMIT: "[release] v2.5 Multiagent architecture stable"
```

---

### FASE 6: DEPLOYMENT & MONITORING (13-14 de abril, ~4 horas)

**Objetivo:** Deploy a GitHub, setup monitoring, crear runbook

**Tareas:**

```
[ ] 6.1) Git commits y push
    - 1 commit por feature: Context, NLP, Agents, Tests
    - Push a main branch
    - Validar CI/CD (si existe)
    - Tiempo: 30 min

[ ] 6.2) Tag release
    - git tag -a v2.5 -m "Multiagent architecture"
    - git push --tags
    - Create Release en GitHub
    - Tiempo: 15 min

[ ] 6.3) Crear runbook operacional
    - Cómo inicializar
    - Cómo actualizar state
    - Cómo debug problemas
    - Troubleshooting guide
    - Documentar en .claude/docs/
    - Tiempo: 1 hora

[ ] 6.4) Monitoring setup
    - Log metrics: tokens, latency, accuracy
    - Crear dashboard (CLI o web simple)
    - Alertas si latency > 3s
    - Tiempo: 30 min

[ ] 6.5) Validación en producción
    - Prueba 1 hora de uso real
    - Monitor logs
    - Validate respuestas en español
    - Collect feedback
    - Tiempo: 1 hora

ENTREGABLE: v2.5 tagged release + monitoring + runbook
VALIDACIÓN: Sistema estable, <2% error rate
```

---

## 📊 Matriz RACI

| Tarea | Responsable | Accountable | Consultar | Informar |
|-------|-------------|-------------|-----------|----------|
| Discovery | c0ldtemplar | c0ldtemplar | CLAUDE | GitHub |
| Context Opt | c0ldtemplar | c0ldtemplar | CLAUDE | Logs |
| NLP Enhancement | c0ldtemplar | c0ldtemplar | CLAUDE | Tests |
| Multiagent | c0ldtemplar | c0ldtemplar | CLAUDE | GitHub |
| Testing | c0ldtemplar | c0ldtemplar | Test suite | Metrics |
| Deployment | c0ldtemplar | c0ldtemplar | CLAUDE | Release |

---

## 🎯 KPIs Objetivo

| KPI | Actual | Target (v2.5) | Success Metric |
|-----|--------|---------------|-----------------|
| Intent Accuracy | 60% | 90% | >90% correct classification |
| Token Efficiency | 100% baseline | 70% | <70% of current usage |
| Response Latency | 3-5s | <2s | 95th percentile < 2s |
| Spanish Compliance | 95% | 99% | 0 English responses |
| Code Coverage | 40% | 85% | pytest --cov > 85% |
| Uptime | 98% | 99.5% | <4.32 hours downtime/month |
| User Satisfaction | 8/10 | 9/10 | Subjective post-session rating |

---

## 🚨 Risk Management

| Risk | Probabilidad | Impacto | Mitigación |
|------|-------------|---------|-----------|
| Incompatibilidad Whistler | BAJA | ALTO | Usar Faster-Whisper tested version |
| Memory leak en agentes | MEDIA | MEDIO | Code review + memory profiling |
| Performance degradation | MEDIA | MEDIO | Profiling en Phase 5 |
| Spanish model inconsistency | BAJA | ALTO | Validación strict + fallback |
| GitHub token expiry | MUY BAJA | CRÍTICO | Usar environment variables |

---

## 💾 Checkpoints & Rollback Plan

```
Checkpoint 1 (Post Phase 2):
├─ Branch: feature/context-optimization
├─ Rollback: git revert [commits]
└─ Test coverage: >70%

Checkpoint 2 (Post Phase 3):
├─ Branch: feature/spanish-nlp
├─ Rollback: git revert [commits]
└─ Test coverage: >80%

Checkpoint 3 (Post Phase 4):
├─ Branch: feature/multiagent
├─ Rollback: git revert [commits]
└─ Test coverage: >85%

Rollback maestro:
└─ git checkout v2.0  # Volver a última versión estable
```

---

## 📅 Timeline Gantt Simplificado

```
Semana 1:  [████] Discovery        (4h)
           [████] Foundation       (8h)
           
Semana 2:  [████] NLP             (10h)
           [██] Multiagent setup  (6h)
           
Semana 3:  [████] Multiagent impl (12h)
           [██] Testing          (4h)
           
Semana 4:  [████] Testing/Perf    (8h)
           [██] Docs/Release     (4h)
           [█] Deployment        (4h)
           
Total: ~60 horas en 4 semanas
```

---

## ✅ Go-Live Checklist

```
ANTES DE PUSH A MAIN:
[ ] Todos tests pasando (pytest coverage >85%)
[ ] Docs actualizadas (README, architecture.md)
[ ] CHANGELOG completado (v2.5)
[ ] Performance validated (<2s latency)
[ ] Spanish validation (99%+ responses en español)
[ ] State management probado (recuperación de contexto)
[ ] Agentes routing correctamente (90%+ accuracy)
[ ] Backwards compatibility confirmado (v2.0 configs still work)
[ ] GitHub Actions pasando (si existe CI/CD)
[ ] Code review aprobado (si multiple contributors)
[ ] Backup de v2.0 en tag (v2.0 tag exists)

DESPUÉS DE PUSH A MAIN:
[ ] GitHub release creado
[ ] Tag v2.5 creado y pusheado
[ ] Release notes completas
[ ] Monitoring activado
[ ] Runbook en .claude/docs/OPERACIONES.md
```

---

**Estado:** 🟡 EN PLANIFICACIÓN  
**Próximo Paso:** Iniciar FASE 1 (Discovery)  
**Estimado Inicio:** 3 de abril de 2026  
**Estimado Fin:** 30 de abril de 2026  

