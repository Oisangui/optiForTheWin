import pandas as pd
import os
from gurobipy import GRB

def guardar_variables(variables_dict):
    for variable_name, indexes in variables_dict.items():
        vardict = {
            "index": [index for index in indexes.keys()],
            "valor": [variable.X for variable in indexes.values()]
                }
        df = pd.DataFrame.from_dict(vardict)
        df.to_csv(os.path.join("output", "variables", f"{variable_name}.csv"))

def guardar_restricciones(restricciones_dict):
    for constraint_name, indexes in restricciones_dict.items():
        try:
            vardict = {
                "index": [index for index in indexes.keys()],
                "holgura": [constr.getAttr(GRB.Attr.Slack) for constr in indexes.values()]
                }
            df = pd.DataFrame.from_dict(vardict)
            df.to_csv(os.path.join("output", "restricciones", f"{constraint_name}.csv"))
        except AttributeError:
            vardict = {
                "index": [1],
                "holgura": [indexes.getAttr(GRB.Attr.Slack)]
                }
            df = pd.DataFrame.from_dict(vardict)
            df.to_csv(os.path.join("output", "restricciones", f"{constraint_name}.csv"))

