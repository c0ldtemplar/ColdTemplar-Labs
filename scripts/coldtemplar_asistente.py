#!/usr/bin/env python3
"""
ColdTemplar Assistant - Flujo completo de conversación inteligente
Integra: Escucha → Transcripción → Razonamiento → Respuesta por voz
Con sistema de memoria persistente mejorado
"""

import sounddevice as sd
from scipy.io.wavfile import write
from scipy import signal
import numpy as np
import subprocess
import os
import sys
import json
import unicodedata
import requests
import difflib
import queue
import sqlite3
from faster_whisper import WhisperModel
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

class ColdTemplarAssistant:
    """
    🤖 Clase Principal: ColdTemplarAssistant
    
    ¿Por qué? 
    Orquesta todo el ciclo de vida del asistente local. Conecta el micrófono (entrada),
    Whisper (transcripción), Llama 3 (razonamiento) y Piper (salida de voz).
    Ahora con sistema de memoria persistente mejorado.
    
    💡 Ejemplo de instanciación:
        asistente = ColdTemplarAssistant()
        asistente.run_interactive()
    """
    
    def __init__(self):
        # Configuración de audio
        # Nota: ALC256 solo soporta 44100 Hz o 48000 Hz
        self.fs_capture = 44100  # Tasa de captura (lo que soporta el hw)
        self.fs_whisper = 16000  # Tasa que necesita Whisper
        self.listen_seconds = 5
        self.audio_file = "/tmp/orden_coldtemplar.wav"
        self.preferred_input_name = "ALC256"  # Preferencia de micrófono

        # Determinar dispositivo de entrada
        self.device_id = None
        try:
            for i, dev in enumerate(sd.query_devices()):
                if dev['max_input_channels'] > 0 and self.preferred_input_name in dev['name']:
                    self.device_id = i
                    print(f"🎯 Dispositivo preferido encontrado: {dev['name']} (id={i})")
                    break

            if self.device_id is None:
                default_input = sd.default.device
                if isinstance(default_input, (tuple, list)):
                    self.device_id = int(default_input[0])
                elif isinstance(default_input, int):
                    self.device_id = default_input
                elif hasattr(default_input, 'input'):
                    self.device_id = int(default_input.input)
                else:
                    self.device_id = 2

                print(f"⚠️  No se encontró '{self.preferred_input_name}'. Usando default device id={self.device_id}")

            print(f"ℹ️  Micrófono seleccionado ID={self.device_id} ({sd.query_devices(self.device_id)['name']})")
        except Exception as e:
            print(f"⚠️  No se pudo resolver el dispositivo de entrada: {e}")
            self.device_id = 2

        # Modelos IA
        print("⚙️  Cargando motores de IA local...")
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
        
        # Sistema de memoria persistente
        self.db_path = Path.home() / "ColdTemplar-Labs" / "coldtemplar_memory.db"
        self.init_memory_db()
        
        # Log de sesión
        self.session_log = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = Path.home() / "ColdTemplar-Labs" / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Comandos especiales
        self.exit_commands = {"adiós", "terminar", "salir", "apagar", "adios"}
        self.memory_commands = {"recuerda", "recuerdame", "historial", "contexto", "memoria"}
        
        print("✅ Sistema listo con memoria persistente.\n")
    
    def init_memory_db(self):
        """Inicializa la base de datos SQLite para memoria persistente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Crear tablas si no existen
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                turn INTEGER,
                user_text TEXT,
                assistant_text TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                user_id TEXT,
                key TEXT,
                value TEXT,
                timestamp TIMESTAMP,
                PRIMARY KEY (user_id, key)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                value REAL,
                timestamp TIMESTAMP
            )
        ''')
        
        # Crear índices para mejor rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_preferences_user ON preferences(user_id)')
        
        conn.commit()
        conn.close()
    
    def apply_voice_filter(self, audio_data, fs):
        """
        🎧 Aplica un filtro pasa-banda matemático para reducir ruido de fondo.
        Elimina zumbidos graves (<80Hz) y siseos agudos (>7000Hz).
        Mantiene la latencia ultrabaja (ms) usando matemáticas puras (SciPy).
        """
        # Filtro Butterworth de orden 4 (rango de voz principal)
        b, a = signal.butter(4, [80, 7000], btype='bandpass', fs=fs)
        return signal.filtfilt(b, a, audio_data, axis=0)
    
    def _record_with_vad(self, device_to_use):
        """Graba audio usando un stream continuo hasta detectar silencio (VAD)."""
        q = queue.Queue()
        
        def audio_callback(indata, frames, time, status):
            q.put(indata.copy())

        recording_chunks = []
        silence_frames = 0
        max_frames = int(15 * self.fs_capture) # Máximo absoluto de seguridad: 15 seg
        silence_limit_frames = int(1.5 * self.fs_capture) # Cortar tras 1.5 seg de silencio
        total_frames = 0
        has_spoken = False
        
        with sd.InputStream(samplerate=self.fs_capture, channels=1, device=device_to_use, callback=audio_callback):
            while total_frames < max_frames:
                chunk = q.get()
                recording_chunks.append(chunk)
                total_frames += len(chunk)
                
                peak = np.max(np.abs(chunk))
                # Umbral de energía para considerar que hay voz humana
                if peak < 0.015:
                    silence_frames += len(chunk)
                else:
                    silence_frames = 0
                    has_spoken = True
                    
                # Si el usuario ya habló y hace una pausa larga, cortar el stream
                if has_spoken and silence_frames >= silence_limit_frames:
                    break
                # Si pasan 5 segundos de silencio total al inicio, cancelar
                if not has_spoken and total_frames >= int(5 * self.fs_capture):
                    break

        return np.concatenate(recording_chunks, axis=0)

    def listen(self):
        """
        🎤 Captura audio del micrófono local con detección de voz (VAD).
        
        ¿Por qué? 
        En lugar de forzar un límite fijo, el asistente escucha de manera continua 
        hasta que detecta una pausa natural en la voz, mejorando la latencia y experiencia.
        
        💡 Ejemplo de salida esperada en terminal:
            🎤 Escuchando... (Habla ahora, me detendré al hacer una pausa)
            💾 WAV creado en /tmp/orden_coldtemplar.wav (16000Hz)
        """
        print("🎤 Escuchando... (Habla ahora, me detendré al hacer una pausa)")
        try:
            print(f"🎧 Usando dispositivo id={self.device_id} tasa={self.fs_capture}Hz")
            recording = self._record_with_vad(self.device_id)

        except Exception as e:
            print(f"❌ Error al grabar en dispositivo primario: {e}")
            try:
                print("🔁 Reintentando con dispositivo por defecto")
                recording = self._record_with_vad('default')
            except Exception as e2:
                print(f"❌ Error alternativo: {e2}")
                return False
                
        peak = float(np.max(np.abs(recording)))
        print(f"📈 Pico de señal final: {peak:.6f}")
        if peak < 0.01:
            print("⚠️  Atención: no se detectó voz clara. Señal muy baja.")
            return False
            
        # Resamplear a 16000 Hz para Whisper
        if self.fs_capture != self.fs_whisper:
            num_samples = int(len(recording) * self.fs_whisper / self.fs_capture)
            recording = signal.resample(recording, num_samples)

        # Aplicar filtro de reducción de ruido ultrarrápido
        recording = self.apply_voice_filter(recording, self.fs_whisper)

        write(self.audio_file, self.fs_whisper, (recording * 32767).astype(np.int16))
        print(f"💾 WAV creado ({self.fs_whisper}Hz) - Duración de captura: {len(recording)/self.fs_whisper:.1f}s")
        return True
    
    def transcribe(self):
        """
        🧠 Convierte el audio grabado a texto (Speech-to-Text).
        
        ¿Por qué?
        Utiliza Faster Whisper de forma local para traducir el archivo WAV
        a un string en español, normalizando y tolerando ruidos de fondo.
        
        💡 Ejemplo de retorno:
            "envia un correo a mi jefe"
        """
        try:
            print("🧠 Transcribiendo...")
            segments, _ = self.model.transcribe(self.audio_file, 
                                                beam_size=5, language="es")
            text = " ".join([seg.text for seg in segments]).strip()
            
            # 🛡️ Filtro de Alucinaciones (Defensive Normalization)
            # Whisper a veces inventa sílabas sueltas o puntuación con el ruido blanco
            texto_limpio = self.normalize_text(text).replace(" ", "")
            if len(texto_limpio) < 2:
                return ""
                
            return text
        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
            return ""
    
    def think(self, prompt):
        """
        🤖 Genera una respuesta inteligente utilizando Ollama (LLM Local).
        
        ¿Por qué?
        Inyecta un system prompt estricto para forzar a Llama 3 a responder en 
        español nativo, de forma concisa y directa (máximo 2 frases).
        
        💡 Ejemplo de uso:
            respuesta = self.think("¿Cuál es la capital de Francia?")
            # Retorna: "La capital de Francia es París."
        """
        try:
            print("🤔 Pensando...")
            
            # Sistema de prompts mejorado para Ollama
            system_prompt = (
                "Eres ColdTemplar, una asistente de IA femenina, inteligente y eficiente. "
                "REGLAS IMPORTANTES:\n"
                "1. Responde SIEMPRE en español español latino, con tono conversacional y amable.\n"
                "2. Máximo 2 frases por respuesta, conciso y directo.\n"
                "3. Si tienes ejemplos, dálos brevemente.\n"
                "4. NUNCA respondas en inglés, NUNCA.\n"
                "5. Si no entiendes, pide aclaración en español.\n"
                "6. Sé práctica y orientada a resultados."
            )

            entrada = f"{system_prompt}\n\nPregunta del usuario:\n{prompt}\n\nRespuesta en español (máximo 2 frases):" 
            
            result = subprocess.run(
                ['ollama', 'run', 'llama3', entrada],
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, 'OLLAMA_MODELS': os.path.expanduser('~/.ollama/models')}
            )
            
            response = result.stdout.strip()
            if not response:
                return "No he entendido bien tu petición. ¿Puedes reformularla en español, por favor?"

            # Validar que la respuesta no sea inglés
            if any(word in response.lower() for word in ["sorry,", "i don't", "i can't", "unable to", "cannot"]):
                return "Disculpa, no pude procesarlo. Por favor, pregunta de nuevo en español claro."

            return response

        except subprocess.TimeoutExpired:
            return "La respuesta tardó demasiado. Intenta una pregunta más simple."
        except Exception as e:
            print(f"⚠️  Error en razonamiento: {e}")
            return "No pude conectar con el cerebro local. Intenta otra vez."
    
    def speak(self, text):
        """
        🔊 Reproduce la respuesta por voz (Text-to-Speech).
        
        ¿Por qué?
        Llama al script Bash 'habla_coldtemplar.sh' que ejecuta Piper TTS 
        para generar un audio natural sin depender de APIs en la nube.
        
        💡 Ejemplo de uso:
            self.speak("Hola, soy ColdTemplar. Sistema en línea.")
        """
        try:
            # Limpiar el texto
            text_clean = text.replace('"', '').replace('\n', ' ')[:200]

            # Ruta robusta al script de TTS.
            tts_script = os.path.expanduser("~/ColdTemplar-Labs/scripts/habla_coldtemplar.sh")
            if not os.path.exists(tts_script):
                tts_script = os.path.expanduser("~/habla_coldtemplar.sh")

            if not os.path.exists(tts_script):
                print(f"⚠️  No encontré el script TTS: {tts_script}")
                return

            subprocess.run(
                f'bash "{tts_script}" "{text_clean}"',
                shell=True,
                timeout=60
            )
        except Exception as e:
            print(f"⚠️  Error en reproducción: {e}")
    
    def normalize_text(self, text: str) -> str:
        """Normaliza y limpia texto para matching."""
        text = text.lower().strip()
        text = unicodedata.normalize('NFKD', text)
        text = ''.join([c for c in text if not unicodedata.combining(c)])
        return text

    def closest_command(self, text, options, cutoff=0.6):
        matches = difflib.get_close_matches(text, options, n=1, cutoff=cutoff)
        return matches[0] if matches else None

    def process_command(self, text):
        """
        🔀 Procesa y enruta comandos especiales del usuario usando Fuzzy Matching.
        
        ¿Por qué?
        Evita enviar comandos de acción local al LLM, ahorrando tiempo y memoria. 
        Detecta variaciones fonéticas o errores leves del STT (ej. "habre" vs "abre").
        
        💡 Ejemplo de evaluación:
            self.process_command("envia un coreo") # Retorna "automation"
            self.process_command("que puedes hacer") # Retorna "help"
        """
        text_norm = self.normalize_text(text)
        words = text_norm.split()
        
        def contains_keyword(keywords, cutoff=0.8):
            for kw in keywords:
                # Coincidencia exacta de substring (muy rápida)
                if kw in text_norm:
                    return True
                # Fuzzy matching para palabras individuales
                if ' ' not in kw:
                    if difflib.get_close_matches(kw, words, n=1, cutoff=cutoff):
                        return True
                # Fuzzy matching para frases (ventana deslizante)
                else:
                    kw_len = len(kw.split())
                    for i in range(len(words) - kw_len + 1):
                        window = " ".join(words[i:i+kw_len])
                        if difflib.SequenceMatcher(None, window, kw).ratio() >= cutoff:
                            return True
            return False

        # === COMANDOS DE TERMINAR SESIÓN ===
        if contains_keyword(["adios", "hasta luego", "terminar", "salir", "apagar", "desconectar", "nos vemos", "bye"]):
            return "exit"

        # === COMANDOS DE AYUDA ===
        if contains_keyword(["ayuda", "help", "que puedes hacer", "tus funciones", "como funciono", "cual es tu funcion", "instrucciones"]):
            return "help"

        # === COMANDOS DE ESTADO/REPORTE ===
        if contains_keyword(["reporte", "estado", "como estoy", "diagnostico", "salud", "status", "como esta"]):
            return "report"

        # === COMANDOS DE CONTROL DE SISTEMA ===
        if contains_keyword(["enciende", "apaga", "abre", "cierra", "ejecuta", "inicia"]):
            return "control"

        # === COMANDOS DE MULTIMEDIA ===
        if contains_keyword(["abre navegador", "abre chrome", "navegador", "google", "internet"]):
            return "open_browser"
        if contains_keyword(["musica", "spotify", "cancion", "reproducir"]):
            return "play_music"

        # === COMANDOS DE AUTOMATIZACIÓN DIGITAL (n8n) ===
        if contains_keyword(["envia un correo", "manda un email", "crea una tarea", "nuevo evento", "tuitea", "publica", "notion", "calendario"]):
            return "automation"

        # === COMANDOS DE MEMORIA ===
        if contains_keyword(["recuerda", "recuerdame", "historial", "contexto", "memoria", "lo que hablamos", "nuestra conversacion"]):
            return "memory"

        return None
    
    def show_help(self):
        """Muestra ayuda sobre funciones disponibles"""
        help_text = (
            "Soy ColdTemplar, tu asistente de voz inteligente. Puedo ayudarte con:\n"
            "• Responder preguntas en español.\n"
            "• Darme instrucciones para tareas.\n"
            "• Consultar el estado del sistema (di 'reporte').\n"
            "• Abrir aplicaciones (di 'abre navegador' o 'abre aplicación').\n"
            "• Reproducir música (di 'poner música' o 'spotify').\n"
            "• Ejecutar tareas digitales como enviar correos o crear tareas (vía n8n).\n"
            "• Recordar conversaciones anteriores (di 'recuerda lo que hablamos').\n"
            "• Consultar nuestro historial (di 'historial').\n"
            "• Obtener contexto de conversaciones recientes (di 'contexto').\n"
            "¿En qué puedo ayudarte?"
        )
        return help_text

    def get_system_report(self):
        """Obtiene reporte del sistema"""
        try:
            # Ejecutar auditoría ligera
            result = subprocess.run(
                "bash ~/ia-tools/auditar_voz.sh --text-only 2>/dev/null || echo 'Sistema online'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() or "Sistema en línea y estable."
        except:
            return "No pude acceder al reporte del sistema."
    
    def save_session(self):
        """Guarda el log de la sesión en JSON"""
        log_file = self.log_dir / f"sesion_{self.session_id}.json"
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'session_id': self.session_id,
                    'timestamp': datetime.now().isoformat(),
                    'turns': self.session_log
                }, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Sesión guardada en: {log_file}")
        except Exception as e:
            print(f"⚠️  No se pudo guardar el log: {e}")
    
    def save_to_memory(self, session_id: str, turn: int, user_text: str, assistant_text: str):
        """Guarda la conversación en la base de datos de memoria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (session_id, turn, user_text, assistant_text, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, turn, user_text, assistant_text, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Obtiene el historial completo de una sesión"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT turn, user_text, assistant_text, timestamp
            FROM conversations
            WHERE session_id = ?
            ORDER BY turn ASC
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'turn': row[0],
            'user_text': row[1],
            'assistant_text': row[2],
            'timestamp': row[3]
        } for row in rows]
    
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """Busca conversaciones que contengan el texto especificado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Búsqueda en user_text y assistant_text
        cursor.execute('''
            SELECT session_id, turn, user_text, assistant_text, timestamp
            FROM conversations
            WHERE user_text LIKE ? OR assistant_text LIKE ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'session_id': row[0],
            'turn': row[1],
            'user_text': row[2],
            'assistant_text': row[3],
            'timestamp': row[4]
        } for row in rows]
    
    def get_context(self, session_id: str, num_turns: int = 3) -> str:
        """Obtiene el contexto reciente de una conversación"""
        history = self.get_conversation_history(session_id)
        
        if not history:
            return "No tengo contexto de conversaciones anteriores."
        
        # Tomar los últimos 'num_turns' turnos
        recent_turns = history[-num_turns:]
        
        context = "En nuestra última conversación, dijiste:\n"
        for turn in recent_turns:
            context += f"• Tú: {turn['user_text']}\n"
            context += f"  Yo: {turn['assistant_text']}\n\n"
        
        return context.strip()
    
    def run_interactive(self):
        """
        🔄 Bucle principal de conversación interactiva (El "Main Loop").
        
        ¿Por qué?
        Mantiene el asistente vivo, alternando continuamente entre escuchar, pensar 
        y hablar, hasta que el usuario dicta un comando de salida o interrumpe.
        
        💡 Flujo esperado:
            1. Escucha -> 2. Transcribe -> 3. Enruta/Piensa -> 4. Habla -> 5. Guarda Log -> (Repite)
        """
        print("\n" + "="*60)
        print("🟢 COLDTEMPLAR ASISTENTE - Modo Interactivo con Memoria Persistente")
        print("="*60)
        print("Commands: 'adiós' para salir, 'reporte' para estado del sistema")
        print("Nuevos comandos: 'recuerda lo que hablamos', 'historial', 'contexto'")
        print("="*60 + "\n")
        
        # Introducción
        self.speak("Sistema en línea, Rober. Estoy escuchando y recordando nuestras conversaciones.")
        
        try:
            turn = 1
            while True:
                print(f"\n--- TURNO {turn} ---")
                
                # 1. ESCUCHAR
                if not self.listen():
                    continue
                
                # 2. TRANSCRIBIR
                texto_usuario = self.transcribe()
                
                if not texto_usuario:
                    print("🌫️  ... (Silencio o ruido ignorado)")
                    continue
                
                print(f"💬 [Tú]: {texto_usuario}")
                
                # 3. DETECTAR COMANDOS ESPECIALES
                comando = self.process_command(texto_usuario)
                
                if comando == "exit":
                    self.speak("Hasta pronto, Rober. Modo de reposo activado.")
                    break
                
                elif comando == "help":
                    respuesta = self.show_help()
                    print(f"📖 [Ayuda]: {respuesta}")
                    self.speak(respuesta)
                
                elif comando == "report":
                    respuesta = self.get_system_report()
                    print(f"📊 [Reporte]: {respuesta}")
                    self.speak(respuesta)
                
                elif comando == "open_browser":
                    respuesta = "Claro, abriendo tu navegador..."
                    print(f"🤖 [IA]: {respuesta}")
                    self.speak(respuesta)
                    os.system("xdg-open https://www.google.com > /dev/null 2>&1 &")
                
                elif comando == "play_music":
                    respuesta = "Perfecto, reproduciendo algo de música tranquila para ti."
                    print(f"🤖 [IA]: {respuesta}")
                    self.speak(respuesta)
                    os.system("spotify &>/dev/null &")
                
                elif comando == "automation":
                    respuesta = "Delegando la tarea a tus automatizaciones..."
                    print(f"🤖 [IA]: {respuesta}")
                    self.speak(respuesta)
                    
                    # Enviar a webhook de n8n
                    try:
                        webhook_url = "http://localhost:5678/webhook/coldtemplar-tasks"
                        payload = {
                            "comando": texto_usuario,
                            "timestamp": datetime.now().isoformat()
                        }
                        requests.post(webhook_url, json=payload, timeout=5)
                        print("✅ Comando de automatización enviado exitosamente a n8n.")
                    except Exception as e:
                        print(f"⚠️ No se pudo conectar con n8n. ¿Está encendido? Error: {e}")
                
                elif comando == "memory":
                    # Manejar comandos de memoria
                    if "recuerda" in texto_usuario or "recuerdame" in texto_usuario:
                        context = self.get_context(self.session_id)
                        respuesta = context
                        print(f"🧠 [Memoria]: {respuesta}")
                        self.speak(respuesta)
                    
                    elif "historial" in texto_usuario:
                        historia = self.get_conversation_history(self.session_id)
                        if historia:
                            respuesta = f"Tenemos {len(historia)} turnos en esta sesión. ¿Quieres que te recuerde algo específico?"
                        else:
                            respuesta = "No tenemos historial en esta sesión aún."
                        print(f"📚 [Historial]: {respuesta}")
                        self.speak(respuesta)
                    
                    elif "contexto" in texto_usuario:
                        context = self.get_context(self.session_id, num_turns=5)
                        respuesta = context
                        print(f"🔄 [Contexto]: {respuesta}")
                        self.speak(respuesta)
                    
                    else:
                        respuesta = "Puedes preguntarme 'recuerda lo que hablamos', 'historial' o 'contexto'"
                        print(f"❓ [Ayuda Memoria]: {respuesta}")
                        self.speak(respuesta)
                
                else:
                    # 4. PENSAR (LLM)
                    respuesta = self.think(texto_usuario)
                    print(f"🤖 [IA]: {respuesta}")
                    
                    # 5. HABLAR (TTS)
                    self.speak(respuesta)
                
                # 6. REGISTRAR EN LOG Y MEMORIA
                self.session_log.append({
                    'turno': turn,
                    'usuario': texto_usuario,
                    'respuesta': respuesta if comando != "exit" else "SESIÓN TERMINADA",
                    'timestamp': datetime.now().isoformat()
                })
                
                # Guardar en memoria persistente
                if comando != "exit":
                    self.save_to_memory(self.session_id, turn, texto_usuario, respuesta)
                
                turn += 1
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Interrupción del usuario (Ctrl+C)")
            self.speak("Sesión terminada por interrupción.")
        
        finally:
            # Guardar log
            self.save_session()
            print("\n✅ Asistente apagado.")

def main():
    """Punto de entrada"""
    try:
        asistente = ColdTemplarAssistant()
        asistente.run_interactive()
    except KeyboardInterrupt:
        print("\n\n⏹️  Términado por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
