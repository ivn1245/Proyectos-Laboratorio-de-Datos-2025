# -*- coding: utf-8 -*-
"""

Alumnos: Camila Lamblot, Nicole Lamblot e Iván Pérez
Materia: Laboratorio de Datos

El siguiente archivo se encuentro dividido en 4 secciones:
    -GQM
        Cálculo de las métricas de los 4 GQM registrados en el informe
    -limpieza  de los datos y armado de las tablas
        limpieza general de los archivos y creacion de las tablas modelo para uso posterior.
    -consultas SQL
        Las 4 consultas solicitadas en la consigna con algunos pasos intermedios de limpieza y normalización. Por ej la normlaización de la cantidad de establecimientos educativos en CABA.
    -graficos
        El proceso de creación de los gráficos, con las respectivas subconsultas necesarias.

Para la correcta ejecución de este archivo,las carpetas TablasModelo TablasOriginales y este mismo archivo deben encontrarse en el mismo directorio, osea, no separar los contenidos de la entrega.
Este archivo esta diseñado de tal forma que al ejecutar el código, las tablas de TablasModelo se sobreescriban con las mismas logrando que se pueda ejecutar todas las veces deseadas sin alterar el resultado.

"""
#%%
import numpy as np
import pandas as pd
import duckdb as dd
import matplotlib.pyplot as plt
from matplotlib import ticker 
import seaborn as sns
import math

#%%

#####################################################################################


#GQM


#####################################################################################

#%%

EE=pd.read_csv('TablasOriginales/establecimientos_educativos.csv', dtype={'Código de departamento': str})
BP=pd.read_csv('TablasOriginales/bibliotecas-populares.csv', dtype={'id_departamento': str})

#%%

#1ra GQM

EE.rename(columns={
    'Unnamed: 37': 'talleres_artistica',
    'Unnamed: 38': 'servicios_complementarios',
    'Unnamed: 39': 'validez_titulos'
}, inplace=True)

celdas_vacias = EE[["talleres_artistica", "servicios_complementarios", "validez_titulos"]].isna().all(axis=1).sum()
print(celdas_vacias)

total_celdas = EE.shape[0]
print(total_celdas)

GQM_1 = celdas_vacias/total_celdas
print(GQM_1)

#%%

#2da GQM

consultaSQL = """
                SELECT 
                COUNT(*) AS total_tuplas,
                COUNT(CASE WHEN Mail LIKE '%/%' THEN 1 END) AS tuplas_con_mas_de_un_mail
                FROM EE
                """
    
tuplas_con_mas_de_un_mail = dd.sql(consultaSQL).df()

cant_mas_de_un_mail = tuplas_con_mas_de_un_mail['tuplas_con_mas_de_un_mail']
print(cant_mas_de_un_mail)

total_tuplas = tuplas_con_mas_de_un_mail['total_tuplas']
print(total_tuplas)

GQM_2 = cant_mas_de_un_mail/total_tuplas
print(GQM_2)

#%%

#4ta GQM

celdas_vacias = BP["mail"].isna().sum()
print(celdas_vacias)

total_celdas = BP.shape[0]
print(total_celdas)

GQM_4 = celdas_vacias/total_celdas
print(GQM_4)

#%%
#####################################################################################


#limpieza de los datos y armado de las tablas


#####################################################################################



#%%
# Limpieza de 'poblacion'

# %%
poblacion = pd.read_csv("TablasOriginales/padron_poblacion.csv")
print(poblacion)

