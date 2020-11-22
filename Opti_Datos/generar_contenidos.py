import pandas as pd

contenidos_list = []
for q in range(52):
    """
    Cada semana hay 6 contenidos de básica, 2 de inglés,
    3 de orientación, 1 de educación física y 1 de música
    """
    if q % 13 in (1, 2, 3, 4, 5, 6): # básica
        contenidos_list.append({"s": (q // 13) + 1, "d": "Básica"})
    elif q % 13 in (7, 8): # inglés
        contenidos_list.append({"s": (q // 13) + 1, "d": "Inglés"})
    elif q % 13 in (9, 10, 11): # orientación
        contenidos_list.append({"s": (q // 13) + 1, "d": "Orientación"})
    elif q % 13 == 12: # música
        contenidos_list.append({"s": (q // 13) + 1, "d": "Música"})
    elif q % 13 == 0: # educación física
        contenidos_list.append({"s": (q // 13) + 1, "d": "Educación física"})

df = pd.DataFrame.from_dict(contenidos_list)

df.to_csv("./contenidos.csv")
