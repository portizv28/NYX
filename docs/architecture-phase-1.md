# Arquitectura de NYX — Fase 1

## Objetivo

Esta fase separa coordinación, interfaz y voz sin cambiar las capacidades
visibles: esfera flotante, texto, activación por «NYX», IA local y síntesis de
voz.

## Flujo actual

`main.py` crea `NYX` desde `app.controller`. El controlador compone la ventana,
la esfera, el cerebro y los servicios de voz. Ninguno de esos módulos importa a
los demás directamente.

1. `VoiceService` escucha y detecta «NYX».
2. El controlador publica el estado `LISTENING` en el hilo de interfaz.
3. `NyxBrain` procesa la orden en segundo plano.
4. El controlador muestra y sintetiza la respuesta; la escucha se pausa para
   no transcribir la propia voz de NYX.

## Estados

`core.state.AssistantState` es la única lista de estados de negocio. Los colores
se definen únicamente en `gui.state_style`, no en el cerebro ni en voz.

## Compatibilidad temporal

Los módulos `voice/wake.py`, `voice/manager.py` y `voice/wake_word.py` no se han
eliminado. Ahora son adaptadores ligeros sobre `VoiceService`; así desaparece la
lógica duplicada sin romper consumidores externos. En una fase posterior se
podrán retirar tras confirmar que nadie los usa.

## Próximos límites

La fase 2 implementará el router de IA, comandos registrables y automatización.
Memoria, visión, simulaciones y posicionamiento inteligente quedan fuera de
esta fase para evitar introducir funcionalidades antes de estabilizar el núcleo.
