from random import randint
import numpy

cantidadFilas = 5000
cantidadPalabras = 10

entidades = [
  "Insulto",
  "Amenaza",
  "Orden Amenazante",
  "Pedido de ayuda",
  "Rechazo",
  "Agradecimiento",
  "Saludo",
  "Aprobacion",
  "Orden Amistosa",
  "Pedir Disculpas"
    ]
cantidadEntidades = len(entidades)
probabilidades = [
    0.05,
    0.05,
    0.05,
    0.05,
    0.05,
    0.15,
    0.15,
    0.15,
    0.15,
    0.15
 ]

filaTexto = ""
f= open("TextClassifierDataset - Sin etiquetar.txt","a+")

for i in range(cantidadFilas):
    cantidadColumnas = randint(0,cantidadPalabras)
    for j in range(cantidadColumnas):
        palabra = entidades[numpy.random.choice(numpy.arange(0, cantidadEntidades), p=probabilidades)]
        if j == 0 :
            filaTexto = filaTexto + palabra
        else:
            filaTexto = filaTexto + ", " + palabra
        if j==cantidadColumnas-1:
            filaTexto += "\n"
            f.write(filaTexto) 
            filaTexto = ""

f.close()



#agregar las entidades finales - LISTO
#cambiar las probabilidades (opcional) - LISTO
#en el primer for aumentar las cantidad de filas (2000 aprox) - LISTO
#en el segundo for, hacer el limite aleatorio entre 1 y 10 para que no sean de la misma longitud todas las frases (puede ser un numero aleatorio o con probabilidades) - LISTO
#Al momento de etiquetar, ver de agregar mas tipos (ahora solo se etiqueta como seguro o inseguro)
#IMPORTANTE: despues de etiquetar, ver que el dataset este balanceado

