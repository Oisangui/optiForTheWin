import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import math
from crear_modelo import cargar_datos


def load_data(subcarpeta) -> tuple:
    dirs = os.listdir(os.path.join('output', subcarpeta, 'variables'))
    variables_dict = dict(zip(map(get_name, dirs), map(lambda x: load_file(subcarpeta, x), dirs)))
    return variables_dict, cargar_datos(subcarpeta)

def detuplize(tuplax):
    if isinstance(tuplax, str):
        return str(tuple(
            json.loads(
            f"{{\"tupla_mala\": {tuplax.replace('(', '[').replace(')', ']')}}}"
        )['tupla_mala']
        ))
    return tuplax

def get_name(filename):
    return filename.split('.')[0]


def load_file(subcarpeta, filename):
    df = pd.read_csv(os.path.join('output', subcarpeta, 'variables', filename))
    df.loc[:, 'index'] = pd.Series(df.loc[:, 'index']).apply(detuplize)
    df = df.set_index(df.loc[:, 'index'])
    return df


def generar_graficos(subcarpeta):
    datos, variables_dict = load_data(subcarpeta)[::-1]
    vars_ = (datos, variables_dict)
    df_contenido_semana = get_contenido_semana_departamento_dict(*vars_)
    df_contenido_semana.to_csv(
        os.path.join("output", subcarpeta, "resultados", "contenido_semana.csv")
    )
    graph_tiempo_semana(*vars_, subcarpeta)
    graph_difusion_semana(*vars_, subcarpeta)
    graph_contenido_semana(df_contenido_semana, subcarpeta)
    graph_contenido_semana_depto(df_contenido_semana, subcarpeta)
    
    df_atraso_contenido = get_atraso_contenido_semana_depto_dict(datos, variables_dict)
    graph_atraso_contenido(df_atraso_contenido, subcarpeta)
    graph_atraso_contenido_depto(df_atraso_contenido, subcarpeta)
    
    #publi_lista(datos, variables_dict, subcarpeta)
    
    print(datos["S"])
    
    
def get_contenido_semana_dict(
        datos: dict, variables_dict: dict) -> pd.DataFrame:
    contenido_semana = list()
    print(variables_dict['u'])
    print(type(variables_dict['u'].index[0]))
    for q in datos["Q"]:
        for s in datos["S"]:
            if(variables_dict["u"].loc[str((q, s))].X == 1):
                contenido_semana.append({
                    'contenido': q,
                    'semana': s,
                })
    return pd.DataFrame(contenido_semana)


def get_contenido_semana_departamento_dict(
        datos: dict, variables_dict: dict) -> pd.DataFrame:
    contenido_semana = list()
    print(variables_dict['u'])
    print(type(variables_dict['u'].index[0]))
    for q in datos["Q"]:
        for s in datos["S"]:
            if(variables_dict["u"].loc[str((q, s))].X == 1):
                for d in datos["D"]:
                    if datos["dQ"][q, d] == 1:
                        contenido_semana.append({
                            'contenido': q,
                            'semana': s,
                            'departamento': d
                        })
    return pd.DataFrame(contenido_semana)
    
def get_atraso_contenido_semana_dict(
        datos: dict, variables_dict: dict) -> pd.DataFrame:
    contenido_semana = list()
    print(variables_dict['u'])
    print(type(variables_dict['u'].index[0]))
    print("atraso")
    print(variables_dict["r"].index[1])
    for q in datos["Q"]:
        contenido_semana.append({
            'contenido': q,
            'atraso': round(variables_dict["r"].loc[q].X)
        })
    return pd.DataFrame(contenido_semana)
    
def get_atraso_contenido_semana_depto_dict(
        datos: dict, variables_dict: dict) -> pd.DataFrame:
    contenido_semana = list()
    print(variables_dict['u'])
    print(type(variables_dict['u'].index[0]))
    print("atraso")
    print(variables_dict["r"].index[1])
    for q in datos["Q"]:
        for d in datos["D"]:
            if datos["dQ"][(q, d)] == 1:
                contenido_semana.append({
                    'contenido': q,
                    'atraso': round(variables_dict["r"].loc[q].X),
                    'depto': d
                })
    return pd.DataFrame(contenido_semana)
    
    


def graph_contenido_semana(df_contenido_semana: pd.DataFrame, subcarpeta):
    # grafico de cuantos contenidos se ven por semana
    df = df_contenido_semana.groupby('semana').count().reset_index()
    print(df)
    plot = df.reindex().plot.bar(x='semana', y='contenido', title="Numero de contenidos publicados por semana")
    plot.set_xlabel("Semana")
    plot.set_ylabel("Número de contenidos publicados")
    fig = plot.get_figure()
    fig.savefig(
        os.path.join(os.getcwd(), "output", subcarpeta, "resultados",
                 "grafico_contenido_semana.png")
    )
    plt.close()
    
