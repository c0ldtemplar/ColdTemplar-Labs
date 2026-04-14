# 🖥️ Manual: Control de Sistema a través de ColdTemplar

Este manual documenta la implementación de la **Fase 2 de autonomía**, permitiendo a ColdTemplar interactuar directamente con el sistema operativo Linux mediante comandos Bash autogenerados.

## 🏗️ Arquitectura de la Solución

El control del sistema no utiliza herramientas complejas como LangChain a nivel local para evitar latencia extrema. En su lugar, el flujo es el siguiente:

1. **Detección de Intención:** `process_command` identifica palabras clave orientadas al SO (ej. *actualiza, instala, ejecuta, terminal*).
2. **Generación Pura (Zero-Shot Prompting):** Si detecta la intención, invoca la nueva función `generate_bash_command`. Esta función envía un *System Prompt* súper estricto a **Llama 3.1**, obligándolo a actuar como un intérprete que **solo** devuelve el comando, sin texto de relleno.
3. **Ejecución y Captura:** Utiliza la librería nativa `subprocess` de Python para ejecutar la orden en una shell (`shell=True`).
4. **Retroalimentación:** Captura `STDOUT` (éxito) y `STDERR` (error). Si el comando dura más de 15 segundos, asume que está en segundo plano y continúa escuchando para no bloquear el bucle de voz principal.

## 🛡️ Seguridad y Permisos

Al usar `shell=True`, el agente tiene exactamente **los mismos permisos que el usuario que ejecuta el script `coldtemplar_asistente.py`**.

- **Modo Usuario Normal:** Si ejecutas el asistente sin `sudo`, no podrá formatear discos ni instalar paquetes que requieran root a menos que le hables de forma explícita pidiendo permisos, y requerirá que tengas configurado sudo sin contraseña (o el comando fallará de forma segura).
- **Límites de tiempo:** El `timeout=15` previene que comandos interactivos (como un `nano` o un prompt interactivo) bloqueen el asistente.

## 🎯 Cómo Probarlo Ahora Mismo

Inicia tu asistente y prueba decir:
> 🗣️ *"ColdTemplar, ejecuta un comando para mostrar el directorio actual"*

En tu terminal deberías ver:
```text
🖥️  [Sistema]: Ejecutando -> pwd
✅ Salida:
/home/coldtemplar/ColdTemplar-Labs
```

## 🔧 Cómo Extender esta Habilidad

Si notas que a veces genera comandos peligrosos o incorrectos, puedes editar el *System Prompt* en la función `generate_bash_command` del archivo `coldtemplar_asistente.py`:

```python
system_prompt = (
    "Eres un administrador de sistemas Linux experto. "
    "Traduce la petición del usuario a un ÚNICO comando de terminal bash válido. "
    "REGLAS: Responde ÚNICAMENTE con el comando. NO uses markdown. NO des explicaciones. "
    "NO uses comandos destructivos como rm -rf. " # <--- Añade reglas de seguridad aquí
)
```

---
*Documentado por: ColdTemplar System Assistants*
*Nivel de Autorización: Total*