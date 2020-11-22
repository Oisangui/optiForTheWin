import pandas as pd
# importamos el gurobipy, la API de Gurobi, que en realidad está escrito en C++
from gurobipy import  GRB, Model, quicksum
import os
import pandas as pd
import matplotlib.pyplot as plt

if not os.path.exists(os.path.join(os.getcwd(), 'output')):
    os.makedirs(os.path.join(os.getcwd(), 'output'))
if not os.path.exists(os.path.join(os.getcwd(), 'output', 'restricciones')):
    os.makedirs(os.path.join(os.getcwd(), 'output', 'restricciones'))
if not os.path.exists(os.path.join(os.getcwd(), 'output', 'resultados')):
    os.makedirs(os.path.join(os.getcwd(), 'output', 'resultados'))
if not os.path.exists(os.path.join(os.getcwd(), 'output', 'variables')):
    os.makedirs(os.path.join(os.getcwd(), 'output', 'variables'))
    

RUTA_ARCHIVO_PERSONAL = os.path.join(os.getcwd(), "encuesta_personal.csv")
RUTA_ARCHIVO_ENCARGADOS = os.path.join(os.getcwd(), "encuesta_encargados.csv")
RUTA_OTROS_DATOS = os.path.join(os.getcwd(), "otros_datos.csv")
RUTA_ARCHIVO_CONTENIDOS = os.path.join(os.getcwd(), "contenidos.csv")

class Clase2:
  def cargar_datos():
    datos = dict(
        a = dict(),
        q = dict(), # { (q, s): 1/0 }
        dP = dict(),
        dQ = dict(),
        t = dict(),
        M = 10000,
        Z = 10000000000000000000000000000,
        KR = 10, # maximos dias de atraso
        hE = dict(),
        hG = dict(),
        hD = dict(),
        E = 1,
        KE = 1,
        LP = 1000,
        UP = 10, # cota superior gente trabajando en el mismo contenido
        LD = 10, # cota inferior de tiempo gastado si se compra publicidad
        q_minus = dict(), #semana en que el contenido debería ser publicado
    )

    personal = pd.read_csv(RUTA_ARCHIVO_PERSONAL)
    encargados = pd.read_csv(RUTA_ARCHIVO_ENCARGADOS)
    otros_datos = pd.read_csv(RUTA_OTROS_DATOS)
    contenidos = pd.read_csv(RUTA_ARCHIVO_CONTENIDOS)

    # numeros de cosas
    n_q = contenidos.shape[0]
    n_p = personal.shape[0]

    # Conjuntos
    Q = list(range(n_q))
    P = list(range(n_p))
    D = personal["departamento"].unique()
    S = contenidos["s"].unique() # asumiendo que todas las semanas se libera un contenido

    datos['Q'] = Q
    datos['P'] = P
    datos['D'] = D
    datos['S'] = S

    # Cargamos los a
    datos['a'][1] = personal.mean()['a_entretenimiento']
    datos['a'][2] = personal.mean()['a_publicidad']
    datos['a'][3] = personal.mean()['a_difusion']
    datos['a'][4] = personal.mean()['a_atraso']
    datos['a'][5] = personal.mean()['a_explicacion']

    # Cargamos q_minus, dQ y q_qs
    for q, row in contenidos.iterrows():
      datos['q_minus'][q] = row["s"]
      for s in S:
        datos['q'][(q, s)] = 1 if row["s"] == s else 0
      for d in D:
        datos['dQ'][(q, d)] = 1 if row["d"] == d else 0

    # Cargamos los dP (pertenencia a deptos)
    for p, row in personal.iterrows():
      for d in D:
        datos['dP'][(p, d)] = 1 if d == row['departamento'] else 0

    # Cargamos los t (tiempos disponibles semanales en horas)
    for p, row in personal.iterrows():
      for s in S:
        datos['t'][(p, s)] = row['tiempo']

    # Cargamos el M (presupuesto total disponible)
    datos['M'] = otros_datos['presupuesto'][0]

    # Cargamos el KR
    datos['KR'] = otros_datos['max_dias_atraso']

    # Cargamos el hE
    for p, row in personal.iterrows():
      datos['hE'][p] = row['h_entretenimiento']

    # Cargamos el hG
    for p, row in personal.iterrows():
      datos['hG'][p] = row['h_explicacion']

    # Cargamos el hD
    for p, row in personal.iterrows():
      datos['hD'][p] = row.fillna(0)['h_difusion']

    # Cargamos el KE
    datos['KE'] = encargados.mean()['entretenimiento_difusion'] / 10

    # Cargamos el LP (dinero a gastar si se elige gastar en publicidad)
    datos['LP'] = otros_datos['dinero_publicidad'][0]

    # Cargamos el UP (máximo de personas trabajando en un video)
    datos['UP'] = encargados.mean()['max_personas_video']

    # Cargamos el LD (horas minimas dedicadas a difusion)
    datos['LD'] = encargados.mean()['horas_difusion']

    datos['E'] = otros_datos['min_horas_video']

    return datos

