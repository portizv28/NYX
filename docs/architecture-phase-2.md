# Arquitectura de NYX — Fase 2

## Router híbrido

`HybridRouter` prioriza la IA local para consultas normales. Sólo selecciona
OpenAI cuando una regla explícita detecta una petición extensa o de razonamiento,
programación, análisis o creatividad. Si el proveedor externo falla, NYX usa la
IA local automáticamente y conserva el servicio.

Las reglas están en `RoutingPolicy`, separadas del proveedor y del cerebro. Se
pueden ajustar sin cambiar el flujo de conversación.

## Cerebro

`NyxBrain` sólo establece el orden de decisión:

1. Ejecutar una acción registrada.
2. Resolver una regla determinista breve.
3. Delegar la petición restante al router de IA.

Por tanto, añadir automatización no requiere editar el cerebro.

La elección de automatización de escritorio, JSON y proveedores reales vive en
`app/composition.py`, no en el cerebro. Esto mantiene el núcleo reutilizable en
otros dispositivos e interfaces.

## Registro de acciones

Cada acción declara nombre, descripción, condición de coincidencia y función de
ejecución. Las acciones actuales abren Google, YouTube y los programas ya
conocidos por el lanzador original. El registro captura errores de una acción y
devuelve un mensaje seguro sin detener NYX.

## Identidad y voz

`config.identity.NYX_IDENTITY` centraliza el nombre visual **NYX**, la
pronunciación **Nix** y las palabras de activación `nyx` y `nix`. La síntesis
convierte el nombre visual a «Nix» antes de hablar.
