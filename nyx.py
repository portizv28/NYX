"""Punto de compatibilidad para la aplicación NYX.

La implementación del controlador vive en ``app.controller`` para que esta
raíz no acumule dependencias de interfaz, voz e inteligencia.
"""

from app.controller import NYX

__all__ = ["NYX"]
