# Versión 0.7 — Experiencia de usuario e interfaz

## Interfaz

La ventana se organiza ahora alrededor de la esfera: navegación lateral plegable
de 280 píxeles, área central de presencia y conversación compacta. La esfera se
redibuja desde el tamaño real del lienzo al redimensionar, por lo que siempre
queda centrada. El panel lateral no contiene lógica: selecciona secciones que
la vista presenta y conserva espacio para futuras capacidades.

## Prioridad: voz

La captura usa un umbral adaptable al ruido ambiental con un mínimo sensible
para voces suaves. El cierre por silencio se reduce de 1,2 a 0,75 segundos y
Whisper recibe un contexto explícito de la pronunciación «Nix / NYX». Se
reconocen también las transcripciones habituales `Nicks`, `Nick` y `Nik`.

El modelo sigue siendo configurable mediante `NYX_WHISPER_MODEL`; `base` es el
valor inicial por equilibrio entre español y recursos. En un equipo más potente
puede probarse `small` para precisión; en uno limitado, `tiny` reduce latencia
con posible pérdida de precisión. La decisión no obliga a cambiar la
arquitectura de voz.

## Validación real pendiente

Las pruebas automatizadas validan sesiones, detector y sensibilidad. La
fiabilidad física depende del micrófono, ruido y drivers: tras instalar las
dependencias, conviene probar `test_voice.py` en tu entorno y ajustar sólo la
configuración de escucha si fuera necesario.
