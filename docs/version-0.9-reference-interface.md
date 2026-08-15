# Versión 0.9 — Interfaz de referencia

La interfaz de escritorio adopta la composición de los bocetos de referencia:
menú lateral, núcleo central de NYX, noticias a la derecha y controles de audio
en la barra inferior. No se movió ninguna decisión de negocio a la vista.

`StateStore` sigue controlando la apariencia: `sleeping` se representa en
blanco; `listening`, `thinking` y `speaking` se representan en azul. La onda
aparece en estados activos. La esfera interior y los dos segmentos verticales
simétricos —izquierdo y derecho, con aberturas arriba y abajo— usan
`orb_geometry.py`, que conserva el hueco al redimensionar.

Los botones **Escuchar** y **Silenciar** son intenciones separadas: el primero
actúa sobre `VoiceService`; el segundo cambia `SpeechService` y detiene solo el
TTS actual. Ninguno altera la lógica de noticias ni el estado de memoria.
