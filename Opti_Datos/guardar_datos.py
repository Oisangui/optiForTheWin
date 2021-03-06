import pandas as pd
import os
from gurobipy import GRB


def guardar_variables(variables_dict, subcarpeta):
    print(f"Guardando variables para {subcarpeta}")
    for variable_name, indexes in variables_dict.items():
        vardict = {
            "index": [index for index in indexes.keys()],
            "X": [variable.X for variable in indexes.values()]
        }
        df = pd.DataFrame.from_dict(vardict)
        df.to_csv(os.path.join("output", subcarpeta,
                               "variables", f"{variable_name}.csv"))
    print(f"Guardadas variables para {subcarpeta}")


def guardar_restricciones(restricciones_dict, subcarpeta):
    print(f"Guardando restricciones para {subcarpeta}")
    for constraint_name, indexes in restricciones_dict.items():
        try:
            vardict = {
                "index": [index for index in indexes.keys()],
                "holgura": [
                    constr.getAttr(GRB.Attr.Slack) for constr in indexes.values()]
            }
            df = pd.DataFrame.from_dict(vardict)
            df.to_csv(os.path.join("output", subcarpeta, "restricciones",
                                   f"{constraint_name}.csv"))
        except AttributeError:
            vardict = {
                "index": [1],
                "holgura": [indexes.getAttr(GRB.Attr.Slack)]
            }
            df = pd.DataFrame.from_dict(vardict)
            df.to_csv(os.path.join("output", subcarpeta, "restricciones",
                                   f"{constraint_name}.csv"))
    print(f"Guardadas restricciones para {subcarpeta}!")


def guardar_fo(valor, subcarpeta):
    print(f"Guardando FO para {subcarpeta}")
    with open(os.path.join("output", subcarpeta, "valores",
                           "valor_fo.txt"), 'w') as file:
        print(f"Guardada FO para {subcarpeta}!")
        file.write(str(valor))
