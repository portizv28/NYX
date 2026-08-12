# Pipeline de voz de producción

## Arquitectura

NYX ya no depende de un único motor. En reposo, `WakeEngine` puede usar un
detector acústico de baja latencia; tras activarse, `SpeechRecognizer` transcribe
la orden con VAD y entrega una métrica de fiabilidad. Ambos contratos son
intercambiables y `VoiceService` no conoce sus bibliotecas concretas.

## Configuración recomendada

Para obtener detección acústica fiable de «Nix», crea un wake word personalizado
en Picovoice con la frase **Nix**, descarga el archivo `.ppn` y define estas
variables locales, nunca en Git:

```powershell
$env:PICOVOICE_ACCESS_KEY = "..."
$env:NYX_PORCUPINE_KEYWORD_PATH = "C:\ruta\a\nix_windows.ppn"
$env:NYX_WAKE_SENSITIVITY = "0.55"
```

Porcupine requiere una clave y un modelo personalizado; procesa audio por
frames localmente y está diseñado para wake words siempre activos en Windows.
Su sensibilidad es configurable: aumentarla reduce omisiones a costa de más
falsos positivos. [Documentación oficial de Porcupine](https://picovoice.ai/docs/quick-start/porcupine-python/).

Para órdenes, instala las dependencias de `requirements.txt`. Por defecto NYX
elige `faster-whisper`; su VAD integrado filtra partes sin voz antes de
transcribir. Si no está instalado, usa automáticamente `openai-whisper`.
Puedes elegir motor y modelo:

```powershell
$env:NYX_STT_ENGINE = "faster_whisper"
$env:NYX_WHISPER_MODEL = "base"
```

`base` es el punto de partida recomendado para español en un portátil. `small`
prioriza precisión si el equipo responde bien; `tiny` prioriza velocidad. El
VAD de faster-whisper está documentado por su proyecto oficial. [README de faster-whisper](https://github.com/SYSTRAN/faster-whisper/blob/master/README.md?plain=1).

## Fallback seguro

Sin las variables de Porcupine, NYX conserva el detector por transcripción y
no necesita ninguna credencial. La diferencia es que no puede ofrecer la misma
precisión ni latencia de un modelo acústico entrenado específicamente para
«Nix».
