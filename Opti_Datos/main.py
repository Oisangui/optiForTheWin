import pandas as pd
# importamos el gurobipy, la API de Gurobi, que en realidad está escrito en C++
from gurobipy import  GRB, Model, quicksum
import os
import pandas as pd
import matplotlib.pyplot as plt

from crear_modelo import cargar_datos, cargar_variables, cargar_restricciones, cargar_funcion_objetivo
from guardar_datos import guardar_variables, guardar_restricciones
from generar_graficos import generar_graficos


if not os.path.exists(os.path.join(os.getcwd(), 'output')):
    os.makedirs(os.path.join(os.getcwd(), 'output'))
if not os.path.exists(os.path.join(os.getcwd(), 'output', 'restricciones')):
    os.makedirs(os.path.join(os.getcwd(), 'output', 'restricciones'))
if not os.path.exists(os.path.join(os.getcwd(), 'output', 'resultados')):
    os.makedirs(os.path.join(os.getcwd(), 'output', 'resultados'))
if not os.path.exists(os.path.join(os.getcwd(), 'output', 'variables')):
    os.makedirs(os.path.join(os.getcwd(), 'output', 'variables'))

RUTA_ARCHIVO_PERSONAL = os.path.join(os.getcwd(), "input", "encuesta_personal.csv")
RUTA_ARCHIVO_ENCARGADOS = os.path.join(os.getcwd(), "input", "encuesta_encargados.csv")
RUTA_OTROS_DATOS = os.path.join(os.getcwd(), "input", "otros_datos.csv")
RUTA_ARCHIVO_CONTENIDOS = os.path.join(os.getcwd(), "input", "contenidos.csv")

personal = pd.read_csv(RUTA_ARCHIVO_PERSONAL)
encargados = pd.read_csv(RUTA_ARCHIVO_ENCARGADOS)
otros_datos = pd.read_csv(RUTA_OTROS_DATOS)
contenidos = pd.read_csv(RUTA_ARCHIVO_CONTENIDOS)

# cargamos los parámetros. Estos deben venir de los datos.
# Usamos pandas
parametros_dict = cargar_datos(personal, encargados, otros_datos, contenidos)

if __name__ == '__main__':
    # creamos el modelo
    m = Model()

    # cargamos las variables
    variables_dict = cargar_variables(m, parametros_dict)
    m.update()


    # cargamos las restricciones
    restricciones_dict = cargar_restricciones(m, variables_dict, parametros_dict)
    m.update()

    # cargamos la función objetivo
    cargar_funcion_objetivo(m, variables_dict, parametros_dict)
    m.update()

    # optimizamos
    m.optimize()

    guardar_variables(variables_dict)

    guardar_restricciones(restricciones_dict)

    #tabla de que contenido se libera que semana
    generar_graficos()

