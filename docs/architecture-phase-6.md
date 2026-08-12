# Arquitectura de NYX — Presencia de escritorio

## StateStore

`core.store.StateStore` es la única fuente de verdad del estado operativo.
Publica instantáneas inmutables con estado visual, actividad, micrófono, modelo,
memoria, capacidades y última acción. Las vistas se suscriben, pero ninguna
puede decidir o mutar su lógica interna.

El router publica la decisión del proveedor y el cerebro publica únicamente el
nombre de una acción ejecutada; ambos eventos se conectan al estado desde la
composición de escritorio. Así siguen siendo reutilizables fuera de Windows.

## Esfera y Control Center

La esfera recibe `AssistantState` y ofrece operaciones de visibilidad y
posición (`set_position`, `position`, `move_to`). No sabe nada de micrófono,
IA o automatizaciones. El Control Center comienza con secciones de
conversaciones, memoria, capacidades, automatizaciones, archivos,
configuración y sistema; el panel Sistema representa directamente la
instantánea central.

## Bandeja e inicio

`integrations.windows.tray` es un adaptador opcional basado en `pystray`. Ofrece
abrir el centro, alternar escucha, consultar estado, abrir configuración y
cerrar NYX. Si la dependencia no está instalada, NYX continúa funcionando sin
bandeja.

El arranque automático ya usa una orden absoluta y la memoria de escritorio se
resuelve desde la raíz del proyecto, no desde el directorio de trabajo de
Windows. Por eso el inicio por registro puede mostrar sólo la esfera en estado
`sleep`, sin ventana principal ni consola cuando se usa `pythonw.exe`.
