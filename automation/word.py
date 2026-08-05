from docx import Document


def crear_documento(
    texto,
    nombre="NYX_documento.docx"
):

    documento = Document()


    documento.add_paragraph(
        texto
    )


    documento.save(nombre)


    return nombre