# Preparación de NYX para un nuevo PC

## Instalación reproducible

1. Instala Python 3.11 o posterior y Git.
2. Clona el repositorio y abre PowerShell en su carpeta.
3. Ejecuta `Set-ExecutionPolicy -Scope Process Bypass` si Windows bloquea scripts locales.
4. Ejecuta `./scripts/setup.ps1 -Profile Full -Dev`.
5. Copia y revisa `.env` (el script lo crea desde `.env.example` si no existe).
6. Instala Ollama y descarga el modelo configurado: `ollama pull llama3.2:3b`.
7. Inicia con `.venv\Scripts\python.exe main.py`.

`-Profile Core` instala únicamente las dependencias no visuales ni de voz. Las dependencias están separadas en `requirements/` para que el entorno no dependa de una lista manual de paquetes.

Si se necesita conservar el motor Whisper clásico como contingencia, instala de
forma explícita `pip install openai-whisper`; la instalación estándar usa
`faster-whisper` y no descarga modelos hasta que se configura/ejecuta el STT.

## Voz de producción

La configuración recomendada combina un detector acústico de wake word Porcupine con `faster-whisper` y VAD para órdenes. La detección se ejecuta en dos fases: Porcupine despierta a NYX; el STT solo se carga para la orden. Sin clave y modelo `.ppn` de Porcupine, NYX conserva el modo de compatibilidad basado en transcripción, pero no ofrece el mismo rechazo de ruido.

Para configurar el detector acústico:

1. Crea en Picovoice un wake word español personalizado para **Nix**.
2. Guarda la clave en `PICOVOICE_ACCESS_KEY` y el archivo `.ppn` fuera de Git.
3. Define `NYX_PORCUPINE_KEYWORD_PATH` y, si procede, `NYX_PORCUPINE_MODEL_PATH`.
4. Ajusta `NYX_WAKE_SENSITIVITY` de forma conservadora; el valor recomendado inicial es `0.45`.
5. Ejecuta manualmente `python scripts/voice_calibrate.py` en silencio para medir el ruido del equipo.

El servicio guarda eventos acotados de voz (`wake_accepted`, `wake_rejected`, duración de transcripción y fin de sesión) en `VoiceDiagnostics`, para que un centro de control futuro pueda mostrarlos sin inundar al usuario de logs.

## Síntesis de voz

`pyttsx3` sigue siendo el motor por defecto para conservar un arranque local. El adaptador `PiperProvider` permite seleccionar Piper mediante `NYX_TTS_ENGINE=piper`, su ejecutable y un modelo local español en `NYX_PIPER_MODEL_PATH`. El modelo no se incluye en Git: ocupa espacio, tiene su propia licencia y debe elegirse por calidad de voz en el nuevo PC. La personalidad genera el estilo de respuesta; el proveedor TTS solo la pronuncia.

## Noticias y seguimiento

`config/news_sources.json` es la lista de fuentes permitidas. Inicialmente incluye MIT Technology Review, TechCrunch, Nature, The Economist y Forbes. La capacidad consume RSS/Atom bajo demanda; no rastrea Internet de forma indiscriminada ni realiza scraping de páginas. El bloque `trackers` contiene el seguimiento de Nil Ojeda con una fuente pública configurable. Las respuestas etiquetan las referencias de terceros y no las presentan como declaraciones propias o hechos confirmados.

## Archivos que no se sincronizan

`.env`, modelos de voz, cachés, logs y entornos virtuales están ignorados. No subas claves de OpenAI/Picovoice ni modelos privados. Usa `.env.example` como plantilla segura.
