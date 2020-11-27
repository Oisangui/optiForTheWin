# Como correr el código
basta con hacer
```sh
python main.py
```

Las librerías a instalar para correr el código son:
* pandas
* matplotlib
* gurobipy

# Subcarpetas

En input están todos los archivos que usamos para hacer correr el código. Están divididas por carpetas, dependiendo si es el problema original o si hay coeficientes variados para efectos de análisis de sensibilidad. En cada subcarpeta hay una pequeña explicación sobre qué parametros se variaron.

En output están los resultados respectivos de cada uno de esos problemas. Cada carpeta está subdividida en 4: 

* resultados, que contiene los gráficos

* variables, que contiene los valores de las variables en el óptimo

* restricciones, que contiene las holguras de cada restriccion

* valores, que contiene otros datos como el valor de la función objetivo en el óptimo alcanzado.

En graficos.comparacion, están los graficos de comparación de varios problemas entre ellos y el problema original, para vislumbrar si alguna variación aumenta el valor de la función objetivo y por ende conviene hacerla, o si no la aumenta y por ende no hay que hacerla.

# Explicación del código

El código está parcelado entre:
* main.py: decide las variaciones a correr y las corre. Están seleccionados por defecto todas las variaciones que terminan en menos de 5 minutos y que tienen solución. Para seleccionar o deseleccionar basta con comentar la línea.
* analizar.py: recibe una variación y realiza la optimización del modelo y finalmente genera los gráficos y guarda los datos.
* crear modelo.py: genera el modelo y sus partes
* generar graficos.py: genera los gráficos a partir de los datos.
* guardar datos.py: guarda los datos relevantes
* generar contenidos.py: genera los contenidos para n semanas (dejadas en 8 actualmente) dado que hay 6 contenidos a la semana de básica, 3 de inglés, 2 de orientación, 1 de música y 1 de educación física.