cargar_datos = Clase2.cargar_datos

# carga de variables
def cargar_variables(modelo, datos):
  vars = dict(
      u = dict(),
      tau = dict(),
      tauD = dict(),
      betaP = dict(),
      delta = dict(),
      m = dict(),
      u_ = dict(),
      r = dict(),
      gE_pqs = dict(),
      gE_s = dict(),
      gP = dict(),
  )
  # delta
  for p in datos['P']:
    for q in datos['Q']:
      for s in datos['S']:
        vars['delta'][(p, q, s)] = modelo.addVar(vtype='B', name= 'delta_{},{},{}'.format(p, q, s))
  # m
  for s in datos['S']:
    vars['m'][s] = modelo.addVar(vtype='I', name= 'm_{}'.format(s))
  # u_
  for q in datos['Q']:
    for s in datos['S']:
      vars['u_'][(q, s)] = modelo.addVar(vtype='B', name= 'u_{},{}'.format(q, s))
  # r
  for q in datos['Q']: # esto es semanas de atraso
    vars['r'][q] = modelo.addVar(vtype='I', name= 'r_{}'.format(q))
  # gE_pqs
  for p in datos['P']:
    for q in datos['Q']:
      for s in datos['S']:
        vars['gE_pqs'][(p, q, s)] = modelo.addVar(vtype='I', name= 'gE_pqs_{},{},{}'.format(p, q, s))
  # gE_s
  for s in datos['S']:
    vars['gE_s'][s] = modelo.addVar(vtype='I', name= 'gE_s_{}'.format(s))
  # gP
  for s in datos['S']:
    vars['gP'][s] = modelo.addVar(vtype='I', name= 'gP_{}'.format(s))

  # u_qs
  for q in datos['Q']:
    for s in datos['S']:
      vars['u'][(q, s)] = modelo.addVar(vtype='B', name= 'u_{},{}'.format(q, s))

  # tau_pqs
  for p in datos['P']:
    for q in datos['Q']:
      for s in datos['S']:
        vars['tau'][(p, q, s)] = modelo.addVar(vtype='I', name= 'tau_{},{},{}'.format(p, q, s))

  # tauD_ps
  for p in datos['P']:
    for s in datos['S']:
      vars['tauD'][(p, s)] = modelo.addVar(vtype='I', name= 'tauD_{},{}'.format(p, s))

  # betaP_s
  for s in datos['S']:
    vars['betaP'][s] = modelo.addVar(vtype='B', name= 'betaP_{}'.format(s))
  return vars


