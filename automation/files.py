import os
import shutil



def crear_carpeta(nombre):

    os.makedirs(
        nombre,
        exist_ok=True
    )


    return nombre



def listar_archivos(
    ruta="."
):

    return os.listdir(ruta)



def mover_archivo(
    origen,
    destino
):

    shutil.move(
        origen,
        destino
    )


    return True



def eliminar_archivo(
    archivo
):

    os.remove(
        archivo
    )


    return True