from openpyxl import Workbook


def crear_excel(
    nombre="NYX_excel.xlsx"
):

    archivo = Workbook()

    hoja = archivo.active

    hoja.title = "Datos NYX"


    hoja["A1"] = "Creado por NYX"


    archivo.save(nombre)


    return nombre



def escribir_datos(
    nombre,
    datos
):

    archivo = Workbook()

    hoja = archivo.active


    for fila in datos:

        hoja.append(fila)


    archivo.save(nombre)


    return nombre