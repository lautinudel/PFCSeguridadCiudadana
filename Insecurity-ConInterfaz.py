import spacy
from pathlib import Path
import re
import string
import unidecode
import time
import sched
from appJar import gui
from threading import Timer
from datetime import datetime
import pysrt
import threading
import os
from os import startfile


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# FUNCION QUE APLICA NLP
def nlp(texto):
    texto = texto.lower()  # minuscula
    texto = unidecode.unidecode(texto)  # acentos
    texto = ''.join(e for e in texto if e.isalnum()
                    or e.isspace())  # caracteres especiales
    texto = ''.join(e for e in texto if not e.isdigit())
    texto = texto.lstrip()  # espacio del principio
    texto = texto.rstrip()  # espacio del final
    return texto

# PASA DE UN ARREGLO DE STRING A UN STRING SEPARADO POR COMAS
def toString(arreglo):
    resultado = ""
    for i in range(len(arreglo)):
        if i == 0:
            resultado = resultado + arreglo[i]
        else:
            resultado = resultado + ", " + arreglo[i]
    return resultado

# RECIBE UN TEXTO Y DEVUELVE UN ARREGLO DE ENTIDADES
def entityRecognizer(texto):
    listaEntidades = []
    textoNLP = nlp(texto)  # APLICO NLP
    # OBTENGO SUS ENTIDADES
    entidades = ner(textoNLP)
    i = 0
    for i in range(len(entidades.ents)):
        entidad = entidades.ents[i].label_
        listaEntidades.append(entidad)
    return listaEntidades

# RECIBE UN ARREGLO DE ENTIDADES Y DEVUELVE UN STRING QUE INDICA SI ES SEGURO O NO
def textCategory(entidades):
    global primerCorrida

    primerCorrida = False
    entidadesSTR = toString(entidades)
    # PASO LAS ENTIDADES EL TEXTCAT PARA VER SI ES UN HECHO DE INSEGURIDAD
    inseguridad = textcat(entidadesSTR)
    probabilidades = [inseguridad.cats['Muy Inseguro'], inseguridad.cats['Inseguro'], inseguridad.cats['Seguro'], inseguridad.cats['Muy Seguro']]
    if inseguridad.cats['Muy Inseguro'] == max(probabilidades):
        categoria = "Muy Insegura"
        app.setMeter("NivelSeguridad", 100, text="Muy Insegura")       
    else:
        if inseguridad.cats['Inseguro'] == max(probabilidades):
            categoria = "Insegura"
            app.setMeter("NivelSeguridad", 75, text="Insegura") 
        else:
            if inseguridad.cats['Seguro'] == max(probabilidades):
                categoria = "Segura"
                app.setMeter("NivelSeguridad", 25, text="Segura")
            else: 
                if inseguridad.cats['Muy Seguro'] == max(probabilidades):
                    categoria = "Muy Segura"
                    app.setMeter("NivelSeguridad", 1, text="Muy Segura")
    app.after(8000,app.setMeter, "NivelSeguridad", 0, "Analizando...")     
    return categoria

def vencioTiempo():
    global entidadesEnEspera
    global entidadesAAnalizar
    global timepoEspera
    global mensajes
    global cantidadEntidades
    global entidadesASolapar

    entidadesASolapar = []

    if (len(entidadesEnEspera) > cantidadEntidadesASolapar or ( len(entidadesEnEspera) > 0 and primerCorrida )):
        entidadesAAnalizar = entidadesEnEspera
        entidadesEnEspera = []
        print("Termine de escuchar porque pasaron mas de "+str(timepoEspera)+" seg")
        print("Entidades a analizar: "+toString(entidadesAAnalizar))
        cantidadEntidades = 0
        print("Analizando...")
        mensajes.insert(0,"")        
        resultado = textCategory(entidadesAAnalizar)        
        mensajes.insert(0,"- "+datetime.now().strftime('%H:%M:%S')+"    "+"Pasaron mas de " +
             str(timepoEspera)+" seg -> LA CONVERSACION FUE: "+resultado)
        print("LA CONVERSACION FUE: "+resultado)
        app.updateListBox("mensajes", mensajes, select=False)
        app.updateListBox("mensajesEscena", mensajes, select=False)
        
