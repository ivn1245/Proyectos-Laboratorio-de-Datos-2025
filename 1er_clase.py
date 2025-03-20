import random
def pertenece(lista: list[int],elem: int)->bool:
        res = False
        for i in lista:
            if (i == elem):
                res = True
        return res
        

#print( pertenece([1,2,3,4],3))
   
def mas_larga(lista1, lista2):
    if (len(lista1) < len(lista2)):
        res = lista2
    elif (len(lista1) > len(lista2)):
        res = lista1
    else:
        res = lista1
    return res

#print(mas_larga([1,2,3],[1,2]))

def mezclar(cadena1: str, cadena2: str)->str:
    res:str=""
    for i in range (len(mas_larga(cadena1,cadena2))):
        if (i<len(cadena1)):
            res+=cadena1[i]
        if (i<len(cadena2)):
            res+=cadena2[i]
    return res

#print(mezclar("azul","amarillo"))

def traductor_geringoso(lista):
    res:dict={}
    for elem in lista:
        palabra=""
        for i in range (len(elem)):
            palabra+=elem[i]
            if (elem[i] in ["a","e","i","o","u"]):
                palabra+="p"
                palabra+=elem[i]
        res[elem] = palabra
    return res

#print(traductor_geringoso(['banana', 'manzana', 'mandarina']))

with open("datame.txt", 'rt') as file:
    data = file.read()

with open('datame.txt', 'rt') as file:
    data = file.read()
    data_nuevo = '2024 seguimos con DATAME\n\n' + data
    data_nuevo = data_nuevo + 'Dirección de Carrera LCD'
    datame = open("datame.txt","w")#write mode
    datame.write(data_nuevo)
    datame.close()

with open("datame.txt", 'rt') as file:
    data = file.read()

#print (data)
        
with open("cronograma_sugerido.csv",'rt' ) as file:
    for line in file:
        datos_linea = line.split(",")

#print(datos_linea[2])        


def tirar_dados():
    i=0
    res =[]
    while i<5:
        elem=random.randint(1,6)
        res.append(elem)
        i+=1
    return res

print(tirar_dados())