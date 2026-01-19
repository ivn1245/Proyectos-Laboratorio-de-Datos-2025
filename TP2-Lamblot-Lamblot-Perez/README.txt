El objetivo de este proyecto fue utilizar el dataset de fashionMIST para construir dos clasificadores de imagenes: uno binario y otro multiclase. El analisis y el informe se centran en el desarrollo de los mismos, como se consiguieron los atributos optimos, como se seleccionaron los pixeles que se usaron para cada modelo y demas.

El programa consta de 3 secciones:
    - el analisis exploratorio
    - la clasificacion binaria usando knn
    - la clasificacion multiclase usando arboles de decision

el codigo tarda un aproximado de 4 min en correr. Si el codigo por alguna razon no corre puede ser debido a la linea:

scores = cross_val_score(modelo, X_dev, Y_dev, cv=5, scoring='accuracy', n_jobs=5) (en la tercera seccion)

Esto se debe al argumento n_jobs, que hace que el codigo corra mas rapido al realizar varias pruebas a la vez pero puede andar mal para ciertas computadoras, por lo que de haber algun problema al correr el codigo, el argumento se puede sacar tranquilamente.
