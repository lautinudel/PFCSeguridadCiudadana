import spacy
from pathlib import Path
import unidecode
from appJar import gui
from threading import Timer
from datetime import datetime
import pysrt
import os
from os import startfile
    
class Chat(object):
    app = gui("Seguridad ciudadana", "1000x400")
    def __init__(self):
        super(Chat, self).__init__()
        self.iniciarInterfaz()
        pass

    def iniciarInterfaz(self):
        self.app.startFrameStack("MENU")
        self.app.startFrame("MENU")
        self.app.setStartFrame("MENU", 0)
        self.app.setBg("gray")
        self.app.setPadding([40,20]) 
        self.app.setButtonFont(16)
        self.app.startFrame("TITULOMENU")
        self.app.addLabel("tituloMenu", "Seguridad ciudadana", 0, 1)
        self.app.setLabelFg("tituloMenu", "black")
        self.app.setLabelFont("tituloMenu", size=18, weight="bold")
        self.app.addImage("placaImagenChat1", "Recursos/Imagenes/placa.gif",  0, 0)
        self.app.addImage("placaImagenChat2", "Recursos/Imagenes/placa.gif",  0, 2)
        self.app.stopFrame()
        self.app.addButton("Chat", SeguridadCiudadana.botonesMenu, 1)
        self.app.addButton("Demo en vivo", SeguridadCiudadana.botonesMenu,2)
        self.app.stopFrame()

        self.app.startFrame("CHAT")
        self.app.setBg("gray")
        self.app.setPadding([20,5])

        self.app.startFrame("TITULOCHAT")
        self.app.addLabel("tituloChat", "Chat interactivo", 0, 1)
        self.app.setLabelFg("tituloChat", "black")
        self.app.setLabelFont("tituloChat", size=18, weight="bold")
        self.app.addImage("chatImagenChat1", "Recursos/Imagenes/chat.gif",  0, 0)
        self.app.addImage("chatImagenChat2", "Recursos/Imagenes/chat.gif",  0, 2)
        self.app.stopFrame()

        self.app.startFrame("LOGS")
        self.app.setStretch('both')
        self.app.setSticky('news')
        self.app.addListBox("mensajes", SeguridadCiudadana.mensajes, 0,0,2)
        self.app.setStretch('row')
        self.app.stopFrame()

        self.app.addLabelEntry("Mensaje")

        self.app.addButtons(["Volver", "Enviar"], SeguridadCiudadana.botonesChat)
        self.app.stopFrame()

        self.app.startFrame("DEMOMENU")
        self.app.setBg("gray")
        self.app.setPadding([20,20])
        self.app.startFrame("TITULODEMO")
        self.app.addLabel("tituloDemo", "Seleccione una escena",0,1)
        self.app.setLabelFg("tituloDemo", "black")
        self.app.setLabelFont("tituloDemo", size=18, weight="bold")
        self.app.addImage("videoImagenDemo1", "Recursos/Imagenes/video.gif",  0, 0)
        self.app.addImage("videoImagenDemo2", "Recursos/Imagenes/video.gif",  0, 2)
        self.app.stopFrame()
        self.app.startFrame("BOTONESDEMO")
        self.app.addButton("Robo y asesinato", SeguridadCiudadana.botonesDemoEnVivo, 0, 0)
        self.app.addButton("Secuestro", SeguridadCiudadana.botonesDemoEnVivo, 0, 1)
        self.app.addButton("Situacion normal", SeguridadCiudadana.botonesDemoEnVivo, 1, 0)
        self.app.addButton("Robo", SeguridadCiudadana.botonesDemoEnVivo, 1, 1)
        self.app.stopFrame()
        self.app.addButton("Atras", SeguridadCiudadana.botonesDemoEnVivo)
        self.app.stopFrame()

        self.app.startFrame("ESCENA")
        self.app.setPadding([20,5])
        self.app.setBg("gray")
        self.app.startFrame("LOGSESCENA")
        self.app.setStretch('both')
        self.app.setSticky('news')
        self.app.addListBox("mensajesEscena", SeguridadCiudadana.mensajes, 0,0,2)
        self.app.setStretch('row')
        self.app.stopFrame()
        self.app.addMeter("NivelSeguridad")
        self.app.setMeterFill("NivelSeguridad", "red")
        self.app.setMeterBg("NivelSeguridad", "LightGreen")
        self.app.addLabel("Subtitulo", "")
        self.app.setLabelBg("Subtitulo","Cornsilk")
        self.app.addButton("Cancelar", SeguridadCiudadana.botonesEscenaElegida)
        self.app.stopFrame()

        self.app.stopFrameStack()
        self.app.enableEnter(SeguridadCiudadana.botonesChat)
        self.app.go()
        pass

