# Arquitectura de NYX — Fase 5

## Personalidad independiente

El perfil `NYX_PROFILE` es declarativo: concentra rasgos, modos de expresión y
ritmo de voz, sin depender de Ollama, OpenAI, Tkinter ni Windows. La identidad
visual y la pronunciación «Nix» siguen en `config.identity`, que es la única
fuente de verdad del nombre.

## Modos

`InteractionModeSelector` selecciona el modo profesional para finanzas,
estudios, trabajo y análisis; el resto usa el modo cotidiano. Las reglas son
locales, explícitas y configurables. El perfil ordena no usar humor en temas
profesionales; en conversaciones cotidianas permite únicamente un toque sutil.

## Decoradores

`PersonalityAwareProvider` prepara la instrucción de identidad antes de enviar
texto a cualquier proveedor de IA. `PersonalityAwareProcessor` adapta el tono
de respuestas deterministas de acciones, memoria y reglas. Ambos se componen
en `app/composition.py`, por lo que `NyxBrain`, el router y los proveedores no
contienen lógica de personalidad.

La síntesis consulta el `VoiceStyle` del perfil para mantener una cadencia más
calmada. Futuros dispositivos podrán reutilizar el mismo perfil y reemplazar
solamente el adaptador de voz o interfaz.
