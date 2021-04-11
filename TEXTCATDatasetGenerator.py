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