# carga de restricciones
def cargar_restricciones(modelo, variables, datos):
  res = dict(
      nat_tau=dict(),
      nat_g_pqs=dict(),
      nat_gE_s=dict(),
      nat_m=dict(),
      nat_r=dict(),
      nat_tauD=dict(),
      nat_gP=dict(),
      r1=dict(),
      r2=dict(),
      r3=dict(),
      r4=dict(),
      r5=dict(),
      r6=dict(),
      r7a=dict(),
      r7b=dict(),
      r8=dict(),
      r9a=dict(),
      r9b=dict(),
      r9c=dict(),
      r10=dict(),
      r11a=dict(),
      r11b=dict(),
      r11c=dict(),
      r12=dict(),
      r13=dict(),
      r14=dict(),
      r150=None,
      r15=dict(),
      r16=dict(),
  )

  # 1
  for q in datos['Q']:
    for s in datos['S']:
      s_primes = list(filter(lambda s_p: s_p <= s, datos['S']))
      res['r1'][(q, s)] = modelo.addConstr(
          variables['u_'][(q, s)] == 1 - sum([variables['u']
                           [(q, s_prime)] for s_prime in s_primes])
          )
  # 2
  for q in datos['Q']:
    res['r2'][q] = modelo.addConstr(
        variables['r'][q] == sum([variables['u_'][(q, s)] for s in datos['S']]) + 1 - datos['q_minus'][q]
    )

  # 3
  for q in datos['Q']:
    res['r3'][q] = modelo.addConstr(variables['r'][q] <= datos['KR'])

  # 4
  for q in datos['Q']:
    for d in datos['D']:
      res['r4'][(q, d)] = modelo.addConstr(
          sum(variables['tau'][(p, q, s)] for s in datos['S'] for p in datos['P']) >= datos['E'] * datos['dQ'][(q, d)]
      )
  # 5
  for q in datos['Q']:
    for s in datos['S']:
      res['r5'][(q, s)] = modelo.addConstr(
          sum([variables['delta'][(p, q, s)] for p in datos['P']]) <= datos['Z'] * variables['u_'][(q, s)]
              )
  # 6
  for p in datos['P']:
    for s in datos['S']:
      res['r6'][(p, s)] = modelo.addConstr(
          sum(variables['tau'][(p, q, s)] for q in datos['Q']) +
              variables['tauD'][(p, s)] <= datos['t'][(p, s)]
      )
  # 7
  for q in datos['Q']:
    for s in datos['S']:
      for p in datos['P']:
        res['r7a'][(p, q, s)] = modelo.addConstr(
            variables['delta'][(p, q, s)] *
                                datos['Z'] >= variables['tau'][(p, q, s)]
        )
        res['r7b'][(p, q, s)] = modelo.addConstr(
            variables['delta'][(p, q, s)] <= variables['tau'][(p, q, s)]
        )
  # 8
  for q in datos['Q']:
    for s in datos['S']:
      res['r8'][(q, s)] = modelo.addConstr(
          sum(variables['delta'][(p, q, s)] for p in datos['P']) <= datos['UP']
      )
  # 9
  for q in datos['Q']:
    for s in datos['S']:
      for p in datos['P']:
        res['r9a'][(p, q, s)] = modelo.addConstr(
            variables['gE_pqs'][(p, q, s)] >= sum(variables['tau'][(p, q, s_prime)]
                                 for s_prime in datos['S']) * datos['hE'][p] - datos['Z'] * (1 - variables['u'][(q, s)])
        )
        res['r9b'][(p, q, s)] = modelo.addConstr(
            variables['gE_pqs'][(p, q, s)] <= datos['Z'] *
                                 variables['u'][(q, s)]
        )
        res['r9c'][(p, q, s)] = modelo.addConstr(
            variables['gE_pqs'][(p, q, s)] <= sum(
                variables['tau'][(p, q, s_prime)] for s_prime in datos['S']) * datos['hE'][p]
        )
  # 10
  for s in datos['S']:
    res['r10'][s] = modelo.addConstr(
        variables['gE_s'][s] == sum(variables['gE_pqs'][(p, q, s)]
                                    for p in datos['P'] for q in datos['Q'])
    )
  # 11
  for s in datos['S']:
    res['r11a'][s] = modelo.addConstr(
        variables['gP'][s] <= datos['Z'] * variables['betaP'][s]
    )
    res['r11b'][s] = modelo.addConstr(
        variables['gP'][s] <= variables['gE_s'][s] * datos['KE']
    )
    res['r11c'][s] = modelo.addConstr(
        variables['gP'][s] >= variables['gE_s'][s] *
            datos['KE'] - datos['Z'] * (1 - variables['betaP'][s])
    )
  # 12
  for s in datos['S']:
    res['r12'][s] = modelo.addConstr(
        sum(variables['tauD'][(p, s)]
            for p in datos['P']) >= variables['betaP'][s] * datos['LD']
    )
  # 13
  for q in datos['Q']:
    res['r13'][q] = modelo.addConstr(
        sum(variables['u'][(q, s)] for s in datos['S']) <= 1
    )
  # 14
  for q in datos['Q']:
    res['r14'][q] = modelo.addConstr(
        variables['r'][q] >= 0
    )
  # 15
  res['r150'] = modelo.addConstr(variables['m'][1] == datos['M'])
  for s in datos['S'][:-1]:
    res['r15'][s] = modelo.addConstr(
        variables['m'][s + 1] == variables['m'][s] - datos['LP'] * variables['betaP'][s]
    )
  # 16
  for q in datos['Q']:
    for s in datos['S']:
      for p in datos['P']:
        d=get_d_constr(q, datos)
        res['r16'][(p, q, s)]=modelo.addConstr(variables['tau'][(p, q, s)] <= datos['Z'] * datos['dP'][(p, d)])

  # 17 NATURALEZA DE LAS VARIABLES
  for s in datos['S']:
    for p in datos['P']:
      for q in datos['Q']:
        res['nat_tau'][(p, q, s)] = modelo.addConstr(variables['tau'][(p, q, s)] >= 0)
        res['nat_g_pqs'][(p, q, s)] = modelo.addConstr(variables['gE_pqs'][(p, q, s)] >= 0)
      res['nat_tauD'][(p, s)] = modelo.addConstr(variables['tauD'][(p, s)] >= 0)
    res['nat_m'][s] = modelo.addConstr(variables['m'][s] >= 0)
    res['nat_gP'][s] = modelo.addConstr(variables['gP'][s] >= 0)
    res['nat_gE_s'][s] = modelo.addConstr(variables['gE_s'][s] >= 0)

  for q in datos['Q']:
    res['nat_r'][q] = modelo.addConstr(variables['r'][q] >= 0)

  return res


