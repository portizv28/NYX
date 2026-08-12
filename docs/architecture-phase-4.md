# Arquitectura de NYX — Fase 4

## Internet

La capacidad `InternetCapability` se compone de un proveedor de búsqueda y un
lector de páginas. La versión inicial abre consultas en el navegador del
usuario, sin API ni credenciales. `SearchProvider` y `PageReader` permiten
sustituirlo por proveedores estructurados, documentación especializada o
lectores con extracción avanzada sin modificar el cerebro.

## Automatización y documentos

Las operaciones de carpetas se registran como capacidad independiente y sólo
incluyen acciones no destructivas: crear, listar y abrir. Borrar o mover
archivos no se exponen aún porque necesitan una política explícita de
confirmación y rutas seguras.

`DocumentsCapability` ofrece los primeros adaptadores Word y Excel. Los
módulos heredados de `automation/word.py` y `automation/excel.py` son ahora
compatibles con esas implementaciones, sin duplicar su lógica. PDF y análisis
documental podrán añadir adaptadores del mismo estilo.

## Inicio de Windows

`WindowsRunKeyStartupManager` implementa el contrato portable de inicio
automático y registra NYX únicamente bajo la cuenta actual del usuario. No se
activa por defecto: usar `python -m integrations.windows.cli enable` después
de instalar las dependencias. El arranque manual sigue siendo `python main.py`.

Al empaquetar NYX, `StartupCommand` detectará el ejecutable instalado; durante
desarrollo emplea el intérprete `pythonw.exe` y el `main.py` absoluto para no
mostrar una consola ni depender del directorio de trabajo.
