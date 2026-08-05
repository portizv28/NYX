import webbrowser
import urllib.parse


def abrir_google(busqueda=None):

    if busqueda:

        texto = urllib.parse.quote(busqueda)

        url = (
            "https://www.google.com/search?q="
            + texto
        )

    else:

        url = "https://www.google.com"


    webbrowser.open(url)



def abrir_youtube():

    webbrowser.open(
        "https://www.youtube.com"
    )



def abrir_web(url):

    webbrowser.open(url)
    