from analizar import analizar
import pandas as pd
import os
if __name__ == "__main__":
    to_run = [
    #"original",
    #"presupuesto",
    #"presupuesto_0",
    #"tiempo_video",
    #"tiempo_video_2", # no tiene solucion
    #"min_difusion",
    #"min_difusion_5",
    #"min_difusion_10",
    #"personas_cont",
    #"personas_cont_1",
    #"tiempo_disp_5",
    #"tiempo_disp_10",
    #"max_atraso", #no tiene solucion
    #"max_atraso_3", # se demora mucho, lo dejé para después
    #"max_atraso_2", # se demora muuuucho (pero menos que el anterior), también lo dejé para después
    #"a_1",
    #"a_1_0",
    #"a_2",
    #"a_2_0",
    #"a_3",
    #"a_3_0",
    #"a_4",
    #"a_4_0",
    #"a_5",
    #"a_5_0",
    "hE+5",
    "hE+10",
    "hD+5",
    "hD+10",
    "hG+5",
    "hG+10",
    ]
    results = {
        subfolder: analizar(subfolder) for subfolder in to_run
    }
    data = list()
    for subfolder in results:
        m = results[subfolder]
        datum = dict()
        datum['index'] = subfolder
        datum['objVal'] = m.ObjVal
        datum['gap'] = m.MIPGAP
        datum['runtime'] = m.Runtime
        datum['sols'] = m.SolCount
        datum['simplex iters'] = m.IterCount
        vars_ = m.getVars()
        constrs = m.getConstrs()
        active_constrs = sum(map(
            lambda constr: constr.Slack == 0,
            constrs,
        ))
        datum['active constrs'] = active_constrs
        data.append(datum)
    df = pd.DataFrame(data)
    df = df.set_index(df['index']).drop(columns=['index'])
    print(df)
    if not os.path.exists(os.path.join(os.getcwd(), "graficos_comparacion")):
        os.makedirs(os.path.join(os.getcwd(), "graficos_comparacion"))
    for col in df.columns:
        ax = df[[col]].plot(
            kind='barh', 
            title=col,
            figsize=(12, 8),
            sharex=True)
        # ax.set_xticklabels(ax.get_xticklabels(), rotation="horizontal")
        fig = ax.get_figure()
        fig.savefig(os.path.join(os.getcwd(), "graficos_comparacion", f'sensibilidad_{col}.png'))
    print(df)