# %%
def convertir_en_una_tabla(poblacion):
    poblacion = pd.read_csv(poblacion)
    #tomo las columnas que me importan
    poblacion_1=poblacion.iloc[11:,1:5]
    filas=[]
    id_dpto=''
    dpto=""
    for _, row in poblacion_1.iterrows():
        # Ponemos un break cuando aparezca el resumen
        if (row.iloc[0]=='RESUMEN'):
            break

        # Saltea filas vacias, filas con nombres de las tablas o filas con totales
        if row.isna().all() or (row.iloc[0]=='Edad') or (row.iloc[0]=='Total'):
            continue

        # Detecta fila de nombre dpto: primeras 4 celdas NaN y la 3ra (índice 2) no NaN
        if (row.iloc[2:5].isna().all())and (pd.notna(row.iloc[1])):
            id_dpto= str(row.iloc[0])
            dpto = str(row.iloc[1])
            continue
        
        # agrega a filas los datos limpios como lista de tuplas
        filas.append({
            'Id_Departamento': id_dpto,
            'Departamento': dpto,
            'Edad': row.iloc[0],
            'cantidad': row.iloc[1]
            })

    # Crea el DataFrame final
    limpio = pd.DataFrame(filas)
    return limpio

#%%
# usamos la funcion para unificar el archivo de poblacion
df=convertir_en_una_tabla('TablasOriginales/padron_poblacion.csv')

# %%  [markdown]
#vemos que las cantidaddes no tienen el formato de numero, sino que es un string con un espacio en el medio

# %%
# Eliminamos espacios internos y convertimos a int las cantidades
df["cantidad"] = df["cantidad"].str.replace(" ", "")
df["cantidad"] = (df["cantidad"]).astype('int64')

df['Edad']=df['Edad'].astype('int64')
print(df["cantidad"].sum())
print(len(df))
print(df)

# %%
#saco el texto de la columna ID
df['Id_Departamento'] = df['Id_Departamento'].str[7:]
print(df)


# %%
df.loc[df['Departamento'].str.contains('Comuna'),['Id_Departamento','Departamento']]=['02000','CABA']
print(df)

# %% [markdown]
# Agrupo por rango etareo

# %%
def clasificar_grupo_etario(edad):
    if 2 <= edad <= 5:
        return 'jardin'
    elif 6 <= edad <= 12:
        return 'primaria'
    elif 13 <= edad <= 18:
        return 'secundaria'
    else:
        return 'otros'

df['grupo_etario'] = df['Edad'].apply(clasificar_grupo_etario)
print(df['grupo_etario'])



# %%
agrupado = df.groupby(['Id_Departamento','Departamento', 'grupo_etario'])['cantidad'].sum().reset_index()
print(agrupado)

# %%
df_final = agrupado.pivot(index=['Id_Departamento','Departamento'], columns='grupo_etario', values='cantidad').fillna(0).reset_index()
print(df_final)

# %% [markdown]
# Creamos el archivo de excel con este nuevo df y la columna de Id_Provincia

df_final['Id_Provincia']=df_final['Id_Departamento'].str[:2]
df_final.to_csv("TablasModelo/Departamentos.csv", index=False)

# %% [markdown]
# Definimos los tres dataframes para seguir la limpieza

# %%
PpE=pd.read_csv('TablasModelo/Departamentos.csv')
PpE['Departamento']=PpE['Departamento'].str.lower()
EE=pd.read_csv('TablasOriginales/establecimientos_educativos.csv', dtype={'Código de departamento': str})
EE['Departamento']=EE['Departamento'].str.lower()
BP=pd.read_csv('TablasOriginales/bibliotecas-populares.csv', dtype={'id_departamento': str})
BP['departamento']=BP['departamento'].str.lower()

# %% [markdown]
# Asignamos mismos ids para los departamentos de CABA en EE (PpE y BP ya lo tienen actualizado)

# %%
EE.loc[EE['Departamento'].str.contains('comuna'),['Departamento','Código de departamento']]=['CABA','02000']
print(EE)

# %% [markdown]
# Creamos tabla provincias

# %%
BP.columns
BP['id_provincia']=BP['id_provincia'].astype(str).str.zfill(2)
provincias=BP[['id_provincia','provincia']].drop_duplicates()
print(provincias)
provincias.to_csv('TablasModelo/Provincias.csv',index=False)



