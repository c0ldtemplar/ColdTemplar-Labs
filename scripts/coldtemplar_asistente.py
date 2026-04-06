#!/usr/bin/env python3
"""
ColdTemplar Assistant - Flujo completo de conversación inteligente
Integra: Escucha → Transcripción → Razonamiento → Respuesta por voz
Con sistema de memoria persistente mejorado
"""

import sounddevice as sd
from scipy.io.wavfile import write
from scipy import signal
from collections import deque
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
import time
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
        # Nota: muchos códecs internos reportan mejor su frecuencia real que una fija.
        self.fs_capture = 44100
        self.fs_whisper = 16000  # Tasa que necesita Whisper
        self.listen_seconds = 5
        self.audio_file = "/tmp/orden_coldtemplar.wav"
        self.raw_audio_file = "/tmp/orden_coldtemplar_raw.wav"
        self.preferred_input_name = "ALC256"  # Preferencia de micrófono
        self.vad_rms_threshold = 0.0035
        self.min_peak_threshold = 0.004
        self.noise_calibration_seconds = 0.8
        self.initial_silence_seconds = 6
        self.silence_limit_seconds = 2.2
        self.max_record_seconds = 20
        self.pre_speech_buffer_seconds = 0.35

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

            selected_device = sd.query_devices(self.device_id)
            default_samplerate = int(selected_device["default_samplerate"])
            if default_samplerate > 0:
                self.fs_capture = default_samplerate

            print(
                f"ℹ️  Micrófono seleccionado ID={self.device_id} "
                f"({selected_device['name']}) @ {self.fs_capture}Hz"
            )
        except Exception as e:
            print(f"⚠️  No se pudo resolver el dispositivo de entrada: {e}")
            self.device_id = 2

        # Modelos IA
        print("⚙️  Cargando motores de IA local...")
        self.whisper_model_name = os.environ.get("COLDTEMPLAR_WHISPER_MODEL", "base")
        self.model = WhisperModel(self.whisper_model_name, device="cpu", compute_type="int8")
        print(f"🧠 Whisper cargado con modelo '{self.whisper_model_name}'")
        
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
        🎧 Limpia y normaliza la señal antes de pasarla a Whisper.
        Evita recortar demasiado la voz: usa un filtro suave y luego normaliza amplitud.
        """
        audio = np.asarray(audio_data, dtype=np.float32).reshape(-1)
        if audio.size == 0:
            return audio

        # Eliminar offset DC para estabilizar la energía de la voz.
        audio = audio - float(np.mean(audio))

        # Filtro suave: quitar graves extremos sin comerse consonantes.
        if audio.size > 64:
            b, a = signal.butter(2, 70, btype='highpass', fs=fs)
            audio = signal.filtfilt(b, a, audio)
            b, a = signal.butter(2, 7600, btype='lowpass', fs=fs)
            audio = signal.filtfilt(b, a, audio)

        # Compresión suave para levantar voz baja sin saturar.
        audio = np.tanh(audio * 1.8)

        peak = float(np.max(np.abs(audio)))
        if peak > 1e-6:
            target_peak = 0.85
            audio = np.clip(audio * (target_peak / peak), -1.0, 1.0)

        return audio.astype(np.float32)

    def calibrate_noise_floor(self, device_to_use):
        """
        Mide ruido ambiente antes de escuchar para adaptar umbrales del VAD.
        Esto ayuda cuando el micrófono está lejos o el entorno tiene ventiladores.
        """
        calibration_frames = max(1, int(self.noise_calibration_seconds * self.fs_capture))
        try:
            sample = sd.rec(
                calibration_frames,
                samplerate=self.fs_capture,
                channels=1,
                dtype="float32",
                device=device_to_use,
            )
            sd.wait()
            mono = np.asarray(sample, dtype=np.float32).reshape(-1)
            if mono.size == 0:
                return

            noise_rms = float(np.sqrt(np.mean(np.square(mono))))
            noise_peak = float(np.max(np.abs(mono)))
            self.vad_rms_threshold = max(0.0025, noise_rms * 2.4)
            self.min_peak_threshold = max(0.0030, noise_peak * 2.1)
            print(
                "🎚️  Calibración ambiente: "
                f"ruido_rms={noise_rms:.6f} ruido_peak={noise_peak:.6f} "
                f"-> umbral_rms={self.vad_rms_threshold:.6f} umbral_peak={self.min_peak_threshold:.6f}"
            )
        except Exception as e:
            print(f"⚠️  No se pudo calibrar ruido ambiente: {e}")
    
    def _record_with_vad(self, device_to_use):
        """Graba audio usando un stream continuo hasta detectar silencio (VAD)."""
        q = queue.Queue()
        
        def audio_callback(indata, frames, time, status):
            q.put(indata.copy())

        recording_chunks = []
        silence_frames = 0
        max_frames = int(self.max_record_seconds * self.fs_capture)
        silence_limit_frames = int(self.silence_limit_seconds * self.fs_capture)
        total_frames = 0
        has_spoken = False
        pre_speech_chunks = deque()
        pre_speech_frames = 0
        target_pre_speech_frames = int(self.pre_speech_buffer_seconds * self.fs_capture)
        
        with sd.InputStream(
            samplerate=self.fs_capture,
            channels=1,
            dtype="float32",
            blocksize=2048,
            device=device_to_use,
            callback=audio_callback,
        ):
            while total_frames < max_frames:
                chunk = q.get()
                recording_chunks.append(chunk)
                total_frames += len(chunk)
                
                mono_chunk = np.asarray(chunk, dtype=np.float32).reshape(-1)
                peak = float(np.max(np.abs(mono_chunk)))
                rms = float(np.sqrt(np.mean(np.square(mono_chunk))))
                pre_speech_chunks.append(chunk)
                pre_speech_frames += len(chunk)
                while pre_speech_frames > target_pre_speech_frames and pre_speech_chunks:
                    removed = pre_speech_chunks.popleft()
                    pre_speech_frames -= len(removed)

                # Combinar RMS y pico evita perder voz suave o sílabas cortas.
                if rms < self.vad_rms_threshold and peak < self.min_peak_threshold:
                    silence_frames += len(chunk)
                else:
                    if not has_spoken and pre_speech_chunks:
                        recording_chunks = list(pre_speech_chunks) + recording_chunks
                        pre_speech_chunks.clear()
                        pre_speech_frames = 0
                    silence_frames = 0
                    has_spoken = True
                    
                # Si el usuario ya habló y hace una pausa larga, cortar el stream
                if has_spoken and silence_frames >= silence_limit_frames:
                    break
                # Si pasan varios segundos de silencio total al inicio, cancelar.
                if not has_spoken and total_frames >= int(self.initial_silence_seconds * self.fs_capture):
                    break

        if not recording_chunks:
            return np.zeros(0, dtype=np.float32)

        return np.concatenate(recording_chunks, axis=0).reshape(-1)

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
            self.calibrate_noise_floor(self.device_id)
            print(f"🎧 Usando dispositivo id={self.device_id} tasa={self.fs_capture}Hz")
            recording = self._record_with_vad(self.device_id)

        except Exception as e:
            print(f"❌ Error al grabar en dispositivo primario: {e}")
            try:
                print("🔁 Reintentando con dispositivo por defecto")
                self.calibrate_noise_floor('default')
                recording = self._record_with_vad('default')
            except Exception as e2:
                print(f"❌ Error alternativo: {e2}")
                return False

        if recording.size == 0:
            print("⚠️  No se grabó audio útil.")
            return False

        raw_peak = float(np.max(np.abs(recording)))
        raw_rms = float(np.sqrt(np.mean(np.square(recording))))
        print(f"📈 Señal cruda: peak={raw_peak:.6f} rms={raw_rms:.6f}")
        if raw_peak < self.min_peak_threshold:
            print("⚠️  Atención: no se detectó voz clara. Señal muy baja.")
            return False

        write(self.raw_audio_file, self.fs_capture, (np.clip(recording, -1.0, 1.0) * 32767).astype(np.int16))
            
        # Resamplear a 16000 Hz para Whisper
        if self.fs_capture != self.fs_whisper:
            num_samples = int(len(recording) * self.fs_whisper / self.fs_capture)
            recording = signal.resample(recording, num_samples)

        # Limpiar y normalizar antes de transcribir
        recording = self.apply_voice_filter(recording, self.fs_whisper)

        write(self.audio_file, self.fs_whisper, (recording * 32767).astype(np.int16))
        processed_peak = float(np.max(np.abs(recording)))
        processed_rms = float(np.sqrt(np.mean(np.square(recording))))
        print(
            f"💾 WAV creado ({self.fs_whisper}Hz) - Duración: {len(recording)/self.fs_whisper:.1f}s "
            f"peak={processed_peak:.6f} rms={processed_rms:.6f}"
        )
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
            segments, info = self.model.transcribe(
                self.audio_file,
                beam_size=8,
                best_of=3,
                language="es",
                vad_filter=True,
                condition_on_previous_text=False,
                temperature=0,
                no_speech_threshold=0.45,
                compression_ratio_threshold=2.2,
                log_prob_threshold=-0.8,
                initial_prompt="Transcribe con precisión en español latino, respetando palabras comunes y nombres propios."
            )
            text = " ".join([seg.text for seg in segments]).strip()
            print(f"📝 Whisper detectó idioma={info.language} prob={info.language_probability:.2f}")
            
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
                ["bash", tts_script, text_clean],
                timeout=60
            )
            time.sleep(0.35)
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

        def has_exact_phrase(phrases):
            return any(phrase in text_norm for phrase in phrases)

        def has_word(words_to_match):
            return any(word in words for word in words_to_match)

        # === COMANDOS DE TERMINAR SESIÓN ===
        if has_exact_phrase(["adios", "hasta luego", "nos vemos"]) or (
            len(words) <= 3 and has_word({"terminar", "salir", "apagar", "desconectar", "bye"})
        ):
            return "exit"

        # === COMANDOS DE AYUDA ===
        if has_exact_phrase(["que puedes hacer", "cual es tu funcion", "tus funciones"]) or (
            len(words) <= 4 and has_word({"ayuda", "help", "instrucciones"})
        ):
            return "help"

        # === COMANDOS DE ESTADO/REPORTE ===
        if has_exact_phrase(["estado del sistema", "reporte del sistema", "diagnostico del sistema"]) or (
            len(words) <= 4 and has_word({"reporte", "diagnostico", "status"})
        ):
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
            return "Sistema en línea y estable."
        except Exception:
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