def seguridadCiudadana(texto):
    print("")
    print(bcolors.HEADER  + "Texto ingresado: " + unidecode.unidecode(texto) + bcolors.ENDC)

    global cantidadEntidades
    global numeroMaximoEntidades
    global entidadesEnEspera
    global entidadesAAnalizar
    global timepoEspera
    global t

    #reseteo el cronometro
    t.cancel()
    t = None
    t = Timer(timepoEspera, vencioTiempo)
    t.start()

    listaEntidadesAux = entityRecognizer(texto)
    cantidadEntidades = cantidadEntidades + len(listaEntidadesAux)

    print("Entidade/s: "+toString(listaEntidadesAux))
    

    if cantidadEntidades >= numeroMaximoEntidades: #se supera el limite del arreglo y se manda a analizar el lote de entidades
        deltaEntidades = numeroMaximoEntidades-len(entidadesEnEspera)
        if deltaEntidades > 0: 
            #si las nuevas entidades superan el limite pero el arreglo de entidades no se lleno todavia
            entidadesAAnalizar = entidadesEnEspera + listaEntidadesAux[:deltaEntidades] #agrego lo que falta para llenar el arreglo de entidades a analizar
            entidadesEnEspera = listaEntidadesAux[deltaEntidades:]  
        else:
            # si las entidades a sumar superan el limite, mando a analizar esas entidades y creo un nuevo arreglo
            entidadesAAnalizar = entidadesEnEspera
            entidadesEnEspera = [] + listaEntidadesAux
        entidadesASolapar = entidadesAAnalizar[-cantidadEntidadesASolapar:]
        entidadesEnEspera = entidadesASolapar + entidadesEnEspera
        print("Termine de escuchar porque se llego al limite de entidades")
        print("Entidades a analizar: "+toString(entidadesAAnalizar))
        cantidadEntidades = len(entidadesEnEspera)
        print("Analizando...")
        resultado = textCategory(entidadesAAnalizar)
        print("LA CONVERSACION FUE: "+resultado)
        return "- "+datetime.now().strftime('%H:%M:%S')+"    "+"Se llego al limite de entidades -> LA CONVERSACION FUE: "+resultado
    else:
        entidadesEnEspera = entidadesEnEspera + listaEntidadesAux
        print("Sigo escuchando")
        return "- "+datetime.now().strftime('%H:%M:%S')+"    "+"Entidad/es: "+toString(listaEntidadesAux)
    
# CARGO LOS MODELOS E INICIALIZO LAS VARIABLES
nermodel = "Modelos/NERModel"
textcatmodel = "Modelos/TEXTCATModel"
cantidadEntidades = 0
cantidadEntidadesASolapar = 1
numeroMaximoEntidades = 4
timepoEspera = 10  #en segundos
entidadesASolapar = []
entidadesEnEspera = []
entidadesAAnalizar = []
t = Timer(0, None)
primerCorrida = True
ner = spacy.load(nermodel) # CARGO EL MODELO DE NER
textcat = spacy.load(textcatmodel) # CARGO EL MODELO DE TEXTCAT

mensajes = []

#Manejo de botones
def botonesChat(button):
    global mensajes
    if button == "Volver":
        app.firstFrame("MENU")
    else:            
        msj = app.getEntry("Mensaje")
        enviarMensaje(msj)
        app.clearEntry("Mensaje", callFunction=True)

def botonesMenu(button):
    global mensajes

    mensajes = []
    app.updateListBox("mensajes", mensajes, select=False)
    app.updateListBox("mensajesEscena", mensajes, select=False)
    if button == "Chat": 
        app.nextFrame("MENU")
        app.setFocus("Mensaje")
    else: 
        if button == "Demo en vivo": 
            app.nextFrame("MENU")
            app.nextFrame("MENU")

def botonesDemo(button):
    global mensajes

    if button == "Atras": app.firstFrame("MENU")
    else: 
        if button == "Apache":
            subs = pysrt.open('Recursos/Videos/Apache Escena.srt',encoding='utf-8')
            startfile(os.path.normpath("Recursos/Videos/Apache Escena.mp4"))
        else:
            if button == "El Clan":
                subs = pysrt.open('Recursos/Videos/El Clan Escena.srt',encoding='utf-8')
                startfile(os.path.normpath("Recursos/Videos/El Clan Escena.mp4"))
            else:
                if button == "El Clan 2":
                    subs = pysrt.open('Recursos/Videos/El Clan Escena 2.srt',encoding='utf-8')
                    startfile(os.path.normpath("Recursos/Videos/El Clan Escena 2.mp4"))
                else:
                    if button == "Nueve Reinas":
                        subs = pysrt.open('Recursos/Videos/Nueve Reinas Escena.srt',encoding='utf-8')
                        startfile(os.path.normpath("Recursos/Videos/Nueve Reinas Escena.mp4"))
        mensajes = []
        app.setMeter("NivelSeguridad", 0, text="Analizando...")
        app.updateListBox("mensajesEscena", mensajes, select=False)
        for sub in subs: 
            timeStart = None
            timeStart = datetime.strptime(str(sub.start),'%H:%M:%S,%f')
            app.after(int(timeStart.hour*3600000 + timeStart.minute*60000+ timeStart.second*1000+timeStart.microsecond*0.001), enviarMensaje, str(sub.text))      
            app.after(int(timeStart.hour*3600000 + timeStart.minute*60000+ timeStart.second*1000+timeStart.microsecond*0.001), mostrarSub, str(sub.text))      
        app.lastFrame("MENU")   