# %% [markdown]
# creamos tabla Bibliotecas_Populares

# %%
Bibliotecas_Populares=BP[['nro_conabip','nombre','id_departamento','fecha_fundacion','mail']]
Bibliotecas_Populares['id_departamento']=Bibliotecas_Populares['id_departamento']
print(Bibliotecas_Populares)

# %%
Bibliotecas_Populares.to_csv('TablasModelo/Bibliotecas_Populares.csv', index=False, encoding='utf-8')

# %% [markdown]
# creamos tabla escuela modalidad comun

# %% [markdown]
# filtramos por la modalidad comun y las submodalidades importantes

# %%
Establecimientos_Educativos=EE[(EE['Común']==1) & ((EE['Nivel inicial - Jardín de infantes']==1) | (EE['Primario']==1) | (EE['Secundario']))]
print(Establecimientos_Educativos)


# %%
Establecimientos_Educativos=Establecimientos_Educativos[['Cueanexo','Nombre','Código de departamento','Ámbito','Sector']]
print(Establecimientos_Educativos)
Establecimientos_Educativos.to_csv('TablasModelo/Escuelas_Modalidad_Comun.csv',index=False,encoding='utf-8')

# %% [markdown]
# creamos tabla de submodalidades para luego hacer la tabla que conecte cada escuela con su submodalidad

# %%
Submodalidad=[]
Submodalidad.append({'Id_Submodalidad': '1', 'submodalidad': 'jardin'})
Submodalidad.append({'Id_Submodalidad': '2', 'submodalidad': 'primario'})
Submodalidad.append({'Id_Submodalidad': '3', 'submodalidad': 'secundario'})

Submodalidades= pd.DataFrame(Submodalidad)
print(Submodalidades)

# %%
Submodalidades.to_csv('TablasModelo/Submodalidades.csv',index=False)

# %% [markdown]
# Creamos tabla de relacion entre submodalidades con establecimientos educativos

# %% [markdown]
# uso la funcion melt con las 3 submodalidades

# %%
EE=pd.read_csv('TablasOriginales/establecimientos_educativos.csv', dtype={'Código de departamento': str})
EE['Departamento']=EE['Departamento'].str.lower()
EE=EE[(EE['Común']==1) & ((EE['Nivel inicial - Jardín de infantes']==1) | (EE['Primario']==1) | (EE['Secundario']))]
conexion= EE[['Cueanexo','Nivel inicial - Jardín de infantes','Primario','Secundario']]

conexion = conexion.rename(columns={
    'Nivel inicial - Jardín de infantes': '1',
    'Primario' : '2',
    'Secundario' : '3'
})

# %%

df_largo = conexion.melt(id_vars='Cueanexo', 
                   value_vars=['1', '2', '3'], 
                   var_name='submodalidad', 
                   value_name='marcado')

df_filtrado = df_largo[df_largo['marcado'] == 1].drop(columns='marcado')
print(df_filtrado)
df_filtrado = df_filtrado.sort_values(by='Cueanexo')
print(df_filtrado)
df_filtrado.to_csv('TablasModelo/Submodalidades_EE.csv', index=False)

#%%

#####################################################################################


#consultas


#####################################################################################
carpeta = 'TablasModelo/'
#%%
#cambiamos los nombres a las tablas para poder realizar consultas más limpias

ee = pd.read_csv(carpeta+'Escuelas_Modalidad_Comun.csv')
bp = pd.read_csv(carpeta+'Bibliotecas_Populares.csv')
deptos = pd.read_csv(carpeta+'Departamentos.csv')
prov = pd.read_csv(carpeta+'Provincias.csv')
submodalidades = pd.read_csv(carpeta+'Submodalidades_EE.csv')
submo = pd.read_csv(carpeta+'Submodalidades.csv')

#%%
#Cambiamos nombres de las columnas:

