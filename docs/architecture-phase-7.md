# Arquitectura de NYX — Fase 7: voz

## Flujo de bajo consumo

`WhisperListener` usa `sounddevice.InputStream`: ya no crea WAV temporales ni
abre y cierra un dispositivo de audio para cada bloque. Sólo carga Whisper al
finalizar una intervención con voz. En reposo, `VoiceService` espera una frase
corta y sólo procesa una transcripción si existe actividad de audio.

## Activación y precisión

`WakeWordDetector` es independiente del motor de reconocimiento. Acepta las
formas explícitas `Nix`, `NYX` y `Nicks`, una transcripción habitual; no aplica
coincidencias difusas que aumentarían falsas activaciones. Un futuro detector
acústico dedicado (por ejemplo, un modelo local de wake word) podrá implementar
el mismo límite sin cambiar sesión, interfaz ni cerebro.

## Sesiones e interrupciones

`VoiceService` tiene una única máquina de estados y una única captura de
micrófono. Tras «Nix», mantiene una sesión de 12 segundos configurables, acepta
preguntas consecutivas sin repetir wake word y vuelve a `sleep` al expirar.
Durante síntesis sólo escucha interrupciones («Nix, para», «espera», «cállate»)
y `SpeechService.stop()` detiene la frase actual.

La interfaz se limita a reflejar el estado: el controlador publica `listen`,
`think`, `talk` y `sleep` en `StateStore`; la lógica de voz no depende de
Tkinter.
