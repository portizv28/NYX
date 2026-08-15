# Versión 0.8 — Noticias e interfaz

La capacidad de noticias sigue separada de `NyxBrain`. La misma instancia de
`NewsService` se compone para las acciones registradas y el Control Center, de
modo que voz, texto y panel comparten resultados, caché y referencias.

La interfaz incorpora el panel **Noticias** con actualización manual, estado
por fuente y apertura del origen. Los errores de una fuente son `SourceStatus`
y se muestran como aviso; nunca se traducen a “no hay noticias”.

La esfera de la ventana y la esfera flotante comparten `gui/orb_geometry.py`.
Ese módulo no depende de Tk y calcula la esfera interior, hueco y anillo. El
anillo se anima hacia fuera y su borde interior siempre permanece separado de
la esfera al menos por el hueco calculado. Las pruebas cubren todos los estados
y varias fases de animación, además del centrado al redimensionar.