bp["año_fundacion"] = pd.to_datetime(bp["fecha_fundacion"], errors="coerce").dt.year
del bp["fecha_fundacion"]

deptos.rename(columns={
    'Id_Departamento': 'id_departamento',
    'Id_Provincia': 'id_provincia',
    'jardin': 'pob_jardin',
    'primaria': 'pob_primaria',
    'secundaria': 'pob_secundaria',
    'Departamento': 'departamento'
}, inplace=True)

submodalidades.rename(columns={
    'Cueanexo': 'cueanexo'    
}, inplace=True)

ee.rename(columns={
    'Cueanexo': 'cueanexo',
    'Nombre': 'nombre',
    'Ámbito': 'ambito',
    'Sector': 'sector',
    'Código de departamento': 'id_departamento'
}, inplace=True)

prov.loc[prov['provincia'] == 'Ciudad Autónoma de Buenos Aires', 'provincia'] = 'CABA'

#%%
#Normalizamos la población de CABA dividiendola por la cantidd de comunas totales

deptos.loc[deptos['id_departamento'] == 2000, 'pob_jardin'] = round(deptos['pob_jardin'] / 15)
deptos.loc[deptos['id_departamento'] == 2000, 'pob_primaria'] = round(deptos['pob_primaria'] / 15)
deptos.loc[deptos['id_departamento'] == 2000, 'pob_secundaria'] = round(deptos['pob_secundaria'] / 15)
deptos.loc[deptos['id_departamento'] == 2000, 'otros'] = round(deptos['otros'] / 15)

#%%

#CONSULTAS
# i)

consultaSQL = """
                SELECT
                prov.provincia AS Provincia,
                deptos.departamento AS Departamento,
                
                -- Contamos la cantidad de escuelas de cada nivel --
                
                COUNT(DISTINCT CASE WHEN sm.submodalidad = 'jardin' THEN s.cueanexo END) AS Jardines,
                deptos.pob_jardin AS Poblacion_Jardin,  
                COUNT(DISTINCT CASE WHEN sm.submodalidad = 'primario' THEN s.cueanexo END) AS Primarias,
                deptos.pob_primaria AS Poblacion_Primaria,
                COUNT(DISTINCT CASE WHEN sm.submodalidad = 'secundario' THEN s.cueanexo END) AS Secundarias,
                deptos.pob_secundaria AS Poblacion_Secundaria

                FROM submodalidades AS s
                
                -- Unimos las tablas involucradas --
                
                JOIN submo AS sm ON sm.Id_Submodalidad = s.submodalidad
                JOIN ee ON ee.cueanexo = s.cueanexo
                JOIN deptos ON ee.id_departamento = deptos.id_departamento
                JOIN prov ON deptos.id_provincia = prov.id_provincia
                
                -- Ordenamos y agrupamos de acuerdo al enunciado de la consulta --
                
                GROUP BY prov.provincia, deptos.departamento, deptos.pob_jardin, deptos.pob_primaria, deptos.pob_secundaria
                
                ORDER BY prov.provincia ASC, Primarias DESC;
                                                                """
    
 
    
primeraConsulta = dd.sql(consultaSQL).df()

#%%

# Normalizamos la cantidad de escuelas de cada nivel de CABA dividiendo por el total de sus comunas.

# Aplicamos 'round' para redondear los números con decimal según si sus decimales son mayores o menores a 0.5 para tener números enteros.

primeraConsulta.loc[primeraConsulta['Departamento'] == "CABA", 'Jardines'] = round(primeraConsulta['Jardines'] / 15)
primeraConsulta.loc[primeraConsulta['Departamento'] == "CABA", 'Primarias'] = round(primeraConsulta['Primarias'] / 15)
primeraConsulta.loc[primeraConsulta['Departamento'] == "CABA", 'Secundarias'] = round(primeraConsulta['Secundarias'] / 15)

#primeraConsulta.to_csv('primeraConsulta.csv', index=False)

print(primeraConsulta)

