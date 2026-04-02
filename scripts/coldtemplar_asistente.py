#!/usr/bin/env python3
"""
ColdTemplar Assistant - Flujo completo de conversación inteligente
Integra: Escucha → Transcripción → Razonamiento → Respuesta por voz
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
import difflib
from faster_whisper import WhisperModel
from datetime import datetime
from pathlib import Path

class ColdTemplarAssistant:
    """Asistente de voz inteligente con contexto y logging"""
    
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
        
        # Log de sesión
        self.session_log = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = Path.home() / "ColdTemplar-Labs" / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Comandos especiales
        self.exit_commands = {"adiós", "terminar", "salir", "apagar", "adios"}
        
        print("✅ Sistema listo.\n")
    
    def listen(self):
        """Captura audio del micrófono"""
        print("🎤 Escuchando (5 seg)...")
        try:
            print(f"🎧 Usando dispositivo id={self.device_id} tasa={self.fs_capture}Hz")
            recording = sd.rec(int(self.listen_seconds * self.fs_capture), 
                             samplerate=self.fs_capture, channels=1, device=self.device_id)
            sd.wait()

            peak = float(np.max(np.abs(recording)))
            print(f"📈 Pico de señal raw: {peak:.6f}")
            if peak < 0.01:
                print("⚠️  Atención: señal muy baja; revisa silencio, ganancia o micrófono apagado")

            # Resamplear a 16000 Hz para Whisper
            if self.fs_capture != self.fs_whisper:
                num_samples = int(len(recording) * self.fs_whisper / self.fs_capture)
                recording = signal.resample(recording, num_samples)

            write(self.audio_file, self.fs_whisper, (recording * 32767).astype(np.int16))
            print(f"💾 WAV creado en {self.audio_file} ({self.fs_whisper}Hz)")
            return True

        except Exception as e:
            print(f"❌ Error al grabar en dispositivo primario: {e}")
            try:
                print("🔁 Reintentando con dispositivo por defecto")
                recording = sd.rec(int(self.listen_seconds * self.fs_capture), 
                                 samplerate=self.fs_capture, channels=1, device='default')
                sd.wait()
                peak = float(np.max(np.abs(recording)))
                print(f"📈 Pico de señal raw (fallback): {peak:.6f}")

                if self.fs_capture != self.fs_whisper:
                    num_samples = int(len(recording) * self.fs_whisper / self.fs_capture)
                    recording = signal.resample(recording, num_samples)

                write(self.audio_file, self.fs_whisper, (recording * 32767).astype(np.int16))
                print(f"💾 WAV fallback creado en {self.audio_file} ({self.fs_whisper}Hz)")
                return True
            except Exception as e2:
                print(f"❌ Error alternativo: {e2}")
                return False
    
    def transcribe(self):
        """Convierte audio a texto (Speech-to-Text)"""
        try:
            print("🧠 Transcribiendo...")
            segments, _ = self.model.transcribe(self.audio_file, 
                                                beam_size=5, language="es")
            text = " ".join([seg.text for seg in segments]).strip()
            return text
        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
            return ""
    
    def think(self, prompt):
        """Genera respuesta inteligente con Ollama en español"""
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
        """Reproduce respuesta por voz (Text-to-Speech)"""
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
        """Procesa comandos especiales del usuario con detección robusta en español"""
        text_norm = self.normalize_text(text)

        # === COMANDOS DE TERMINAR SESIÓN ===
        exit_keywords = ["adios", "hasta luego", "terminar", "salir", "apagar", "desconectar", "nos vemos", "bye"]
        if any(keyword in text_norm for keyword in exit_keywords):
            return "exit"

        # === COMANDOS DE AYUDA ===
        help_keywords = ["ayuda", "help", "que puedes hacer", "tus funciones", "como funciono", "cual es tu funcion", "instrucciones"]
        if any(keyword in text_norm for keyword in help_keywords):
            return "help"

        # === COMANDOS DE ESTADO/REPORTE ===
        report_keywords = ["reporte", "estado", "como estoy", "diagnostico", "salud", "status", "como esta"]
        if any(keyword in text_norm for keyword in report_keywords):
            return "report"

        # === COMANDOS DE CONTROL DE SISTEMA ===
        if any(x in text_norm for x in ["enciende", "apaga", "abre", "cierra", "ejecuta", "inicia"]):
            return "control"

        # === COMANDOS DE MULTIMEDIA ===
        if any(x in text_norm for x in ["abre navegador", "abre chrome", "navegador", "google", "internet"]):
            return "open_browser"
        if any(x in text_norm for x in ["musica", "spotify", "cancion", "reproducir"]):
            return "play_music"

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
    
    def run_interactive(self):
        """Bucle principal de conversación interactiva"""
        print("\n" + "="*60)
        print("🟢 COLDTEMPLAR ASISTENTE - Modo Interactivo")
        print("="*60)
        print("Commands: 'adiós' para salir, 'reporte' para estado del sistema")
        print("="*60 + "\n")
        
        # Introducción
        self.speak("Sistema en línea, Rober. Estoy escuchando.")
        
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
                    print("... (Silencio detectado)")
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
                
                elif comando == "control":
                    respuesta = self.think(texto_usuario)
                    print(f"🤖 [IA]: {respuesta}")
                    self.speak(respuesta)
                
                else:
                    # 4. PENSAR (LLM)
                    respuesta = self.think(texto_usuario)
                    print(f"🤖 [IA]: {respuesta}")
                    
                    # 5. HABLAR (TTS)
                    self.speak(respuesta)
                
                # 6. REGISTRAR EN LOG
                self.session_log.append({
                    'turno': turn,
                    'usuario': texto_usuario,
                    'respuesta': respuesta if comando != "exit" else "SESIÓN TERMINADA",
                    'timestamp': datetime.now().isoformat()
                })
                
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
