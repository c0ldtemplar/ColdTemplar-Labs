import sounddevice as sd
from scipy.io.wavfile import write
import os
from faster_whisper import WhisperModel

fs = 16000
seconds = 5
filename = "/tmp/orden_coldtemplar.wav"

print("\n🎤 [ColdTemplar] Escuchando (5 seg)...")
try:
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, myrecording)

    print("🧠 [ColdTemplar] Procesando voz...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(filename, beam_size=5, language="es")
    text = " ".join([segment.text for segment in segments])

    if text.strip():
        print(f"💬 Dijiste: {text}")
        os.system(f'~/habla_coldtemplar.sh "{text}"')
    else:
        print("❌ No detecté voz.")
except Exception as e:
    print(f"⚠️ Error de audio: {e}")
