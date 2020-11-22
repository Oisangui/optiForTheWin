import pandas as pd
import matplotlib.pyplot as plt
import os

def generar_graficos(datos, variables_dict, parametros_dict):
    contenido_semana = {
        "index": list(),
        "value": list()
    }

    for q in datos["Q"]:
        for s in datos["S"]:
            if(variables_dict["u"][(q, s)].X == 1):
                contenido_semana["index"].append(q)
                contenido_semana["value"].append(s)

    df_contenido_semana = pd.DataFrame.from_dict(contenido_semana)

    df_contenido_semana.to_csv(os.path.join("output", "resultados", "contenido_semana.csv"))


    # grafico de tiempo total de videos semanal por depto
    tiempo_total_semanal_depto = {
    }

    for d in datos["D"]:
        for s in datos["S"]:
            tiempo_total_semanal_depto[(d, s)] = (
                sum(variables_dict["tau"][(p, q, s)].X for p in datos["P"] for q in datos["Q"] if datos['dP'][(p, d)] == 1)
            )

    handless = list()
    for d in datos["D"]:
        handle, = plt.plot(datos["S"], [tiempo_total_semanal_depto[(d, s)] for s in datos["S"]], label=d)
        handless.append(handle)
    plt.legend(handles = handless)
    plt.savefig(os.path.join(os.getcwd(), "output", "resultados", "grafico_tiempo_difusion_semanal.png"))
    plt.close()



    # grafico de tiempo total de difusion por semana
    tiempo_difusion = {
        "index": list(),
        "value": list()
    }

    for s in datos["S"]:
        tiempo_difusion["index"].append(s)
        tiempo_difusion["value"].append(sum(variables_dict["tauD"][(p, s)].X for p in datos["P"]))

    plt.plot(tiempo_difusion["index"], tiempo_difusion["value"])
    plt.savefig(os.path.join(os.getcwd(), "output", "resultados", "grafico_tiempo_semanal_depto.png"))
    plt.close()

    # lista de cuando se compra publicidad
    lista_semanas_publicidad = list()

    for s in datos["S"]:
        if variables_dict["betaP"][s].X == 1:
            lista_semanas_publicidad.append(s)
    with open(os.path.join("output", "resultados", "semanas_publicidad.csv"), "w") as file:
        file.write(",".join(str(lista_semanas_publicidad)))


