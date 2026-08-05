import math



def calcular(
    expresion
):

    permitidos = {
        "sqrt": math.sqrt,
        "pi": math.pi,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan
    }


    resultado = eval(
        expresion,
        {
            "__builtins__": {}
        },
        permitidos
    )


    return resultado