#%%

#ii)

consultaSQL = """
                SELECT prov.provincia AS Provincia, 
                deptos.departamento AS Departamento,
                
                -- Cuenta las BP fundadas desde 1950 (si cumple la condición, cuenta nro_conabip) --
                
                COUNT(CASE WHEN bp.año_fundacion >= 1950 THEN bp.nro_conabip END) AS "Cantidad de BP fundadas desde 1950"
                
                FROM bp
                
                -- Unimos a bp las tablas de departamento y provincia para obtener los nombres de los departamentos y de provincias --
                
                JOIN deptos ON bp.id_departamento = deptos.id_departamento
                JOIN prov ON deptos.id_provincia = prov.id_provincia
                
                -- Ordenamos y agrupamos de acuerdo al enunciado de la consulta --
                
                GROUP BY prov.provincia, deptos.departamento
                
                ORDER BY prov.provincia ASC, "Cantidad de BP fundadas desde 1950" DESC;
                
              """
              
segundaConsulta = dd.sql(consultaSQL).df()

#segundaConsulta.to_csv('segundaConsulta.csv', index=False)

print(segundaConsulta)

#%%

#iii)

consultaSQL = """
                SELECT 
                prov.provincia AS Provincia,
                deptos.departamento AS Departamento,
                ee_data.Cant_EE AS Cant_EE,
                bp_data.Cant_BP AS Cant_BP,
                
                -- Calculamos la población total de cada departamento sumando todas las categorías --
                
                (deptos.pob_jardin + deptos.pob_primaria + deptos.pob_secundaria + deptos.otros) AS Población
            
                FROM deptos
                
                -- Unimos con la tabla de provincias para obtener el nombre de la provincia correspondiente --
                
                JOIN prov ON deptos.id_provincia = prov.id_provincia
                
                -- Armamos 2 subconsultas (Cant_EE y Cant_BP) para contar la cantidad de establecimientos y bibliotecas por departamento. Hacemos LEFT JOIN para incluir aquellos departamentos que no tengan escuelas y/o bibliotecas --
                
                LEFT JOIN (
                    SELECT id_departamento, COUNT(*) AS Cant_EE
                    FROM ee
                    GROUP BY id_departamento
                ) AS ee_data ON ee_data.id_departamento = deptos.id_departamento
                LEFT JOIN (
                    SELECT id_departamento, COUNT(*) AS Cant_BP
                    FROM bp
                    GROUP BY id_departamento
                ) AS bp_data ON bp_data.id_departamento = deptos.id_departamento;"""
              
aux_terceraConsulta = dd.sql(consultaSQL).df()


#%%

# Normalizamos la cantidad de escuelas de cada nivel y la cantidad de bibliotecas de CABA dividiendo por el total de sus comunas.

aux_terceraConsulta.loc[aux_terceraConsulta['Departamento'] == "CABA", 'Cant_BP'] = round(aux_terceraConsulta['Cant_BP'] / 15)
aux_terceraConsulta.loc[aux_terceraConsulta['Departamento'] == "CABA", 'Cant_EE'] = round(aux_terceraConsulta['Cant_EE'] / 15)

# Reemplazamos los valores nulos en Cant_BP y Cant_EE por 0

aux_terceraConsulta.loc[aux_terceraConsulta['Cant_BP'].isna(), 'Cant_BP'] = 0
aux_terceraConsulta.loc[aux_terceraConsulta['Cant_EE'].isna(), 'Cant_EE'] = 0

# Definimos una nueva consulta igual a aux_terceraConsulta, pero con las modificaciones aplicadas
# y ordenamos los datos de acuerdo al enunciado.

consultaSQL = """SELECT (*)
                     FROM aux_terceraConsulta
                     ORDER BY Cant_EE DESC, Cant_BP DESC, Provincia ASC, Departamento ASC;"""

terceraConsulta = dd.sql(consultaSQL).df()

