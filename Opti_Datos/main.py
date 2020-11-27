from analizar import analizar
import pandas as pd
if __name__ == "__main__":
    to_run = [
    "original",
    #"presupuesto",
    ##"presupuesto_0",
    ##"tiempo_minimo_video",
    #"tiempo_minimo_video_2", # no tiene solucion
    #"min_difusion_publicidad",
    #"min_difusion_publicidad_5",
    #"min_difusion_publicidad_10",
    ##"cantidad_personas_contenido",
    "tiempo_max_persona_mas_5",
    ##"tiempo_max_persona_mas_10",
    #"max_semanas_atraso", #no tiene solucion
    #"max_semanas_atraso_3", # se demora mucho, lo dejé para después
    #"max_semanas_atraso_2", # se demora muuuucho (pero menos que el anterior), también lo dejé para después
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
    for col in df.columns:
        ax = df[[col]].plot.bar(title=col)
        fig = ax.get_figure()
        fig.savefig(f'sensibilidad_{col}.png')


    print(df)
