# Versión 0.7.1 — Estabilización de voz e interfaz

## Filtro de ruido y timeout

El reconocedor entrega ahora `RecognitionResult`, incluyendo la probabilidad de
ausencia de voz y la confianza media de Whisper. `VoiceService` descarta antes
de procesar cualquier transcripción con alta probabilidad de silencio o baja
confianza. Esto impide que ruido ambiente llegue al cerebro.

Una sesión iniciada con «Nix» expira a los seis segundos configurables si no
llega una orden válida. Las intervenciones no fiables no reinician ese plazo.

## Síntesis

`SpeechService` reutiliza el motor TTS en su hilo dedicado en vez de crearlo
para cada respuesta, reduciendo latencia y puntos de bloqueo. Busca una voz
española disponible y comunica cualquier fallo al `StateStore`; por tanto, una
respuesta silenciosa queda visible como estado diagnosticable.

## Ventana y esfera

La activación, escucha, respuesta, errores y finalización de acciones ya no
abren el Control Center. La única presencia permanente es la esfera. La ventana
sólo se abre por doble clic en ella, acciones explícitas de bandeja o futuras
acciones de usuario.

## Límite físico

Las métricas de Whisper y las pruebas simuladas filtran ruido lógico. La
calibración definitiva sigue dependiendo de micrófono, ganancia de Windows y
ruido del entorno; se debe probar en el equipo real antes de ajustar valores.