#terceraConsulta.to_csv('terceraConsulta.csv', index=False)

print(terceraConsulta)
#%%

#iv)

consultaSQL = """
                
                -- Primero hacemos una tabla que tenga los dominios que aparecen en cada departamento y su cantidad por departamento --   
                
                WITH c2 AS (
                SELECT prov.provincia, deptos.departamento,
                
                -- Nos quedamos con el dominio del correo después del '@' --
                
                SUBSTR(bp.mail, INSTR(bp.mail, '@') + 1) AS dominio,
                
                -- Contamos cuántas veces aparece cada dominio por departamento --
                
                COUNT(*) AS cantidad
    
                FROM bp
                
                -- Unimos a bp con departamentos y provincias para obtener nombres --
                
                JOIN deptos ON bp.id_departamento = deptos.id_departamento
                JOIN prov ON deptos.id_provincia = prov.id_provincia
                
                -- Solo consideramos tuplas que tengan el mail no nulo --
                
                WHERE bp.mail IS NOT NULL
                
                -- Agrupamos por provincia, departamento y dominio de mail --
                
                GROUP BY deptos.departamento, prov.provincia, dominio)
    
                
                SELECT c2.provincia, c2.departamento, c2.dominio AS "Dominio más frecuente en BP"
                
                FROM c2
                
                -- Nos quedamos con el dominio que tenga la mayor cantidad dentro de cada departamento --
                
                WHERE c2.cantidad = (
                SELECT MAX(c3.cantidad)
                FROM c2 AS c3
                WHERE c3.departamento = c2.departamento)
                
                -- Ordenamos según el enunciado --
                
                ORDER BY provincia ASC, departamento ASC;
    
    """
    
    
cuartaConsulta = dd.sql(consultaSQL).df()

#cuartaConsulta.to_csv('cuartaConsulta.csv', index=False)

print(cuartaConsulta)

#%%
#####################################################################################


#GRÁFICOS


#####################################################################################
#i)

# Primero contamos la cantidad total de bp por provincia
consultaSQL = """
                SELECT prov.provincia AS Provincia,
                COUNT(*) AS "Cantidad de BP"
                
                FROM bp
                
                JOIN deptos ON bp.id_departamento = deptos.id_departamento
                JOIN prov ON deptos.id_provincia = prov.id_provincia
                
                GROUP BY prov.provincia;
              """
              
aux_cant_BP = dd.sql(consultaSQL).df()

# Ordenamos la tabla según el enunciado
consulta2SQL = """
                SELECT *
                FROM aux_cant_BP AS aux
                ORDER BY "Cantidad de BP" DESC;
              """
cant_BP = dd.sql(consulta2SQL).df()

# Hacemos un gráfico de barra
fig, ax = plt.subplots()

plt.rcParams['font.family'] = 'sans-serif'

ax.bar(data=cant_BP, x='Provincia', height = 'Cantidad de BP')

ax.set_title('Bibliotecas por provincia')
ax.set_xlabel('Provincias', fontsize='medium')
ax.set_ylabel('Cantidad de BP', fontsize = 'medium')
ax.set_xlim(-1,23)
ax.set_ylim(0,520)

ax.set_yticks([])
ax.bar_label(ax.containers[0], fontsize=8)

ax.tick_params(axis='x', rotation=90, labelsize=8)

plt.show()

#%%
#ii)

# Creamos el gráfico basándonos en la primera consulta y utilizando la estructura del scatter.
# Hacemos 3 gráficos (uno para cada nivel educativo) mostrándolos en uno general. 

fig, ax = plt.subplots()

# Jardín
plt.rcParams['font.family'] = 'sans-serif'
ax.scatter(data = primeraConsulta, 
           x = 'Poblacion_Jardin', 
           y = 'Jardines', 
           s=8, 
           color='green',
           label='Jardín')

# Primaria
ax.scatter(data = primeraConsulta, 
           x = 'Poblacion_Primaria', 
           y = 'Primarias', 
           s=8, 
           color='blue',
           label='Primaria')

