import sounddevice as sd
from scipy.io.wavfile import write
import os
import subprocess
from faster_whisper import WhisperModel

# --- CONFIGURACIÓN ---
fs = 16000
seconds = 5  # Tiempo de escucha
filename = "/tmp/orden_coldtemplar.wav"

print("⚙️  Cargando Whisper y Ollama en la GPU...")
model = WhisperModel("tiny", device="cpu", compute_type="int8")

def hablar(texto):
    texto_limpio = texto.replace('"', '').replace('\n', ' ')
    os.system(f'~/habla_coldtemplar.sh "{texto_limpio}"')

def preguntar_ollama(prompt):
    instruccion = f"{prompt}. Responde de forma breve, en una sola frase y como un asistente técnico avanzado."
    try:
        process = subprocess.Popen(['ollama', 'run', 'llama3', instruccion], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, _ = process.communicate()
        return stdout.strip()
    except:
        return "Error de conexión con el núcleo."

# --- BUCLE INTERACTIVO ---
print("\n🟢 MODO INTERACTIVO ACTIVADO. Presiona Ctrl+C para salir.")
hablar("Sistema en línea, Rober. Estoy escuchando.")

try:
    while True:
        print("\n🎤 Escuchando...")
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()
        write(filename, fs, myrecording)

        segments, _ = model.transcribe(filename, beam_size=5, language="es")
        text = " ".join([segment.text for segment in segments]).strip()

        if text:
            print(f"💬 Tú: {text}")
            if "adiós" in text.lower() or "terminar" in text.lower():
                hablar("Entendido. Entrando en modo de reposo.")
                break
            
            respuesta = preguntar_ollama(text)
            print(f"🤖 IA: {respuesta}")
            hablar(respuesta)
        else:
            print("... (Silencio)")
except KeyboardInterrupt:
    print("\nAbortado por el usuario.")
