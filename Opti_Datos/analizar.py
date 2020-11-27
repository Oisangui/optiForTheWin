import pandas as pd
# importamos el gurobipy, la API de Gurobi, que en realidad está escrito en C++
from gurobipy import Model
import os

from crear_modelo import cargar_datos, cargar_variables, cargar_restricciones, cargar_funcion_objetivo
from guardar_datos import guardar_variables, guardar_restricciones, guardar_fo
from generar_graficos import generar_graficos


def analizar(subcarpeta: str):
    if not os.path.exists(os.path.join(os.getcwd(), 'output')):
        os.makedirs(os.path.join(os.getcwd(), 'output'))
    if not os.path.exists(os.path.join(os.getcwd(), 'output', subcarpeta)):
        os.makedirs(os.path.join(os.getcwd(), 'output', subcarpeta))
    if not os.path.exists(os.path.join(os.getcwd(), 'output', subcarpeta, 'restricciones')):
        os.makedirs(os.path.join(os.getcwd(), 'output', subcarpeta, 'restricciones'))
    if not os.path.exists(os.path.join(os.getcwd(), 'output', subcarpeta, 'resultados')):
        os.makedirs(os.path.join(os.getcwd(), 'output', subcarpeta, 'resultados'))
    if not os.path.exists(os.path.join(os.getcwd(), 'output', subcarpeta, 'variables')):
        os.makedirs(os.path.join(os.getcwd(), 'output', subcarpeta, 'variables'))
    if not os.path.exists(os.path.join(os.getcwd(), 'output', subcarpeta, 'valores')):
        os.makedirs(os.path.join(os.getcwd(), 'output', subcarpeta, 'valores'))

    # cargamos los parámetros. Estos deben venir de los datos.
    # Usamos pandas
    parametros_dict = cargar_datos(subcarpeta)

    # creamos el modelo
    m = Model()

    # cargamos las variables
    variables_dict = cargar_variables(m, parametros_dict)
    m.update()

    # cargamos las restricciones
    restricciones_dict = cargar_restricciones(
        m, variables_dict, parametros_dict)
    m.update()

    # cargamos la función objetivo
    cargar_funcion_objetivo(m, variables_dict, parametros_dict)
    m.update()

    # optimizamos
    m.optimize()

    guardar_variables(variables_dict, subcarpeta)

    guardar_restricciones(restricciones_dict, subcarpeta)
    
    guardar_fo(m.ObjVal, subcarpeta)

    # tabla de que contenido se libera que semana
    generar_graficos(subcarpeta)
