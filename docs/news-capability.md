# Capacidad de noticias

La capacidad vive en `news/` y se registra desde `capabilities/defaults.py`.
`NyxBrain` no contiene reglas de fuentes, RSS ni referencias de noticias.

## Flujo

1. `NewsSourceRepository` lee exclusivamente las fuentes permitidas en
   `config/news_sources.json`.
2. `RssNewsProvider` consulta RSS/Atom con timeout y validación TLS.
3. `WebNewsProvider` es el último recurso para Forbes mientras no mantiene un
   RSS operativo: consume únicamente JSON-LD público de su página configurada.
4. `NewsService` conserva estado por fuente, caché JSON local, deduplicación y
   filtros temporales en zona Europe/Madrid.
5. `NewsCapability` responde a la conversación y resuelve referencias como
   “la segunda” a partir de los identificadores de la última consulta.
6. `NyxWindow` solo representa `NewsQueryResult`; emite eventos de actualizar y
   abrir origen al controlador.

Una fuente que falla genera `SourceStatus(ok=False, error=...)`. Esto nunca se
convierte en “no hay noticias”. El panel muestra ✓ o ⚠ y las respuestas indican
que hubo fuentes no consultables.

La caché se guarda en `.nyx/news_cache.json`, que está excluida de Git. El
contrato `JsonNewsCache` permite sustituirla posteriormente por SQLite.
