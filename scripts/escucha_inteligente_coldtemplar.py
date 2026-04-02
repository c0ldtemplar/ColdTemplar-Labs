import sounddevice as sd
from scipy.io.wavfile import write
import os
import subprocess
from faster_whisper import WhisperModel

# Configuración de Audio
fs = 16000
seconds = 5
filename = "/tmp/orden_coldtemplar.wav"

# Inicializar Whisper (Carga el modelo en memoria una vez)
print("⚙️  Cargando motores de IA local...")
model = WhisperModel("tiny", device="cpu", compute_type="int8")

def hablar(texto):
    """Llama a tu script de Piper para hablar"""
    # Usamos shlex o comillas para evitar errores con caracteres especiales
    texto_limpio = texto.replace('"', '').replace('\n', ' ')
    os.system(f'~/habla_coldtemplar.sh "{texto_limpio}"')

def preguntar_ollama(prompt):
    """Envía el texto a Ollama y captura la respuesta"""
    print(f"🤔 Pensando respuesta para: {prompt}")
    # Limitamos la respuesta a algo breve para que Piper no tarde horas
    instruccion = f"{prompt}. Responde de forma breve y concisa en una sola frase."
    
    try:
        resultado = subprocess.check_output(
            ['ollama', 'run', 'llama3', instruccion], 
            stderr=subprocess.STDOUT
        ).decode('utf-8').strip()
        return resultado
    except Exception as e:
        return "Lo siento Rober, tuve un error al conectar con mi cerebro local."

print("\n🎤 [ColdTemplar] Escuchando (5 seg)... Di algo.")

try:
    # 1. Grabar Audio
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, myrecording)

    # 2. Transcribir (Speech-to-Text)
    print("🧠 Procesando voz...")
    segments, _ = model.transcribe(filename, beam_size=5, language="es")
    text = " ".join([segment.text for segment in segments]).strip()

    if text:
        print(f"💬 Dijiste: {text}")
        
        # 3. Generar respuesta con Ollama (Cerebro)
        respuesta_ia = preguntar_ollama(text)
        print(f"🤖 IA dice: {respuesta_ia}")
        
        # 4. Hablar (Text-to-Speech)
        hablar(respuesta_ia)
    else:
        print("❌ No detecté voz.")
        hablar("No te he escuchado bien, Rober.")

except Exception as e:
    print(f"⚠️ Error en el sistema: {e}")
