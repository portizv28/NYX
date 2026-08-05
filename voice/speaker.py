import pyttsx3


def hablar(texto):

    engine = pyttsx3.init()

    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1)

    engine.say(texto)

    engine.runAndWait()

    engine.stop()
    