def get_d_constr(q, datos):
  for d in datos['D']:
    if datos['dQ'][(q, d)] == 1:
      return d
  raise Exception('bad programming....')

def cargar_funcion_objetivo(m, variables, datos):
  m.setObjective(sum((datos['a'][1] * variables['gE_s'][s] + datos['a'][2] * variables['gP'][s] + sum((datos['a'][3] * variables['tauD'][(p, s)] * datos['hD'][p]) for p in datos['P'])) for s in datos['S']) - sum(datos['a'][4] * variables['r'][q] for q in datos['Q']) + sum(datos['a'][5] * variables['tau'][(p, q, s)] * datos['hG'][p] for s in datos['S'] for p in datos['P'] for q in datos['Q']), GRB.MAXIMIZE)

  # cargamos los parámetros. Estos deben venir de los datos.
# Usamos pandas
parametros_dict = cargar_datos()


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

for variable_name, indexes in variables_dict.items():
    vardict = {
        "index": [index for index in indexes.keys()],
        "valor": [variable.X for variable in indexes.values()]
            }
    df = pd.DataFrame.from_dict(vardict)
    df.to_csv(os.path.join("output", "variables", f"{variable_name}.csv"))


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


#me parece que hay que hacer
#* una tabla de "contenido se publica esta semana"
#* un grafico de tiempo total de videos semanal por departamento
#* un grafico de tiempo total de difusion semanal
#* una lista de cuando se compra publicidad 

#tabla de que contenido se libera que semana
def generar_graficos(datos, parametros_dict):
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

generar_graficos(parametros_dict, parametros_dict)

