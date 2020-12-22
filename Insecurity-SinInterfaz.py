import spacy
import re 
import string   
import unidecode
import time

#FUNCION QUE APLICA NLP
def nlp(texto):
    texto = texto.lower() #minuscula
    texto = unidecode.unidecode(texto) #acentos
    texto = ''.join(e for e in texto if e.isalnum() or e.isspace()) #caracteres especiales
    texto = ''.join(e for e in texto if not e.isdigit())
    texto = texto.lstrip() #espacio del principio
    texto = texto.rstrip() #espacio del final
    return texto

#PASA DE UN ARREGLO DE STRING A UN STRING SEPARADO POR COMAS
def toString(arreglo):
    resultado = ""
    for i in range(len(arreglo)):
        if i == 0 :
            resultado = resultado + arreglo[i]
        else:
            resultado = resultado + ", " + arreglo[i]
    return resultado

#RECIBE UN TEXTO Y DEVUELVE UN ARREGLO DE ENTIDADES
def entityRecognizer(texto):
    listaEntidades = []
    textoNLP = nlp(texto) #APLICO NLP
    #OBTENGO SUS ENTIDADES
    entidades = ner(textoNLP)
    i=0
    for i in range(len(entidades.ents)):
        entidad = entidades.ents[i].label_
        listaEntidades.append(entidad)
    return listaEntidades

#RECIBE UN ARREGLO DE ENTIDADES Y DEVUELVE UN STRING QUE INDICA SI ES SEGURO O NO
def textCategory(entidades):
    entidadesSTR = toString(entidades)
    #PASO LAS ENTIDADES EL TEXTCAT PARA VER SI ES UN HECHO DE INSEGURIDAD
    inseguridad = textcat(entidadesSTR)
    if inseguridad.cats['Inseguro'] < 0.4:
        categoria= "Segura"
    else:
        categoria= "Insegura"
    return categoria

#devuelve true si pasaron mas de 10 segundos
def time_passed(oldepoch):
    return time.time() - oldepoch >= 10


#CARGO LOS MODELOS E INICIALIZO LAS VARIABLES
nermodel = "NERModel"
textcatmodel = "TEXTCATTestModel"
cantidadEntidades = 0
numeroMaximoEntidades = 3
entidadesEnEspera =[]
entidadesAAnalizar = []
#CARGO EL MODELO DE NER
ner = spacy.load(nermodel)
#CARGO EL MODELO DE TEXTCAT
textcat = spacy.load(textcatmodel)


tiempoInicio = time.time()

#EL SEGUNDO ALGORITMO SE ACTIVA SI SE LLEGAN A 10 ENTIDADES O PASO MAS DE 30 SEG SIN UNA NUEVA ENTIDAD
#LOOPEA HASTA QUE ALGUNA DE LAS DOS COSAS OCURRA, ENTONCES AHI LLAMO AL SEGUNDO ALGORITMO
while cantidadEntidades <= numeroMaximoEntidades and not time_passed(tiempoInicio):
    tiempoInicio = time.time()
    texto = input("Ingrese una frase")
    print("Frase ingresada: "+texto)
    
    listaEntidadesAux = entityRecognizer(texto)
    cantidadEntidades = cantidadEntidades + len(listaEntidadesAux) 
    print("Entidade/s: "+toString(listaEntidadesAux))

    if time_passed(tiempoInicio) and cantidadEntidades <= numeroMaximoEntidades:
        entidadesEnEspera = entidadesEnEspera + listaEntidadesAux
        entidadesAAnalizar = entidadesEnEspera
        entidadesEnEspera = []
        print("Termine de escuchar porque pasaron mas de 10 seg")
    else:
        if cantidadEntidades >= numeroMaximoEntidades :
            #si las entidades a sumar superan el limite, mando a analizar esas entidades y creo un nuevo arreglo
            entidadesAAnalizar = entidadesEnEspera
            entidadesEnEspera = []
            entidadesEnEspera = entidadesEnEspera + listaEntidadesAux
            print("Termine de escuchar porque se llego al limite de entidades")
        else: 
            entidadesEnEspera = entidadesEnEspera + listaEntidadesAux
            print("Sigo escuchando")
    print("")

print("Entidades a analizar: "+toString(entidadesAAnalizar))
cantidadEntidades = 0
print("Analizando...")
print("LA CONVERSACION FUE: "+textCategory(entidadesAAnalizar))
    


