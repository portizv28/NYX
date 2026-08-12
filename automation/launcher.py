import os

def abrir_programa(nombre):

    nombre = nombre.lower()

    programas = {
        "spotify": "start spotify",
        "steam": "start steam",
        "chrome": "start chrome",
        "word": "start winword",
        "excel": "start excel",
        "calculadora": "start calc",
        "explorador": "start explorer",
        "bloc de notas": "start notepad",
        "paint": "start mspaint"
    }

    if nombre in programas:
        os.system(programas[nombre])
        return f"Abriendo {nombre}."

    return "No conozco ese programa."
    