def graph_atraso_contenido(df_atraso_contenido: pd.DataFrame, subcarpeta):
    # grafico de cuantos contenidos se ven por semana
    df = df_atraso_contenido.groupby('atraso').count().reset_index()
    print(df)
    plot = df.reindex().plot.bar(x="atraso", y="contenido", title="Frecuencia de días de atraso")
    plot.set_xlabel("Días de atraso")
    plot.set_ylabel("Frecuencia")
    fig = plot.get_figure()
    fig.savefig(
        os.path.join(os.getcwd(), "output", subcarpeta, "resultados",
                 "grafico_atraso_contenido.png")
    )
    plt.close()
    
    
def graph_atraso_contenido_depto(df_contenido_semana: pd.DataFrame, subcarpeta):
    # grafico de cuantos contenidos se ven por semana
    plot = df_contenido_semana.groupby(['atraso', 'depto']).count().unstack('depto').plot.bar(y="contenido", title="Frecuencia de atraso de contenidos por departamento")       
    plot.set_xlabel("Días de atraso")
    plot.set_ylabel("Fecuencia")
    fig = plot.get_figure()
    fig.savefig(
        os.path.join(os.getcwd(), "output", subcarpeta, "resultados",
                 "grafico_atraso_contenido_depto.png")
    )
    plt.close()

    
def graph_contenido_semana_depto(df_contenido_semana: pd.DataFrame, subcarpeta):
    # grafico de cuantos contenidos se ven por semana
    plot = df_contenido_semana.groupby(['semana', 'departamento']).count().unstack('departamento').plot.bar(y="contenido", title="Número de contenidos publicados por semana por departamento")       
    plot.set_xlabel("Semana")
    plot.set_ylabel("Número de contenidos publicados")
    fig = plot.get_figure()
    fig.savefig(
        os.path.join(os.getcwd(), "output", subcarpeta, "resultados",
                 "grafico_contenido_semana_depto.png")
    )
    plt.close()


def graph_tiempo_semana(datos, variables_dict, subcarpeta):
    # grafico de tiempo total de videos semanal por depto
    tiempo_total_semanal_depto = {
    }
    print(variables_dict['tau'])
    for d in datos["D"]:
        for s in datos["S"]:
            tiempo_total_semanal_depto[(d, s)] = (
                sum(variables_dict["tau"].loc[str((p, q, s))].X for p in datos["P"]
                    for q in datos["Q"] if datos['dP'][(p, d)] == 1)
            )

    handless = list()
    for d in datos["D"]:
        handle, = plt.plot(
            datos["S"], [tiempo_total_semanal_depto[(d, s)] for s in datos["S"]], label=d)
        handless.append(handle)
    plt.legend(handles=handless)
    plt.title("Tiempo semanal dedicado por departamento")
    plt.xlabel("Semana")
    plt.ylabel("Tiempo")
    plt.savefig(os.path.join(os.getcwd(), "output", subcarpeta, "resultados",
                             "grafico_tiempo_semanal_depto.png"))
    plt.close()


def graph_difusion_semana(datos, variables_dict, subcarpeta):
    # grafico de tiempo total de difusion por semana
    tiempo_difusion = {
        "index": list(),
        "value": list()
    }

    for s in datos["S"]:
        tiempo_difusion["index"].append(s)
        tiempo_difusion["value"].append(
            sum(variables_dict["tauD"].loc[str((p, s))].X for p in datos["P"]))

    plt.plot(tiempo_difusion["index"], tiempo_difusion["value"])
    plt.title("Tiempo total de difusión semanal")
    plt.xlabel("Semana")
    plt.ylabel("Tiempo")
    plt.savefig(os.path.join(os.getcwd(), "output", subcarpeta, "resultados",
                             "grafico_tiempo_difusion_semanal.png"))
    plt.close()


def publi_lista(datos, variables_dict, subcarpeta):
    # lista de cuando se compra publicidad
    lista_semanas_publicidad = list()
    for s in datos["S"]:
        if variables_dict["betaP"][s].X == 1:
            lista_semanas_publicidad.append(s)
    with open(os.path.join("output", "resultados", subcarpeta, "semanas_publicidad.csv"), "w") as file:
        file.write(",".join(map(str, lista_semanas_publicidad)))

if __name__ == '__main__':
    generar_graficos("original")
    generar_graficos("presupuesto")
    generar_graficos("presupuesto_0")
    generar_graficos("tiempo_minimo_video")
    # generar_graficos("tiempo_minimo_video_2") # no tiene solucion
    generar_graficos("min_difusion_publicidad")
    generar_graficos("min_difusion_publicidad_5")
    generar_graficos("min_difusion_publicidad_10")
    generar_graficos("cantidad_personas_contenido")
    generar_graficos("cantidad_personas_contenido_1")
    generar_graficos("tiempo_max_persona_mas_5")
    generar_graficos("tiempo_max_persona_mas_10")
    # generar_graficos("max_semanas_atraso") # no tiene solucion
    # generar_graficos("max_semanas_atraso_3") # se demora mucho, lo dejé para después
    # generar_graficos("max_semanas_atraso_2") # se demora muuuucho (pero menos que el anterior), también lo dejé para después
