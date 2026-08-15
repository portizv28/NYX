# NYX

Asistente personal local con interfaz de esfera flotante, entrada de texto y
activación por voz. El proyecto se está refactorizando de forma incremental
para convertir el prototipo inicial en una plataforma modular.

## Ejecutar

1. En Windows, ejecuta `./scripts/setup.ps1 -Profile Full -Dev`.
2. Revisa el archivo `.env` creado desde `.env.example`; no lo incluyas en Git.
3. Inicia NYX con `.venv\Scripts\python.exe main.py`.

NYX usa Ollama local para la conversación actual. Debe estar disponible en
`http://localhost:11434` y tener instalado `llama3.2:3b`.

## Inicio automático en Windows

La integración no se activa sola. Tras instalar las dependencias, consulta su
estado con `python -m integrations.windows.cli status`, actívala con
`python -m integrations.windows.cli enable` y desactívala con
`python -m integrations.windows.cli disable`. Usa la clave de inicio del usuario
de Windows, no un acceso directo, y conserva `python main.py` para el arranque
manual.

## Arquitectura

La documentación de arquitectura está en
[`docs/architecture-phase-1.md`](docs/architecture-phase-1.md),
[`docs/architecture-phase-2.md`](docs/architecture-phase-2.md) y
[`docs/architecture-phase-3.md`](docs/architecture-phase-3.md),
[`docs/architecture-phase-4.md`](docs/architecture-phase-4.md) y
[`docs/architecture-phase-5.md`](docs/architecture-phase-5.md),
[`docs/architecture-phase-6.md`](docs/architecture-phase-6.md) y
[`docs/architecture-phase-7.md`](docs/architecture-phase-7.md),
[`docs/version-0.7-ux.md`](docs/version-0.7-ux.md) y
[`docs/version-0.7.1-voice-stability.md`](docs/version-0.7.1-voice-stability.md),
[`docs/voice-production-pipeline.md`](docs/voice-production-pipeline.md). El controlador
vive en `app/controller.py`; los estados se comparten desde `core/state.py`.

La guía de migración, voz, TTS y noticias está en
[`docs/new-pc-preparation.md`](docs/new-pc-preparation.md).
