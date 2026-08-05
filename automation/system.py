import os
import pyautogui



def apagar():

    os.system(
        "shutdown /s /t 5"
    )



def reiniciar():

    os.system(
        "shutdown /r /t 5"
    )



def captura_pantalla(
    nombre="captura.png"
):

    imagen = pyautogui.screenshot()

    imagen.save(nombre)


    return nombre