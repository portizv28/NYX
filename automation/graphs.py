import matplotlib.pyplot as plt



def crear_grafica(
    x,
    y,
    titulo="Grafica NYX"
):

    plt.figure()

    plt.plot(
        x,
        y
    )


    plt.title(
        titulo
    )

    plt.grid()


    plt.show()