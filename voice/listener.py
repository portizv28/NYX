import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import tempfile
import numpy as np

# Cargamos Whisper una sola vez
modelo = whisper.load_model("base")


def escuchar():

    frecuencia = 16000

    umbral = 0.02          # sensibilidad

    silencio_max = 8       # bloques de 0.2 s = 1.6 s

    audio = []

    grabando = False

    silencio = 0

    while True:

        bloque = sd.rec(
            int(0.2 * frecuencia),
            samplerate=frecuencia,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        volumen = np.abs(bloque).mean()

        # -------------------------
        # Detectamos voz
        # -------------------------

        if volumen > umbral:

            grabando = True

            silencio = 0

            audio.append(
                bloque.copy()
            )

        elif grabando:

            silencio += 1

            audio.append(
                bloque.copy()
            )

            if silencio >= silencio_max:

                break

    if not audio:

        return ""

    audio = np.concatenate(audio)

    audio16 = (
        audio * 32767
    ).astype("int16")

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as archivo:

        write(
            archivo.name,
            frecuencia,
            audio16
        )

        resultado = modelo.transcribe(
            archivo.name,
            language="es"
        )

    texto = resultado["text"].strip()

    print("Has dicho:", texto)

    return texto
    