# Secundaria
ax.scatter(data = primeraConsulta, 
           x = 'Poblacion_Secundaria', 
           y = 'Secundarias', 
           s=8, 
           color='red',
           label='Secundaria')


ax.set_title('Establecimientos educativos según nivel y grupo etario')
ax.set_xlabel('Población', fontsize='medium')
ax.set_ylabel('Cantidad de EE', fontsize = 'medium')

#ax.set_xlim(0,80000)
#ax.set_ylim(0,300)

plt.legend()

plt.show()

#%%
#iii)

# Hacemos una consulta para obtener una tabla con las provincias, sus departamentos y la cantidad de escuelas en cada uno.

consultaSQL = """
                -- Seleccionamos los datos de cantidad de EE por provincia y departamento obtenidos en la tercera consulta --
                
                SELECT Provincia, 
                Departamento,
                Cant_EE
                
                FROM terceraConsulta
                
                ORDER BY Provincia ASC, Departamento ASC;"""
                
Consulta = dd.sql(consultaSQL).df()


# Hacemos una consulta para obtener las medianas de la cantidad de escuelas por departamento de cada provincia

medianas_provincias = """

                -- Subconsulta para calcular la mediana de cada provincia --

                WITH medianas AS (
                    SELECT Provincia, 
                    median(Cant_EE) AS mediana
                    
                    FROM Consulta
                    
                    GROUP BY Provincia
                )
                
                -- Ahora seleccionamos los atributos para nuestro nuevo df
                
                SELECT Consulta.Provincia, 
                m.mediana
                
                FROM Consulta
                
                -- Unimos con medianas --
                
                JOIN medianas AS m ON Consulta.Provincia = m.Provincia
                
                GROUP BY Consulta.Provincia, m.mediana
                
                -- Ordenamos los datos según el valor de las medianas ascendentemente --
                
                ORDER BY m.mediana ASC

                """

mediana = dd.sql(medianas_provincias).df()

#GRAFICO
ax = sns.boxplot(x='Provincia',
                 y= 'Cant_EE',
                 data= Consulta,
                 order=mediana['Provincia'], 
                 color = 'magenta', 
                 showmeans=True,
                 meanprops={
                    'marker': '^',        
                    'markerfacecolor': 'green',
                    'markeredgecolor': 'green',
                    'markersize': 2 })

ax.set_title('Establecimientos educativos por provincia')
ax.set_xlabel('Provincias')
ax.set_ylabel('Cantidad de EE')
ax.set_ylim(0,1200)
ax.tick_params(axis='x', rotation=90, labelsize=8)

plt.show()
#%%
# iv)

# Copiamos el df obtenido en la tercera consulta ya que tiene la cantidad de bp y ee que hay en cada departamento
cada_mil = terceraConsulta.copy()

# Agregamos dos columnas al nuevo df que digan la cantidad de bp y ee cada mil habitantes por departamento.
# Obtenemos esa información dividiendo la cantidad total de cada institución por la población y multiplicando por 1000
cada_mil["BP_cada_mil"] = cada_mil["Cant_BP"] / cada_mil["Población"] * 1000
cada_mil["EE_cada_mil"] = cada_mil["Cant_EE"] / cada_mil["Población"] * 1000

# Hacemos un scatter plot
fig, ax = plt.subplots()


plt.rcParams['font.family'] = 'sans-serif'
ax.scatter(data = cada_mil, 
           x = 'EE_cada_mil', 
           y = 'BP_cada_mil', 
           s=8, 
           color='blue')

ax.set_title('Relación entre  cantidad de EE y de BP cada mil habitantes por departamento.')
ax.set_xlabel('Cantidad de EE cada mil habitantes', fontsize='medium')
ax.set_ylabel('Cantidad de BP cada mil habitantes', fontsize = 'medium')

plt.show()