# 🌟 Guía: Cómo Sacar el Máximo Provecho a tu Agente ColdTemplar

Has pasado de tener un asistente que solo "habla", a tener un **Agente Autónomo** que "actúa". Para que realice todas las tareas en tus cuentas digitales por ti, usaremos la integración con **n8n**.

## 🚀 Paso 1: Encender las "Manos Digitales"

Abre una terminal en la carpeta principal de tu proyecto y levanta el contenedor de n8n:

```bash
cd ~/ColdTemplar-Labs
docker-compose up -d
```
*Esto descargará e iniciará n8n en el puerto `5678` de tu máquina.*

## ⚙️ Paso 2: Crear el Flujo Principal (El "Cerebro de Acción")

1. Abre tu navegador y ve a `http://localhost:5678`.
2. Crea tu cuenta local de administrador (es 100% privada).
3. Haz clic en **Add Workflow** y crea lo siguiente:

### Nodo 1: Webhook (La Oreja)
- **Tipo:** Webhook
- **Method:** POST
- **Path:** `coldtemplar-tasks`
- *Importante:* Ponlo en modo "Production" (Listen for events).

### Nodo 2: Advanced AI (El Razonamiento)
- Conecta el Webhook a un nodo de tipo **AI Agent**.
- En el AI Agent, necesitas un modelo. Si tienes una API Key de **OpenAI/Claude**, úsala. Si quieres que sea 100% local, conecta un nodo **Ollama Chat Model** apuntando a tu `http://host.docker.internal:11434` (llama3).
- **Prompt del Agente:** *"Eres el brazo ejecutor de ColdTemplar. Analiza la petición del usuario y usa las herramientas disponibles para cumplirla."*

### Nodo 3: Las Herramientas (Tools)
Aquí es donde conectas tus cuentas. En n8n, puedes arrastrar nodos de herramientas y conectarlos al Agente de IA:

- **Gmail / Outlook:** Agrega la herramienta de Google. Autentícate una sola vez usando OAuth2 (n8n te guía en el proceso).
- **Notion / Trello:** Conecta la herramienta para crear bases de datos y tarjetas. Solo pegas tu API Key de Notion.
- **Google Calendar:** Autentícate para que el agente pueda leer si tienes tiempo libre o agendar eventos.

*El Agente de IA automáticamente sabrá qué herramienta usar basado en lo que le pediste a ColdTemplar por el micrófono.*

## 💡 Ejemplos Prácticos

Una vez conectadas las herramientas a n8n, puedes decirle al micrófono de ColdTemplar:

> 🗣️ *"ColdTemplar, envía un correo a Juan diciendo que el reporte estará listo a las 5, y crea una tarea en Notion para recordar revisarlo mañana."*

**Lo que pasa por detrás:**
1. Python escucha y transcribe.
2. Detecta la intención "automatización" y envía el texto al Webhook de n8n.
3. El Agente de IA de n8n lee la frase y llama internamente a la API de Gmail y a la API de Notion usando tus credenciales guardadas.
4. ¡Tarea completada!