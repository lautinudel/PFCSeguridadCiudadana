from random import randint
import numpy

class GeneradorDatasetTEXTCAT(object):
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

    def __init__(self, arg):
        super(GeneradorDatasetTEXTCAT, self).__init__()
        self.arg = arg
        self.generarDataset()
        pass
    
    def generarDataset(self):
        archivo= open("TextClassifierDataset - Sin etiquetar.txt","a+")
        for i in range(self.cantidadFilas):
            cantidadColumnas = randint(0,self.cantidadPalabras)
            for j in range(cantidadColumnas):
                palabra = self.entidades[numpy.random.choice(numpy.arange(0, self.cantidadEntidades), p=self.probabilidades)]
                if j == 0 :
                    self.filaTexto = self.filaTexto + palabra
                else:
                    self.filaTexto = self.filaTexto + ", " + palabra
                if j==cantidadColumnas-1:
                    self.filaTexto += "\n"
                    archivo.write(self.filaTexto) 
                    self.filaTexto = ""
        archivo.close()
        pass

generadorDataset = GeneradorDatasetTEXTCAT({})