def botonesEscena(button):
    global mensajes
    global entidadesASolapar
    global entidadesAAnalizar
    global t
    if button == "Cancelar":
        mensajes = []
        entidadesASolapar = []
        entidadesEnEspera = []
        entidadesAAnalizar = []
        t = Timer(0, None)
        app.setMeter("NivelSeguridad", 0, text="Analizando...")
        app.updateListBox("mensajesEscena", mensajes, select=False)
        app.prevFrame("MENU")

def enviarMensaje(msj):
    global mensajes
    mensajes.insert(0, "")    
    mensajes.insert(0,"+ "+datetime.now().strftime('%H:%M:%S')+"    "+msj) 
    mensajes.insert(0,seguridadCiudadana(msj))     
    app.updateListBox("mensajes", mensajes, select=False)
    app.updateListBox("mensajesEscena", mensajes, select=False)

def mostrarSub(msj):
    app.setLabel("Subtitulo", msj)

    
#INTERFAZ

app = gui("Seguridad ciudadana", "900x400")
app.startFrameStack("MENU")

#MENU PRINCIPAL
app.startFrame("MENU")
app.setStartFrame("MENU", 0)
app.setBg("gray")
app.setPadding([40,20]) 
app.setButtonFont(16)
app.startFrame("TITULOMENU")
app.addLabel("tituloMenu", "Seguridad ciudadana", 0, 1)
app.setLabelFg("tituloMenu", "black")
app.setLabelFont("tituloMenu", size=18, weight="bold")
app.addImage("placaImagenChat1", "Recursos/Imagenes/placa.gif",  0, 0)
app.addImage("placaImagenChat2", "Recursos/Imagenes/placa.gif",  0, 2)
app.stopFrame()
app.addButton("Chat", botonesMenu, 1)
app.addButton("Demo en vivo", botonesMenu,2)
app.stopFrame()

#CHAT
app.startFrame("CHAT")
app.setBg("gray")
app.setPadding([20,5])
#Titulo
app.startFrame("TITULOCHAT")
app.addLabel("tituloChat", "Chat interactivo", 0, 1)
app.setLabelFg("tituloChat", "black")
app.setLabelFont("tituloChat", size=18, weight="bold")
app.addImage("chatImagenChat1", "Recursos/Imagenes/chat.gif",  0, 0)
app.addImage("chatImagenChat2", "Recursos/Imagenes/chat.gif",  0, 2)
app.stopFrame()
#Lista de mensajes
app.startFrame("LOGS")
app.setStretch('both')
app.setSticky('news')
app.addListBox("mensajes", mensajes, 0,0,2)
app.setStretch('row')
app.stopFrame()
#Ingreso de texto
app.addLabelEntry("Mensaje")
#Botones
app.addButtons(["Volver", "Enviar"], botonesChat)
app.stopFrame()

#MENU DEMO EN VIVO
app.startFrame("DEMOMENU")
app.setBg("gray")
app.setPadding([20,20])
app.startFrame("TITULODEMO")
app.addLabel("tituloDemo", "Seleccione una escena",0,1)
app.setLabelFg("tituloDemo", "black")
app.setLabelFont("tituloDemo", size=18, weight="bold")
app.addImage("videoImagenDemo1", "Recursos/Imagenes/video.gif",  0, 0)
app.addImage("videoImagenDemo2", "Recursos/Imagenes/video.gif",  0, 2)
app.stopFrame()
app.startFrame("BOTONESDEMO")
app.addButton("Apache", botonesDemo, 0, 0)
app.addButton("El Clan", botonesDemo, 0, 1)
app.addButton("El Clan 2", botonesDemo, 1, 0)
app.addButton("Nueve Reinas", botonesDemo, 1, 1)
app.stopFrame()
app.addButton("Atras", botonesDemo)
app.stopFrame()

#ESCENA
app.startFrame("ESCENA")
app.setPadding([20,5])
app.setBg("gray")
app.startFrame("LOGSESCENA")
app.setStretch('both')
app.setSticky('news')
app.addListBox("mensajesEscena", mensajes, 0,0,2)
app.setStretch('row')
app.stopFrame()
app.addMeter("NivelSeguridad")
app.setMeterFill("NivelSeguridad", "red")
app.setMeterBg("NivelSeguridad", "LightGreen")
app.addLabel("Subtitulo", "")
app.setLabelBg("Subtitulo","Cornsilk")
app.addButton("Cancelar", botonesEscena)
app.stopFrame()

app.stopFrameStack()

# al presionar enter se envia el mensaje
app.enableEnter(botonesChat)

# start the GUI
app.go()