class SeguridadCiudadana(object):
    ubicacionNer = "Modelos/NERModel"
    ubicacionTextcat = "Modelos/TEXTCATModel"
    cantidadEntidades = 0
    cantidadEntidadesASolapar = 1
    numeroMaximoEntidades = 4
    timepoEspera = 10
    entidadesASolapar = []
    entidadesEnEspera = []
    entidadesAAnalizar = []
    temporizador = Timer(0, None)
    primerEjecucion = True
    modeloNer = spacy.load(ubicacionNer)
    modeloTextcat = spacy.load(ubicacionTextcat)
    mensajes = []

    def __init__(self, arg):
        super(SeguridadCiudadana, self).__init__()
        self.arg = arg
        pass

    def botonesChat(boton):
        if boton == "Volver":
            Chat.app.firstFrame("MENU")
        else:            
            mensaje = Chat.app.getEntry("Mensaje")
            SeguridadCiudadana.enviarMensaje(mensaje)
            Chat.app.clearEntry("Mensaje", callFunction=True)
        pass

    def botonesMenu(boton):
        SeguridadCiudadana.mensajes = []
        Chat.app.updateListBox("mensajes", SeguridadCiudadana.mensajes, select=False)
        Chat.app.updateListBox("mensajesEscena", SeguridadCiudadana.mensajes, select=False)
        if boton == "Chat": 
            Chat.app.nextFrame("MENU")
            Chat.app.setFocus("Mensaje")
        else: 
            if boton == "Demo en vivo": 
                Chat.app.nextFrame("MENU")
                Chat.app.nextFrame("MENU")
        pass
    
    def botonesDemoEnVivo(boton):
        if boton == "Atras": Chat.app.firstFrame("MENU")
        else: 
            if boton == "Robo y asesinato":
                subtitulos = pysrt.open('Recursos/Videos/Apache Escena.srt',encoding='utf-8')
                startfile(os.path.normpath("Recursos/Videos/Apache Escena.mp4"))
            else:
                if boton == "Secuestro":
                    subtitulos = pysrt.open('Recursos/Videos/El Clan Escena.srt',encoding='utf-8')
                    startfile(os.path.normpath("Recursos/Videos/El Clan Escena.mp4"))
                else:
                    if boton == "Situacion normal":
                        subtitulos = pysrt.open('Recursos/Videos/El Clan Escena 2.srt',encoding='utf-8')
                        startfile(os.path.normpath("Recursos/Videos/El Clan Escena 2.mp4"))
                    else:
                        if boton == "Robo":
                            subtitulos = pysrt.open('Recursos/Videos/Nueve Reinas Escena.srt',encoding='utf-8')
                            startfile(os.path.normpath("Recursos/Videos/Nueve Reinas Escena.mp4"))
            SeguridadCiudadana.mensajes = []
            Chat.app.setMeter("NivelSeguridad", 0, text="Analizando...")
            Chat.app.updateListBox("mensajesEscena", SeguridadCiudadana.mensajes, select=False)
            for subtitulo in subtitulos: 
                tiempoInicio = None
                tiempoInicio = datetime.strptime(str(subtitulo.start),'%H:%M:%S,%f')
                Chat.app.after(int(tiempoInicio.hour*3600000 + tiempoInicio.minute*60000+ tiempoInicio.second*1000+tiempoInicio.microsecond*0.001),  SeguridadCiudadana.enviarMensaje, str(subtitulo.text))      
                Chat.app.after(int(tiempoInicio.hour*3600000 + tiempoInicio.minute*60000+ tiempoInicio.second*1000+tiempoInicio.microsecond*0.001),  SeguridadCiudadana.mostrarSubtitulo, str(subtitulo.text))      
            Chat.app.lastFrame("MENU")
        pass

    def botonesEscenaElegida(boton):
        if boton == "Cancelar":
            SeguridadCiudadana.mensajes = []
            SeguridadCiudadana.entidadesASolapar = []
            SeguridadCiudadana.entidadesEnEspera = []
            SeguridadCiudadana.entidadesAAnalizar = []
            SeguridadCiudadana.temporizador = Timer(0, None)
            Chat.app.setMeter("NivelSeguridad", 0, text="Analizando...")
            Chat.app.updateListBox("mensajesEscena", SeguridadCiudadana.mensajes, select=False)
            Chat.app.prevFrame("MENU")
        pass

    def enviarMensaje(mensaje):
        SeguridadCiudadana.mensajes.insert(0, "")    
        SeguridadCiudadana.mensajes.insert(0,"+ "+datetime.now().strftime('%H:%M:%S')+"    "+mensaje) 
        SeguridadCiudadana.mensajes.insert(0, SeguridadCiudadana.seguridadCiudadana(mensaje))     
        Chat.app.updateListBox("mensajes", SeguridadCiudadana.mensajes, select=False)
        Chat.app.updateListBox("mensajesEscena", SeguridadCiudadana.mensajes, select=False)
        pass

    def mostrarSubtitulo(mensaje):
        Chat.app.setLabel("Subtitulo", mensaje)
        pass

    def aCadenaDeTexto(arreglo):
        resultado = ""
        for i in range(len(arreglo)):
            if i == 0:
                resultado = resultado + arreglo[i]
            else:
                resultado = resultado + ", " + arreglo[i]
        return resultado
        
   
    def detectarEntidades(texto):
        listaEntidades = []
        entidades = SeguridadCiudadana.modeloNer(texto)
        i = 0
        for i in range(len(entidades.ents)):
            entidad = entidades.ents[i].label_
            listaEntidades.append(entidad)
        return listaEntidades

    def detectarNivelDeInseguridad(entidades):
        SeguridadCiudadana.primerEjecucion = False
        entidadesSTR =  SeguridadCiudadana.aCadenaDeTexto(entidades)
        inseguridad = SeguridadCiudadana.modeloTextcat(entidadesSTR)
        probabilidades = [inseguridad.cats['Muy Inseguro'], inseguridad.cats['Inseguro'], inseguridad.cats['Seguro'], inseguridad.cats['Muy Seguro']]
        if inseguridad.cats['Muy Inseguro'] == max(probabilidades):
            categoria = "Muy Insegura"
            Chat.app.setMeter("NivelSeguridad", 100, text="Muy Insegura")       
        else:
            if inseguridad.cats['Inseguro'] == max(probabilidades):
                categoria = "Insegura"
                Chat.app.setMeter("NivelSeguridad", 66, text="Insegura") 
            else:
                if inseguridad.cats['Seguro'] == max(probabilidades):
                    categoria = "Segura"
                    Chat.app.setMeter("NivelSeguridad", 33, text="Segura")
                else: 
                    if inseguridad.cats['Muy Seguro'] == max(probabilidades):
                        categoria = "Muy Segura"
                        Chat.app.setMeter("NivelSeguridad", 1, text="Muy Segura")
        Chat.app.after(8000, Chat.app.setMeter, "NivelSeguridad", 0, "Analizando...")     
        return categoria

    def vencioTiempo():
        SeguridadCiudadana.entidadesASolapar = []
        if (len(SeguridadCiudadana.entidadesEnEspera) > SeguridadCiudadana.cantidadEntidadesASolapar or ( len(SeguridadCiudadana.entidadesEnEspera) > 0 and SeguridadCiudadana.primerEjecucion )):
            SeguridadCiudadana.entidadesAAnalizar = SeguridadCiudadana.entidadesEnEspera
            SeguridadCiudadana.entidadesEnEspera = []
            print("Termine de escuchar porque pasaron mas de "+str(SeguridadCiudadana.timepoEspera)+" seg")
            print("Entidades a analizar: "+ SeguridadCiudadana.aCadenaDeTexto(SeguridadCiudadana.entidadesAAnalizar))
            SeguridadCiudadana.cantidadEntidades = 0
            print("Analizando...")
            SeguridadCiudadana.mensajes.insert(0,"")        
            resultado = SeguridadCiudadana.detectarNivelDeInseguridad(SeguridadCiudadana.entidadesAAnalizar)        
            SeguridadCiudadana.mensajes.insert(0,"- "+datetime.now().strftime('%H:%M:%S')+"    "+"Pasaron mas de " +
                str(SeguridadCiudadana.timepoEspera)+" seg -> LA CONVERSACION FUE: "+resultado)
            print("LA CONVERSACION FUE: "+resultado)
            Chat.app.updateListBox("mensajes", SeguridadCiudadana.mensajes, select=False)
            Chat.app.updateListBox("mensajesEscena", SeguridadCiudadana.mensajes, select=False)
        pass
            
    def seguridadCiudadana(texto):
        print("")
        print("Texto ingresado: " + unidecode.unidecode(texto))

        SeguridadCiudadana.temporizador.cancel()
        SeguridadCiudadana.temporizador = None
        SeguridadCiudadana.temporizador = Timer(SeguridadCiudadana.timepoEspera, SeguridadCiudadana.vencioTiempo)
        SeguridadCiudadana.temporizador.start()

        listaEntidadesAux = SeguridadCiudadana.detectarEntidades(texto)
        SeguridadCiudadana.cantidadEntidades = SeguridadCiudadana.cantidadEntidades + len(listaEntidadesAux)

        print("Entidade/s: "+ SeguridadCiudadana.aCadenaDeTexto(listaEntidadesAux))

        if SeguridadCiudadana.cantidadEntidades >= SeguridadCiudadana.numeroMaximoEntidades: #se supera el limite del arreglo y se manda a analizar el lote de entidades
            deltaEntidades = SeguridadCiudadana.numeroMaximoEntidades-len(SeguridadCiudadana.entidadesEnEspera)
            if deltaEntidades > 0: 
                #si las nuevas entidades superan el limite pero el arreglo de entidades no se lleno todavia
                SeguridadCiudadana.entidadesAAnalizar = SeguridadCiudadana.entidadesEnEspera + listaEntidadesAux[:deltaEntidades] #agrego lo que falta para llenar el arreglo de entidades a analizar
                SeguridadCiudadana.entidadesEnEspera = listaEntidadesAux[deltaEntidades:]  
            else:
                # si las entidades a sumar superan el limite, mando a analizar esas entidades y creo un nuevo arreglo
                SeguridadCiudadana.entidadesAAnalizar = SeguridadCiudadana.entidadesEnEspera
                SeguridadCiudadana.entidadesEnEspera = [] + listaEntidadesAux
            SeguridadCiudadana.entidadesASolapar = SeguridadCiudadana.entidadesAAnalizar[-SeguridadCiudadana.cantidadEntidadesASolapar:]
            SeguridadCiudadana.entidadesEnEspera = SeguridadCiudadana.entidadesASolapar + SeguridadCiudadana.entidadesEnEspera
            print("Termine de escuchar porque se llego al limite de entidades")
            print("Entidades a analizar: "+ SeguridadCiudadana.aCadenaDeTexto(SeguridadCiudadana.entidadesAAnalizar))
            SeguridadCiudadana.cantidadEntidades = len(SeguridadCiudadana.entidadesEnEspera)
            print("Analizando...")
            resultado = SeguridadCiudadana.detectarNivelDeInseguridad(SeguridadCiudadana.entidadesAAnalizar)
            print("LA CONVERSACION FUE: "+resultado)
            return "- "+datetime.now().strftime('%H:%M:%S')+"    "+"Entidad/es: "+ SeguridadCiudadana.aCadenaDeTexto(listaEntidadesAux)+"    "+" => Se llego al limite de entidades -> LA CONVERSACION FUE: "+resultado
        else:
            SeguridadCiudadana.entidadesEnEspera = SeguridadCiudadana.entidadesEnEspera + listaEntidadesAux
            print("Sigo escuchando")
            return "- "+ datetime.now().strftime('%H:%M:%S')+"    "+"Entidad/es: "+ SeguridadCiudadana.aCadenaDeTexto(listaEntidadesAux)

chat = Chat()