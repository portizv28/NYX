# Arquitectura de NYX — Fase 3

## Memoria permanente

`MemoryService` expresa los casos de uso; `MemoryStore` define el contrato de
persistencia. `JsonMemoryStore` es la implementación actual, con formato
versionado y migración automática de la memoria JSON inicial. Una futura
implementación SQLite sólo tendrá que cumplir el mismo contrato.

La memoria almacena clave, valor, categoría, origen y fechas. Hoy interpreta
órdenes sencillas como «Recuerda que mi coche es un Kia»; más adelante podrá
recibir extracción semántica, preferencias y conocimiento estructurado sin
cambiar el cerebro.

## Contexto conversacional

`ConversationHistory` mantiene un historial acotado en memoria durante la
sesión. Antes de pedir IA, forma un prompt con los últimos mensajes; así una
pregunta de seguimiento conserva el tema anterior. No se persiste todavía:
memoria a largo plazo y conversación temporal tienen finalidades distintas y
no deben mezclarse.

## Capacidades

Una capacidad implementa `Capability` y registra sus acciones en un
`ActionRegistry`. La automatización de escritorio es la primera capacidad.
Internet, visión, documentos, finanzas, simulaciones y movimiento podrán ser
paquetes independientes que implementen el mismo contrato.

## Núcleo portable

`app/composition.py` elige las implementaciones de escritorio actuales:
proveedores de IA, memoria JSON y automatización local. `NyxBrain` no conoce
Tkinter, Windows, JSON ni proveedores concretos, por lo que puede reutilizarse
en un altavoz, móvil, servidor o interfaz futura.
