# --- Start: IMPORTAR LIBRERIAS --- #
from ctypes import alignment
from timeit import repeat
import tkinter as tk               
from tkinter import BOTH, font as tkfont
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import serial.tools.list_ports
from tkinter.constants import ANCHOR, UNDERLINE  
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)      # OLD:  NavigationToolbar2TkAgg)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as anim     
from tkscrolledframe import ScrolledFrame
import os
import serial.tools.list_ports                                                              # Necesario para tener la lista de puertos disponibles, la transmision de datos se realiza en otro script
import threading                                                                            # Para poder ejecutar Multithread
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import time
import datetime as dt
from PIL import ImageTk, Image
#from scipy.ndimage.filters import uniform_filter1d OLD
from scipy.ndimage import uniform_filter1d
from pathlib import Path                        # Para crear las carpetas
import json                                     # Para procesar archivos JSON
import shutil                                   # Para copiar archivos
import win32com.client                          # Para poder ejecutar las macros de excel
# IMPORTAR LIBRERIAS CUSTOM
import scripts.serialreadtestVdev as serialread  # Libreria custom para leer el serial
# --- End: IMPORTAR LIBRERIAS --- #

# --- Start: DECLARACION DE VARIABLES --- #
    # Programa
versionNr='Py 0.2.3'                            # Version del programa
titleBarText='Tribómetro Pin on Disk'
    # Ventana
defaultGeometry="900x1000"                       # Dimensiones Default
width_acercade_text=600                         # Ancho texto acerca de
width_acercade_window=width_acercade_text+40    # Ancho texto acerca de
minWidth=900,  #300,          # Ancho minimo
minHeight=1000,                                  # Altura minima
    # Graficos
grafWidthInch=9                                 # Ancho de los graficos en pulgadas
grafHeightInch=4                                # Altura de los graficos en pulgadas
grafDPI=100                                     # DPI de los graficos
    # Archivos
calibrationPath = 'C:/MaquinaPOD/Calibracion/'  # Carpeta de arhivos de calibracion
ensayosPath = 'C:/MaquinaPOD/Ensayos/'          # Carpeta de archivos de ensayos
rutaLogoUtn="img/utnlogo.ico"                   # Icono logo UTN
rutaimgMed = "img/MedicionRadio.png"
rutaNormaASTMG99="pdf\ASTM_G99.pdf"             # PDF norma ASTM G99
rutaManualDeUsuario="pdf\ManualDeUsuario.pdf"   # PDF Manual de usuario
rutaInformeXlsm="xslm\Informe_00.xlsm"             # Excel para informe
    # Colores
colorAppBg='#B9B9B9'                            # Color de fondo general de la APP (Gris Medio)
colorPageBg='#FFFFFF'                           # Color de fondo de las paginas (Blanco)
colorUtnFrh='#33b25a'                           # Verde FRH
colorMenuBoton=colorUtnFrh  #'#abdbe3'          # Boton Menu
colorMenuBoton2='#47855b'                       # Boton Menu
colorMenuBoton3='#808080'                       # Boton Menu
colorMenuBotonClicked='#0ac244'                 # Boton Menu Clickeado
colorEntryBoxSelected = "Grey"                  # Color Entry Box selecionado
colorEntryBoxUnselected = colorUtnFrh           # Color Entry Box sin seleccionar
    # Fonts
defaultFontFamily = 'Calibri'
buttonFontMenu = defaultFontFamily+' 18 bold'
buttonFontVolver = defaultFontFamily+' 14 bold'
    # EntryBox
time1 = ''
entryBox_Width = 50                             # Ancho del entryBox
entryBox_BorderWidth = 5                        # Borde del entryBox
    # Textos de msgboxes
msgPuestaACero = 'Poner la celda de carga en cero. Hacer click en aceptar y esperar el próximo mensaje. No tocar la máquina.'
msgEnCarga = 'Aplicar a la celda, una carga conocida. Hacer click en aceptar y esperar el próximo mensaje. No tocar la máquina.'
msgTerminando = 'Adquisición de datos terminada. Complete el valor de la carga aplicada debajo. Luego presione generar archivo.'
msgDatosObtenidos='Adquisición de datos finalizada. Para finalizar, haga click en aceptar y siga la instrucciones.'
msgEnsayoFinalizado='Ensayo finalizado. Los datos y el informe se encuentran en: '
    # Puertos com
SelectedPort=''                                 # Puerto COM seleccionado
    # Variables de ensayo
RPM = ''                                        # RPM Seteadas
DurationSec = ''                                # Duracion de ensayo seteada
   # Ruta Ensayo
RutaEnsayoCarpeta = ''                          # Carpeta de ensayo
RutaEnsayoArchivoRawData = ''                   # Carpeta de ensayo / archivo raw data .csv
RutaEnsayoArchivoCalibracion = ''               # Carpeta de ensayo / archivo calibracion .json
RutaEnsayoArchivoSetup = ''                     # Carpeta de ensayo / archivo setup .json
RutaEnsayoArchivoInforme = ''                   # Carpeta de ensayo / archivo informe .xlsx
    # Otras rutas
RutaArchivoCalibracionSeleccionado = ''         # Ruta del archivo de calibracion seleccionado para el archivo   
# Calibracion
valorEnCero = 0                                 # Valor de celda de carga en cero
valorEnCarga = 0                                # Valor de celda de carga en carga
valorCargaAplicadaN = 0                         # Carga de calibracion aplicada
valorCargaAplicadaKg = 0                        # Carga de calibracion aplicada
calibrationNotas = ''                           # Notas sobre la calibracion
# Fuerzas
Fa1 = 0                                         # Fuerza aplicada 1 (pesas-poleas-vertical)
Fa2 = 0                                         # Fuerza aplicada 2 (directamente sobre el pin)
Fc = 0                                          # Fuerza celda (valor en sentido celda de carga)
Fn = 0                                          # Fuerza normal (composición de Fa1 y Fa2)
Fr =0                                           # Fuerza de rozamiento

L1 = 0.27             # Constante de máquina     # Distancia del apoyo central al punto de aplicacion de Fa1 y Fc
L2 = 0.265             # Constante de máquina     # Distancia del apoyo central al eje de rotación del disco
L3 = 5               # Radio pista de desgaste (ATENCION: importa positivo o negativo)




    # Otros
KgN981 = 9.80665                                # Equivalencia Newton - Kg
lastFileSize = int
getSerialData_thread = threading.Thread
RadioPinDiscoReal = float                       # Valor ingresado por el usuario
redirectPage = ""                               #Pagina a la que se redirige la navegación
Data_Frame = pd.DataFrame()
    # Banderas 
IsRun = False                                   # Bandera 1 
FirstTime = True                               # Bandera 2 
IsOver = False                                  # Bandera 3

todoOk = True
# --- End: DECLARACION DE VARIABLES --- #

# --- Graficos --- #
# Se ubican afuera de la clase porque es mas simple siendo
# globales que para una clase especifica

    # Grafico 1 #
figure1 = Figure(figsize=(grafWidthInch,grafHeightInch), dpi=grafDPI)
a1 = figure1.add_subplot(111)
a1.plot(0.1, 0.1)
    # Grafico 2 #
figure2 = Figure(figsize=(grafWidthInch,grafHeightInch), dpi=grafDPI)
a2 = figure2.add_subplot(111)
a2.plot(0.1, 0.1)
    # Grafico 3 #
figure3 = Figure(figsize=(grafWidthInch,grafHeightInch), dpi=grafDPI)
a3 = figure3.add_subplot(111)
a3.plot(0.1, 0.1)
    # Grafico 4 #
figure4 = Figure(figsize=(grafWidthInch,grafHeightInch), dpi=grafDPI)
a4 = figure4.add_subplot(111)
a4.plot(0.1, 0.1)

# --- Graficos --- #




# --- Funcion para plotear todos los graficos --- #
def draw_chart(i):

    global lastFileSize, RutaEnsayoArchivoCalibracion, RutaEnsayoArchivoSetup

            # --- Verificar archivo --- #
    if (os.path.exists(RutaEnsayoArchivoRawData) == True):                                   # Verificar si existe el archivo.
        lastFileSize = Path(RutaEnsayoArchivoRawData).stat().st_size

        # --- Generar Dataframe --- #
        columns = ['tiempoMs','tempAmbC','tempObjC','vueltas','celdaCarga']         # Columnas a importar   de = ['tiempoMs','tempAmbC','tempObjC','vueltas','celdaCarga']
        df = pd.read_csv(RutaEnsayoArchivoRawData, usecols=columns)                         # Data Frame del CSV                

        # --- Start: Calcular CoF --- #
            # Obtener valores del Archivo calibracion #
        f = open(RutaEnsayoArchivoCalibracion)                                      # Opening JSON file
        data = json.load(f)                                                         # returns JSON object as a dictionary
        CalibCelda_enCero = data['ValorEnCero']                                     # Valor de la celda de carga en cero                                         
        ConstanteCeldaKg = data['ConstanteEnKg']                                    # Constante de la celda de carga en Kg
        f.close()                                                                   # Cerrar archivos
            # -- #                         # Closing file
            # Obtener valores del Archivo setup #
        f = open(RutaEnsayoArchivoSetup)                                            # Opening JSON file
        data = json.load(f)                                                         # returns JSON object as a dictionary
        CargaDeEnsayoEnKg = data['CargaKg']                                         # Carga del ensayo, en Kg
        CargaDeEnsayoEnKgDirecta = data['CargaKgDirecta']                                         # Carga del ensayo, en Kg
        if 'RadioDiscoPistaMMReal' in data:
            print('existe el real, wacho!')
            L3 = float(data['RadioDiscoPistaMMReal']) / 1000
        else:
            L3 = float(data['RadioDiscoPistaMMEstimado']) / 1000
        #    print('no existe el real, wacho!')
        radioPistaDisco = float(data['RadioDiscoPistaMMEstimado']) / 1000                      # Divido valor REAL por 1000 para pasar a metros  
        f.close()                                                                   # Cerrar archivos
                # -- #                               # Closing file
        # - Calculo de CoF - #
        # OLD COF: Without L1, L2, L3    cof = (( df['celdaCarga'] - float(CalibCelda_enCero) ) / float(ConstanteCeldaKg)) / float(CargaDeEnsayoEnKg)                                # Cof
                           
        Fc = (df['celdaCarga'] - float(CalibCelda_enCero) ) / float(ConstanteCeldaKg)
        Fa1 = float(CargaDeEnsayoEnKg)
        Fa2 = float(CargaDeEnsayoEnKgDirecta)

        Fn = Fa2 + Fa1*(L1/(L2+L3))
        Fr = Fc * (L1/(L2+L3))
        cof = Fr / Fn 
        # --- End: Calcular CoF --- #

            # --- Grafico N-E --- #   
        x1 = df['tiempoMs'].to_numpy() / 1000
        y1 = cof.to_numpy()
            # --- Grafico N-W --- #
        x2 = df['vueltas'].to_numpy() * np.pi * 2 * radioPistaDisco
        y2 = cof.to_numpy()
            # --- Grafico S-E --- #
        x3 = df['tiempoMs'].to_numpy() / 1000
        y3 = df['tempObjC'].to_numpy()
            # --- Grafico S-W --- #
            # - Start: Determinar valores a plotear - #
        lastVuelta= 0                                                               
        lastTimeMs= 0
        tiempoArray=[]                                                              # Array de tiempo a plotear
        rpmArray=[]                                                                 # Array de rpm a plotear

        for i,row in df.iterrows():                                                # Loopear filas
            vuelta = row["vueltas"]                                                 # Valor de vueltas totales en esa fila 
            if vuelta != lastVuelta:                                                # Si el valor cambio (respecto de la fila anterior)
                timeMs = row["tiempoMs"]                                                # Valor de Ms de esa fila
                rpm = ((vuelta - lastVuelta)*60000)/(timeMs - lastTimeMs)               # Definir RPM como Delta Vueltas sobre Delta T * 60000 (para pasar de ms a rpm)
                lastVuelta = vuelta                                                     # Setear nuevo valor de vuelta anterior
                lastTimeMs = timeMs                                                     # Setear nuevo valor de tiempo anterior
                tiempoArray.append(timeMs)                                              # Agregar valor de tiempo a Array a plotear
                rpmArray.append(rpm)                                                    # Agregar valor de rpm a Array a plotear
                #print (timeMs, vuelta,rpm)                                              # Para debuggear


        x4 = [xx / 1000 for xx in tiempoArray]                                       # Eje X -> Pasar de Ms a s
        y4 = uniform_filter1d(rpmArray, size=15)                                     # Eje Y -> Media movil de los valores. Para mas info ver:    https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
           # - End: Determinar valores a plotear - #   

        # --- Start: Ploteo --- #
        a1.clear()
        a2.clear()
        a3.clear()
        a4.clear()
        # --- Grafico N-E --- #
        a1.set_title('Friction Graph')                                                   # Titulo
        a1.set_xlabel('Time [s]')                                                   # Etiqueta Eje X
        a1.set_ylabel('Coefficient of friction')                                    # Etiqueta Eje Y
        a1.set_xlim([0,int(DurationSec)])                                           # Limites Eje X, desde 0 hasta la duracion del ensayo       
        a1.plot(x1, y1, 'r')
        # --- Grafico N-W --- #
        a2.set_title('RPM Graph')                                                   # Titulo
        a2.set_xlabel('Sliding distance [m]')                                                   # Etiqueta Eje X
        a2.set_ylabel('Coefficient of friction')                                    # Etiqueta Eje Y
        a2.set_xlim([0,(int(RPM)/60)*int(DurationSec)* np.pi * 2 * radioPistaDisco])# Limites Eje X, desde 0 hasta la duracion del ensayo (calculada en distancia)
        a2.plot(x2, y2, 'b')
        # --- Grafico S-E --- #
        a3.set_title('Contact zone Temperature')      
        a3.set_ylabel('Temperature [°C]')
        a3.set_xlabel('Time [s]')
        a3.set_xlim([0,int(DurationSec)])                                           # Limites Eje X, desde 0 hasta la duracion del ensayo       
        a3.plot(x3, y3, 'k')
        # --- Grafico S-W --- #
        a4.set_title('Axis rotational speed control')
        a4.set_xlabel('Time [s]')
        a4.set_ylabel('RPM')
        a4.set_xlim([0,int(DurationSec)])                                           # Limites Eje X, desde 0 hasta la duracion del ensayo
        #a4.set_yticks(list(range(0,int(y4.max()*1.2),50)))                            # Divisiones Eje Y                       
        a4.plot(x4, y4, 'green')
    else:
        a1.plot(0.1, 0.1)
        a2.plot(0.1, 0.1)
        a3.plot(0.1, 0.1)
        a4.plot(0.1, 0.1)






# CLASES


class CurrentTimeClock(tk.Label):
    def __init__(self, parent, *args, **kwargs):
        tk.Label.__init__(self, parent, *args, **kwargs)
        self.lastTime = ""
        t = time.localtime()
        self.zeroTime = dt.timedelta(hours=t[3], minutes=t[4], seconds=t[5])
        self.tick()
 
    def tick(self):
        # get the current local time from the PC
        now = dt.datetime(1, 1, 1).now()
        elapsedTime = now  # = now - self.zeroTime
        time2 = elapsedTime.strftime("%Y-%m-%d_%H-%M-%S")  #("%Y-%m-%d, %H-%M-%S")
        # if time string has changed, update it
        if time2 != self.lastTime:
            self.lastTime = time2
            self.config(text=time2)
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.after(200, self.tick)


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)


        # Configuracion de FONTS para usar en Labels
        self.font_title = tkfont.Font(family=defaultFontFamily, size=18, weight="bold", slant="italic")
        self.font_subtitle = tkfont.Font(family=defaultFontFamily, size=14, weight="bold")
        self.font_subtitle2 = tkfont.Font(family=defaultFontFamily, size=14)
        self.font_title_acercade = tkfont.Font(family=defaultFontFamily, size=18, weight="bold")
        self.font_text_acercade = tkfont.Font(family=defaultFontFamily, size=12, weight="normal")
        font_barrasuperior = tkfont.Font(family=defaultFontFamily, size=20, weight="bold")
        font_barrainferior = tkfont.Font(family=defaultFontFamily, size=10, weight="bold")



        # the container is where we'll stack a bunch of frames on top of each other, then the one we want visible will be raised above the others

        
        # Etiqueta barra superior
        etiqueta = tk.Label(self,                          
                            text="Tribómetro Pin On Disk",
                            font=font_barrasuperior,        # Fuente
                            anchor="w",                     # Central al Oeste (LEFT)
                            width=30,                       # Alto del botón en lineas de texto
                            height=1,                       # Alto del botón en caracteres
                            padx=5,                         # Horizontal padding
                            pady=5,                         # Vertical padding
                            bg=colorUtnFrh,                 #'#rrggbb' Background color normal
                            fg='#FFFFFF',
                             )
        etiqueta.pack(side="top", anchor="n", fill="x") #, pady=10)
        

        # Etiqueta barra inferior
        etiquetaBarraInferior = tk.Label(self,                          
                            text="Version: "+versionNr,
                            font=font_barrainferior,        # Fuente
                            anchor="e",                     # Central al Oeste (LEFT)
                            width=30,                       # Alto del botón en lineas de texto
                            height=1,                       # Alto del botón en caracteres
                            padx=5,                         # Horizontal padding
                            pady=5,                         # Vertical padding
                            bg=colorUtnFrh,                 #'#rrggbb' Background color normal
                            fg='#FFFFFF',
                             )
        etiquetaBarraInferior.pack(side="bottom", anchor="s", fill="x") #, pady=10)

        
        # Frames (Paginas) del medio
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)


        # Frames 
        self.frames = {}
        for F in (PageMenuPrincipal, 
                  PageConnection, 
                  PageNuevoEnsayo, 
                  PageEnsayoRunning, 
                  PageCalibrarMaquina, 
                  PageAcercaDe, 
                  PagePinDiskRadius):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("PageMenuPrincipal")
        #self.show_frame("PagePinDiskRadius")
       

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        

class PageMenuPrincipal(tk.Frame):


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        global redirectPage
        # Frame Setup
        self.config(bg=colorPageBg)                   # Background color
    
        
        # -- Botones -- #

        # Frame para espaciar botones
        frameEspacio0 = tk.Frame(self, bg=colorPageBg)
        frameEspacio0.pack(expand=True, fill=tk.BOTH)
        
        # Boton Nuevo ensayo
        botonNuevoEnsayo = tk.Button(self,
                          text="Nuevo ensayo",                                              #
                          font=buttonFontMenu,                                              # Configuracion de la fuente
                          fg='white',                                                       # Color de la fuente
                          command=lambda: CheckAndGoToNuevoEnsayo(),                  # 
                          bg=colorMenuBoton,                                                #'#rrggbb' Background color normal
                          activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                          cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                          width=40,                                                         # Ancho del boton en caracteres
                          )
        botonNuevoEnsayo.pack(expand=True, fill=tk.Y)                                       # Expandir a lo alto
        
        def CheckAndGoToNuevoEnsayo():
            global redirectPage
            redirectPage = "PageNuevoEnsayo"
            CheckConnectionAndRedirect(controller)
        

        # Frame para espaciar botones
        frameEspacio1 = tk.Frame(self, bg=colorPageBg)
        frameEspacio1.pack(expand=True, fill=tk.BOTH)

        # Boton Calibrar Maquina
        botonCalibrarMaquina = tk.Button(self,
                          text="Calibrar máquina",                                          #
                          font=buttonFontMenu,                                              # Configuracion de la fuente
                          fg='white',                                                       # Color de la fuente
                          command=lambda: CheckAndGoToCalibrarMaquina(),   #controller.show_frame("PageCalibrarMaquina"),     #
                          bg=colorMenuBoton,                                                #'#rrggbb' Background color normal
                          activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                          cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                          width=40,                                                         # Ancho del boton en caracteres
                          )
        botonCalibrarMaquina.pack(expand=True, fill=tk.Y)                                   # Expandir a lo alto
                
        def CheckAndGoToCalibrarMaquina():
            global redirectPage
            redirectPage = "PageCalibrarMaquina"
            CheckConnectionAndRedirect(controller)
        

        
        # Frame para espaciar botones
        frameEspacio2 = tk.Frame(self, bg=colorPageBg)            
        frameEspacio2.pack(expand=True, fill=tk.BOTH)
        
        # Boton Manual de usuario
        buttonAbrirManual = tk.Button(self,
                          text="Manual de usuario",                                         #
                          font=buttonFontMenu,                                              # Configuracion de la fuente
                          fg='white',                                                       # Color de la fuente
                          command=lambda: os.startfile(rutaManualDeUsuario),                #
                          bg=colorMenuBoton3,                                                #'#rrggbb' Background color normal
                          activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                          cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                          width=40,                                                         # Ancho del boton en caracteres
                          )
        buttonAbrirManual.pack(expand=True, fill=tk.Y)                                      # Expandir a lo alto
        
        # Frame para espaciar botones
        frameEspacio3 = tk.Frame(self, bg=colorPageBg)            
        frameEspacio3.pack(expand=True, fill=tk.BOTH)

        # Boton Abrir Norma
        buttonAbrirNorma = tk.Button(self,
                          text="Norma ASTM G99",                                              #
                          font=buttonFontMenu,                                              # Configuracion de la fuente
                          fg='white',                                                       # Color de la fuente
                          command=lambda: os.startfile(rutaNormaASTMG99),                   #
                          bg=colorMenuBoton3,                                                #'#rrggbb' Background color normal
                          activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                          cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                          width=40,                                                         # Ancho del boton en caracteres
                          )
        buttonAbrirNorma.pack(expand=True, fill=tk.Y)                                      # Expandir a lo alto
        
        # Frame para espaciar botones
        frameEspacio4 = tk.Frame(self, bg=colorPageBg)            
        frameEspacio4.pack(expand=True, fill=tk.BOTH)

        # Boton Acerca De
        botonAcercaDe = tk.Button(self,
                          text="Acerca de",                                                 #
                          font=buttonFontMenu,                                              # Configuracion de la fuente
                          fg='white',                                                       # Color de la fuente
                          command=lambda: controller.show_frame("PageAcercaDe"),            #
                          bg=colorMenuBoton3,                                                #'#rrggbb' Background color normal
                          activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                          cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                          width=40,                                                         # Ancho del boton en caracteres
                          )
        botonAcercaDe.pack(expand=True, fill=tk.Y)                                          # Expandir a lo alto

        # Frame para espaciar botones
        frameEspacio5 = tk.Frame(self, bg=colorPageBg)                                         
        frameEspacio5.pack(expand=True, fill=tk.BOTH)



# Funciones para obtener lista serial



  
def CheckConnectionAndRedirect(controller):

    global redirectPage

    if serialread.isSerialConnected() == True:
        
        controller.show_frame(redirectPage)
        print(redirectPage)
        # print('connected')
    else:
        controller.show_frame("PageConnection")        # Show connection page
        # print('disconnected')


def setConnectionAndShowMessagebox(SelectedPort, controller=None, NextPageOk=None):

    serialread.connectSerial(SelectedPort)                              # Conectar al puerto deseado
    
    if serialread.isSerialConnected() == True:                          # Checkear conexion
        
        tk.messagebox.showinfo("Conexion", "Máquina POD Conectada")     # Mostrar messagebox maquina conectada

        try: controller.show_frame(NextPageOk)
        except: print('NextPage Error')
        
        # print('connected')
    else:
        tk.messagebox.showwarning("Conexion", "Máquina desconectada")   # Mostrar messagebox con errores
        # print('disconnected')


            
# - isNumeric no me sirve con los decimales (Ej: conversion Kg N) - #
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
        

class PageConnection(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        global redirectPage


        # - Título - #
        frameLabelTitle = tk.Frame(self,
                               width=width_acercade_window-24,
                               height=50,
                               bg=colorPageBg,
                               )
        frameLabelTitle.pack_propagate(False)
        frameLabelTitle.pack()

        labelTitle = tk.Label(frameLabelTitle, text="Conectar máquina", font=controller.font_title, bg='white')
        labelTitle.pack(side="top", fill="x", pady=10)

        
         # Funcion para setear la variable global de puerto conectado
        def set_port(_):                                   
            global SelectedPort             
            SelectedPort = comboBoxPuertoCOM.get()                                  # Obtener valor de la lista de puertos COM
            SelectedPort = SelectedPort.partition(' ')[0]                                   # Formatear para quedarse solo con la parimera parte Ej: "COM5 - USB-Serial-blablabla"  -> "COM5"
            # print(Port)                                                   # Para debugear

        # Lista de puertos com
        comlist = serial.tools.list_ports.comports()                        # Obtener lista de puertos COM
      
        # Combobox con lista de puertos COM
        frameComboBoxPuertoCOM = tk.Frame(self,
                               width=width_acercade_window-24,
                               height=50,
                               bg=colorPageBg,
                               )
        frameComboBoxPuertoCOM.pack_propagate(False)
        frameComboBoxPuertoCOM.pack()

        comboBoxPuertoCOM = ttk.Combobox(frameComboBoxPuertoCOM, values=comlist, font=buttonFontVolver, width=50)             # Cargar valores en el combobox 
        comboBoxPuertoCOM.bind("<<ComboboxSelected>>", set_port)           # Llamar la funcion para setear puerto
        comboBoxPuertoCOM.pack()                                           # Pack 


        # - Start: Boton Conectar Máquina - 
        frameBotonConectarMaquina = tk.Frame(self,
                               width=width_acercade_window-24,
                               height=50,
                               bg=colorPageBg,
                               )
        frameBotonConectarMaquina.pack_propagate(False)
        frameBotonConectarMaquina.pack()

        botonConectarMaquina = tk.Button(frameBotonConectarMaquina,
                                text="Conectar máquina",
                                font=buttonFontVolver,
                                fg='white',
                                command=lambda:setConnectionAndShowMessagebox(SelectedPort, controller, redirectPage),
                                bg=colorMenuBoton,                                         #
                                activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                                cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                                height=40,
                                width=30
                                )
        botonConectarMaquina.pack(pady=5)
        # - End: Boton Conectar Máquina - 


        # - Start: Boton Volver - 
        frameVolverAlMenu = tk.Frame(self,
                               width=width_acercade_window-24,
                               height=50,
                               bg=colorPageBg,
                               )
        frameVolverAlMenu.pack_propagate(False)
        frameVolverAlMenu.pack()

        buttonVolver = tk.Button(frameVolverAlMenu,
                                text="Volver al menú",
                                font=buttonFontVolver,
                                fg='white',
                                command=lambda: controller.show_frame("PageMenuPrincipal"),
                                bg=colorMenuBoton3,                                         #
                                activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                                cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                                height=40,
                                width=30
                                )
        buttonVolver.pack(pady=5)
        # - End: Boton Volver - 



class PageNuevoEnsayo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        #RPM = "000700"         #OLD: Fija
        def updateRPM(self):        # Funcion para convertir Int en Str formato "XXXXXX" Ej: 700 a "000700"
            global RPM
            EntryRPM = RPM_EntryBox.get()
            limit = 6-len(EntryRPM)
            RPM = ''
            for i in range(0,limit):
                RPM = RPM + "0"
            RPM = RPM + EntryRPM

        #DurationSec = "000150"         #OLD: Fija
        def updateDuracion(self):        # Funcion para convertir Int en Str formato "XXXXXX" Ej: 700 a "000700"
            global DurationSec
            EntryDurationSec = Duracion_EntryBox.get()
            limit = 6-len(EntryDurationSec)
            DurationSec = ''
            for i in range(0,limit):
                DurationSec = DurationSec + "0"
            DurationSec = DurationSec + EntryDurationSec


        # Para centrar, se usa el Wight excepto en el contenido que se autodefine
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)

        # - Titulo - #
        Title_Label = tk.Label(self, text="Nuevo ensayo", font=controller.font_title)
        Title_Label.grid(row=1,column=1, pady=5, sticky="nsew")
        
        # - SubTitulo 1 - #
        SubTitle_Label = tk.Label(self, text="Informacion del ensayo", font=controller.font_subtitle)
        SubTitle_Label.grid(row=10,column=1, pady=5, sticky="nsew")

        # Campos de informacion del ensayo
                # Ensayo Fecha y Hora
        EnsayoFechaYHora_Label = tk.Label(self, text="Fecha y Hora", font=controller.font_subtitle2)
        EnsayoFechaYHora_Label.grid(row=11,column=1, sticky="nsew")
        EnsayoFechaYHora_EntryBox = CurrentTimeClock(self)  #CurrentTimeClock(self, font=('times', 20, 'bold'), bg='green')
        EnsayoFechaYHora_EntryBox.grid(row=11,column=2, sticky="nsew")
                # Codigo de Ensayo
        EnsayoCod_Label = tk.Label(self, text="Código de Ensayo", font=controller.font_subtitle2)
        EnsayoCod_Label.grid(row=12,column=1, sticky="nsew")
        EnsayoCod_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
        EnsayoCod_EntryBox.grid(row=12,column=2, sticky="nsew")
                # Proyecto
        Proyecto_Label = tk.Label(self, text="Proyecto", font=controller.font_subtitle2)
        Proyecto_Label.grid(row=13,column=1, sticky="nsew")
        Proyecto_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
        Proyecto_EntryBox.grid(row=13,column=2, sticky="nsew")
                # Par Tribologico
        ParTribologico_Label = tk.Label(self, text="Par Tribológico", font=controller.font_subtitle2)
        ParTribologico_Label.grid(row=14,column=1, sticky="nsew")
        ParTribologico_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
        ParTribologico_EntryBox.grid(row=14,column=2, sticky="nsew")
                # Responsable del ensayo
        Responsable_Label = tk.Label(self, text="Responsable", font=controller.font_subtitle2)
        Responsable_Label.grid(row=15,column=1, sticky="nsew")
        Responsable_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
        Responsable_EntryBox.grid(row=15,column=2, sticky="nsew")
                # Observaciones
        Observaciones_Label = tk.Label(self, text="Observaciones", font=controller.font_subtitle2)
        Observaciones_Label.grid(row=16,column=1, sticky="nsew")
        Observaciones_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
        Observaciones_EntryBox.grid(row=16,column=2, sticky="nsew")
        
        # - SubTitulo 2 - #
        SubTitle2_Label = tk.Label(self, text="Configuracion del ensayo", font=controller.font_subtitle)
        SubTitle2_Label.grid(row=20,column=1, pady=5, sticky="nsew")
        
        # Campos de configuracion del ensayo
                # Duracion
        Duracion_Label = tk.Label(self, text="Duracion [s]", font=controller.font_subtitle2)
        Duracion_Label.grid(row=21,column=1, sticky="nsew")
        Duracion_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
        Duracion_EntryBox.bind('<KeyRelease>', updateDuracion)
        Duracion_EntryBox.grid(row=21,column=2, sticky="nsew")
                # RPM
        RPM_Label = tk.Label(self, text="RPM", font=controller.font_subtitle2)
        RPM_Label.grid(row=22,column=1, sticky="nsew")
        RPM_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
        RPM_EntryBox.bind('<KeyRelease>', updateRPM)
        RPM_EntryBox.grid(row=22,column=2, sticky="nsew")

                # Carga aplicada Kg
        CargaAplicadaKg_Label = tk.Label(self, text="Carga aplicada [Kg]", font=controller.font_subtitle2)
        CargaAplicadaKg_Label.grid(row=23,column=1, sticky="nsew")
        CargaAplicadaKg_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
        
        def updateCargaAplicadaN(self):
            CargaAplicadaN_EntryBox.delete(0, tk.END)                        # Borrar todo lo previo
            ValueToUpdateN = float(CargaAplicadaKg_EntryBox.get()) * KgN981  # Calcular nuevo valor
            CargaAplicadaN_EntryBox.insert(0, ValueToUpdateN)                # Actualizar valor
        
        CargaAplicadaKg_EntryBox.bind('<KeyRelease>', updateCargaAplicadaN)
        CargaAplicadaKg_EntryBox.grid(row=23,column=2, sticky="nsew")
                
                # Carga aplicada N
        CargaAplicadaN_Label = tk.Label(self, text="Carga aplicada [N]", font=controller.font_subtitle2)
        CargaAplicadaN_Label.grid(row=24,column=1, sticky="nsew")
        CargaAplicadaN_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
        
        def updateCargaAplicadaKg(self):
            CargaAplicadaKg_EntryBox.delete(0, tk.END)                        # Borrar todo lo previo
            ValueToUpdateKg = float(CargaAplicadaN_EntryBox.get()) / KgN981  # Calcular nuevo valor
            CargaAplicadaKg_EntryBox.insert(0, ValueToUpdateKg)                # Actualizar valor
        
        CargaAplicadaN_EntryBox.bind('<KeyRelease>', updateCargaAplicadaKg)
        CargaAplicadaN_EntryBox.grid(row=24,column=2, sticky="nsew")



                # Carga aplicada Kg Directa (sobre el pin)
        CargaAplicadaKgDirecta_Label = tk.Label(self, text="Carga aplicada [Kg] Directa (sobre pin)", font=controller.font_subtitle2)
        CargaAplicadaKgDirecta_Label.grid(row=25,column=1, sticky="nsew")
        CargaAplicadaKgDirecta_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
        
        def updateCargaAplicadaNDirecta(self):
            CargaAplicadaNDirecta_EntryBox.delete(0, tk.END)                        # Borrar todo lo previo
            ValueToUpdateNDirecta = float(CargaAplicadaKgDirecta_EntryBox.get()) * KgN981  # Calcular nuevo valor
            CargaAplicadaNDirecta_EntryBox.insert(0, ValueToUpdateNDirecta)                # Actualizar valor
        
        CargaAplicadaKgDirecta_EntryBox.bind('<KeyRelease>', updateCargaAplicadaNDirecta)
        CargaAplicadaKgDirecta_EntryBox.grid(row=25,column=2, sticky="nsew")
               
                # Carga aplicada N Directa (sobre el pin)
        CargaAplicadaNDirecta_Label = tk.Label(self, text="Carga aplicada [N] Directa (sobre pin)", font=controller.font_subtitle2)
        CargaAplicadaNDirecta_Label.grid(row=26,column=1, sticky="nsew")
        CargaAplicadaNDirecta_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle) 
       
        def updateCargaAplicadaKgDirecta(self):
            CargaAplicadaKgDirecta_EntryBox.delete(0, tk.END)                        # Borrar todo lo previo
            ValueToUpdateKgDirecta = float(CargaAplicadaNDirecta_EntryBox.get()) / KgN981  # Calcular nuevo valor
            CargaAplicadaKgDirecta_EntryBox.insert(0, ValueToUpdateKgDirecta)                # Actualizar valor
        
        CargaAplicadaNDirecta_EntryBox.bind('<KeyRelease>', updateCargaAplicadaKgDirecta)
        CargaAplicadaNDirecta_EntryBox.grid(row=26,column=2, sticky="nsew")



                # Radio Disco-Pista
        RadioDiscoPista_Label = tk.Label(self, text="Radio disco-pista EST. [mm]", font=controller.font_subtitle2)
        RadioDiscoPista_Label.grid(row=27,column=1, sticky="nsew")
        RadioDiscoPista_EntryBox = tk.Entry(self, width=entryBox_Width, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected, font=controller.font_subtitle2) 
        RadioDiscoPista_EntryBox.grid(row=27,column=2, sticky="nsew")
      
                # Calibration file
        def SetCalibrationFilePath():
            global RutaArchivoCalibracionSeleccionado
            if os.path.exists(calibrationPath) == False: Path(calibrationPath).mkdir(parents=True)      # Crear carpeta si no existe
            RutaArchivoCalibracionSeleccionado = filedialog.askopenfilename(initialdir=calibrationPath,  filetypes=[("Json File", "*.json")]) #abre el explorador de archivos y guarda la seleccion en la variable!



        # Boton Seleccionar Archivo de Calibracion
        botonCalibrationFile = tk.Button(self,
                          text="Seleccionar archivo de calibración",
                          #command=lambda: controller.show_frame("PageEnsayoRunning"),
                          command= SetCalibrationFilePath,
                          bg=colorMenuBoton,  #'#rrggbb' Background color normal
                          activebackground=colorMenuBotonClicked,  #'#rrggbb' Background color al clickear
                          height= 2,       # Alto del botón en lineas de texto
                          width= 28,       # Ancho del botón en caracteres
                          cursor="hand2",
                          )
        botonCalibrationFile.grid(row=30,column=2, sticky="nsew")


        
            
        
        # - Start: Boton Iniciar Ensayo - 
        framebotonIniciarEnsayo = tk.Frame(self,
                               width=300,
                               height=50,
                               bg=colorPageBg,
                               )
        framebotonIniciarEnsayo.pack_propagate(False)
        framebotonIniciarEnsayo.grid(row=31,column=1, sticky="nsew") # framebotonIniciarEnsayo.pack()

        botonIniciarEnsayo = tk.Button(framebotonIniciarEnsayo,
                            text="Iniciar Ensayo",
                            font=buttonFontVolver,
                            fg='white',
                            command=lambda: verificarDatosIniciarNuevoEnsayo(controller),
                            bg=colorMenuBoton,                                         #
                            activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                            cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                            height=40,
                            width=30
                          )
        botonIniciarEnsayo.pack(pady=5, expand=True, fill=BOTH)
        # - End: Boton Iniciar Ensayo - 

        

        # - Start: Boton Volver - 
        frameVolverAlMenu = tk.Frame(self,
                               width=300,
                               height=50,
                               bg=colorPageBg,
                               )
        frameVolverAlMenu.pack_propagate(False)
        frameVolverAlMenu.grid(row=32,column=1, sticky="nsew") # frameVolverAlMenu.pack()

        buttonVolver = tk.Button(frameVolverAlMenu,
                                text="Volver al menú",
                                font=buttonFontVolver,
                                fg='white',
                                command=lambda: controller.show_frame("PageMenuPrincipal"),
                                bg=colorMenuBoton3,                                         #
                                activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                                cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                                height=40,
                                width=30
                                )
        buttonVolver.pack(pady=5, expand=True, fill=BOTH)
        # - End: Boton Volver - 

        
        # Verificar Datos de Nuevo Ensayo e Iniciar #
        def verificarDatosIniciarNuevoEnsayo(controller):
            
            global RutaEnsayoArchivoRawData   # Pasar variable global de ruta de archivo
            global Data_Frame
            ErrorMessage = ''
            
            
            ## - isNumeric no me sirve con los decimales (Ej: conversion Kg N) - #
            #def isfloat(num):
            #    try:
            #        float(num)
            #        return True
            #    except ValueError:
            #        return False
                
            # Verificar que los campos esten completos CORRECTAMENTE

                # - Info del ensayo - #
            if len(EnsayoCod_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Código de Ensayo \n'
            if len(Proyecto_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Proyecto \n'
            if len(ParTribologico_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Par Triblógico \n'
            if len(Responsable_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Responsable \n'
            if len(Observaciones_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Observaciones \n'

                # - Config del ensayo - #
                    # Duracion
            if len(Duracion_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Duración del Ensayo \n'
            elif len(Duracion_EntryBox.get()) > 6: ErrorMessage = ErrorMessage + 'Duración: Max. 6 caracteres \n'
            #elif Duracion_EntryBox.get().isnumeric() == False: ErrorMessage = ErrorMessage + 'Duración: Usar solo valores numericos \n'
            elif isfloat(Duracion_EntryBox.get()) == False: ErrorMessage = ErrorMessage + 'Duración: Usar solo valores numericos \n'
                    # RPM
            if len(RPM_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta RPM \n'
            elif len(RPM_EntryBox.get()) > 6: ErrorMessage = ErrorMessage + 'RPM: Max. 6 caracteres \n'
            #elif RPM_EntryBox.get().isnumeric() == False: ErrorMessage = ErrorMessage + 'RPM: Usar solo valores numericos \n'
            elif isfloat(RPM_EntryBox.get()) == False: ErrorMessage = ErrorMessage + 'RPM: Usar solo valores numericos \n'
                    # Carga en Kg
            if len(CargaAplicadaKg_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Carga aplicada en Kg \n'
            #elif CargaAplicadaKg_EntryBox.get().isnumeric() == False: ErrorMessage = ErrorMessage + 'Carga en Kg: Usar solo valores numericos \n'
            elif isfloat(CargaAplicadaKg_EntryBox.get()) == False: ErrorMessage = ErrorMessage + 'Carga en Kg: Usar solo valores numericos \n'
                    # Carga en N
            if len(CargaAplicadaN_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Carga aplicada en N \n'
            #elif CargaAplicadaN_EntryBox.get().isnumeric() == False: ErrorMessage = ErrorMessage + 'Carga en N: Usar solo valores numericos \n'
            elif isfloat(CargaAplicadaN_EntryBox.get()) == False: ErrorMessage = ErrorMessage + 'Carga en N: Usar solo valores numericos \n'
                   # Carga en Kg Directa
            if CargaAplicadaKgDirecta_EntryBox.get() == 0: ErrorMessage = ErrorMessage + 'Falta Carga aplicada en Kg Directa \n'
            #elif CargaAplicadaKg_EntryBox.get().isnumeric() == False: ErrorMessage = ErrorMessage + 'Carga en Kg: Usar solo valores numericos \n'
            elif isfloat(CargaAplicadaKgDirecta_EntryBox.get()) == False: ErrorMessage = ErrorMessage + 'Carga en Kg: Usar solo valores numericos \n'
                    # Carga en N Directa
            if len(CargaAplicadaNDirecta_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Carga aplicada en N Directa \n'
            #elif CargaAplicadaN_EntryBox.get().isnumeric() == False: ErrorMessage = ErrorMessage + 'Carga en N: Usar solo valores numericos \n'
            elif isfloat(CargaAplicadaNDirecta_EntryBox.get()) == False: ErrorMessage = ErrorMessage + 'Carga en N: Usar solo valores numericos \n'



                    # Radio disco
            if len(RadioDiscoPista_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Radio Disco Pista Estimado \n'
            #elif RadioDiscoPista_EntryBox.get().isnumeric() == False: ErrorMessage = ErrorMessage + 'Radio Pista Disco Estimado: Usar solo valores numericos \n'
            elif isfloat(RadioDiscoPista_EntryBox.get()) == False: ErrorMessage = ErrorMessage + 'Radio Pista Disco Estimado: Usar solo valores numericos \n'
            
                    # Calibration file
            global RutaArchivoCalibracionSeleccionado
            if RutaArchivoCalibracionSeleccionado == '': ErrorMessage = ErrorMessage + 'Falta Seleccionar archivo de calibracion \n'




            # Checkear si hay algun error
            if ErrorMessage != '': 
                tk.messagebox.showerror("Errores", ErrorMessage)    # Mostrar messagebox con errores
                return                                              # Salir de la funcion para no continuar con la ejecucion del codigo
           




            # Funcion para generar archivo de Setup de Ensayo (se usa mas adelante)
            def generarArchivoSetup():
                #print ('Archivo generado')
                global RutaEnsayoCarpeta
                global RutaEnsayoArchivoSetup

                RutaEnsayoArchivoSetup = RutaEnsayoCarpeta+"/Setup.json"  
                    
                # Data to be written
                dictionary ={
                    "Maquina" : "POD",
                    "FechaYHora": EnsayoFechaYHora_EntryBox.cget("text"),
                    "CodEnsayo": EnsayoCod_EntryBox.get(),
                    "Proyecto": Proyecto_EntryBox.get(),
                    "ParTribologico": ParTribologico_EntryBox.get(),
                    "Responsable": Responsable_EntryBox.get(),
                    "Observaciones": Observaciones_EntryBox.get(),
                    "DuracionS": Duracion_EntryBox.get(),
                    "RPM": RPM_EntryBox.get(),
                    "CargaKg": CargaAplicadaKg_EntryBox.get(),
                    "CargaN": CargaAplicadaN_EntryBox.get(),
                    "CargaKgDirecta": CargaAplicadaKgDirecta_EntryBox.get(),
                    "CargaNDirecta": CargaAplicadaNDirecta_EntryBox.get(),
                    "RadioDiscoPistaMMEstimado": RadioDiscoPista_EntryBox.get(), 
                    "L1": L1, 
                    "L2": L2   
                }
  
                # Serializing json 
                json_object = json.dumps(dictionary, indent = 4)
    
                
                # Writing to sample.json
                with open(RutaEnsayoArchivoSetup, "w") as outfile:
                    outfile.write(json_object)
                




            # ---#--- Empieza el ensayo ---#--- #
            global IsRun 

            IsRun = True            # Actualizo bandera

            global RutaEnsayoCarpeta
            global RutaEnsayoArchivoCalibracion

            if os.path.exists(ensayosPath) == False: Path(ensayosPath).mkdir(parents=True)      # Crear carpeta de ensayos si no existe
            
            CarpetaDeEnsayo = EnsayoFechaYHora_EntryBox.lastTime + '_' + EnsayoCod_EntryBox.get()   # Crear carpeta especifica del ensayo
            RutaEnsayoCarpeta = ensayosPath+ CarpetaDeEnsayo
            Path(RutaEnsayoCarpeta).mkdir(parents=True)

            RutaEnsayoArchivoCalibracion = RutaEnsayoCarpeta+"/Calibration.json"         # Renombrar archivo de calibracion
            shutil.copy(RutaArchivoCalibracionSeleccionado, RutaEnsayoArchivoCalibracion)                             # Copiar archivo de calibracion

            generarArchivoSetup()                                          # Guardar archivo Json con la el setup de maquina

            #  --- LA OBTENCION DE DATOS ESTA THREADEADA --- #
            RutaEnsayoArchivoRawData = RutaEnsayoCarpeta + "/RawData.csv"         # Renombrar archivo de calibracion
            print(RutaEnsayoArchivoRawData)
            global getSerialData_thread

            getSerialData_thread = threading.Thread(
                                    target=lambda:[serialread.getSerialData(RPM,DurationSec, RutaEnsayoArchivoRawData)], 
                                    name="gSerialDataThread")  # no entiendo por que necesito el lambda
            
            getSerialData_thread.start()
            
            controller.show_frame("PageEnsayoRunning")          # Show Page Ensayo Running

                




def generarArchivoCalibration(controller):
    
    # Start: Checkear si hay algun error #
    ErrorMessage = ''                                                                           # Variable Mensaje de error

    if valorCargaAplicadaKg == 0: ErrorMessage = ErrorMessage + 'Falta Valor de carga aplicada en Kg \n'
    if valorCargaAplicadaN == 0: ErrorMessage = ErrorMessage + 'Falta Valor de carga aplicada en N \n'

    if ErrorMessage != '': 
        tk.messagebox.showerror("Error", ErrorMessage)                                          # Mostrar messagebox con errores
        return                                                                                  # Salir de la funcion para no continuar con la ejecucion del codigo

    # End: Checkear si hay algun error #


    # - Start: Guardar archivo - #
    if os.path.exists(calibrationPath) == False: Path(calibrationPath).mkdir(parents=True)      # Crear carpeta si no existe

    directory = filedialog.asksaveasfilename(
                defaultextension='.json', filetypes=[("json files", '*.json')],
                initialdir=calibrationPath,
                title="Elegir nombre de archivo de calibracion")

        # Data to be written
    FechaYHora = str
    FechaYHora = dt.datetime(1, 1, 1).now().strftime("%Y-%m-%d_%H-%M-%S"),                      # Current Date and Time
    dictionary ={
        "Maquina" : "POD",
        "FechaYHora" : FechaYHora,
        "ValorEnCero" : valorEnCero,
        "ValorEnCarga" : valorEnCarga,
        "CargaEnNewtons:" : valorCargaAplicadaN,
        "CargaEnKg:" : valorCargaAplicadaKg,
        "ConstanteEnNewtons" : (valorEnCarga-valorEnCero)/valorCargaAplicadaN,
        "ConstanteEnKg" : (valorEnCarga-valorEnCero)/valorCargaAplicadaKg,
        "PathOriginal" : directory,
        "Notas": calibrationNotas
    }
  
        # Serializing json 
    json_object = json.dumps(dictionary, indent = 4)
    
        # Writing to sample.json
    name = os.path.basename(directory)                                           # Get user filename input
    newname= ''.join(FechaYHora) + '_' + name
    directory = directory.replace(name, newname)                                 # Add date to filename

    with open(directory, "w") as outfile:
        outfile.write(json_object)

    # - End: Guardar archivo - #

    # - Verificar si el archivo fue guardado - #
    if os.path.exists(directory):
        #print ("File exist")
        controller.show_frame("PageMenuPrincipal")    
    else:
        return
        #print ("File not exist")


        
class PageCalibrarMaquina(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        global valorEnCero
        global valorEnCarga
        
        def updateCargaAplicadaN(self):
            global valorCargaAplicadaN
            global valorCargaAplicadaKg
            CargaAplicadaN_EntryBox.delete(0, tk.END)                        # Borrar todo lo previo
            ValueToUpdateN = float(CargaAplicadaKg_EntryBox.get()) * KgN981  # Calcular nuevo valor
            CargaAplicadaN_EntryBox.insert(0, ValueToUpdateN)                # Actualizar valor
            valorCargaAplicadaN = ValueToUpdateN
            valorCargaAplicadaKg = float(CargaAplicadaKg_EntryBox.get())

        def updateCargaAplicadaKg(self):
            global valorCargaAplicadaKg
            global valorCargaAplicadaN
            CargaAplicadaKg_EntryBox.delete(0, tk.END)                              # Borrar todo lo previo
            ValueToUpdateKg = float(CargaAplicadaN_EntryBox.get()) / KgN981         # Calcular nuevo valor
            CargaAplicadaKg_EntryBox.insert(0, ValueToUpdateKg)                     # Actualizar valor
            valorCargaAplicadaN = float(CargaAplicadaN_EntryBox.get())
            valorCargaAplicadaKg = ValueToUpdateKg

        def updateNotas(self):                                                      # Funcion de actualizar variable global Notas
            global calibrationNotas
            calibrationNotas = Notas_EntryBox.get()

        def hideCalibrationFormularAndButton():                                     # Ocultar formulario y botón de generar archivo
            botonGenerarArchivo.pack_forget()
            
            labelEnCero.pack_forget()
            labelEnCarga.pack_forget()
            CargaAplicadaKg_Label.pack_forget()
            CargaAplicadaKg_EntryBox.pack_forget()
            CargaAplicadaN_Label.pack_forget()
            CargaAplicadaN_EntryBox.pack_forget()
            Notas_Label.pack_forget()
            Notas_EntryBox.pack_forget()
            
        def showCalibrationFormularAndButton():                                     # Mostrar formulario y botón de generar archivo
            botonGenerarArchivo.pack(pady=5)
            
            labelEnCero.pack(side="top", fill="x", pady=10)
            labelEnCarga.pack(side="top", fill="x", pady=10)
            CargaAplicadaKg_Label.pack(side="top", fill="x", pady=10)
            CargaAplicadaKg_EntryBox.pack(side="top", fill="x", pady=10)
            CargaAplicadaN_Label.pack(side="top", fill="x", pady=10)
            CargaAplicadaN_EntryBox.pack(side="top", fill="x", pady=10)
            Notas_Label.pack(side="top", fill="x", pady=10)
            Notas_EntryBox.pack(side="top", fill="x", pady=10)
        
        def updateLabels():
            labelEnCero.configure(text='Valor de celda en cero: '+str(round(valorEnCero,2)))
            labelEnCarga.configure(text='Valor de celda en carga: '+str(round(valorEnCarga,2)))
              

        def calibrarMaquina():
    
            global valorEnCero
            global valorEnCarga


            botonIniciarCalibracion.pack_forget()                                          # Ocultar boton iniciar calibracion
            buttonVolver.pack_forget()                                                     # Ocultar boton volver al menu

            # Puesta a Cero
            labelTitulo.configure(text='Obteniendo valor de celda en cero', fg='red')
            tk.messagebox.showinfo("Puesta a Cero", msgPuestaACero)
            valorEnCero = serialread.getCalibrationDataAVG()

            # En Carga
            labelTitulo.configure(text='Obteniendo valor de celda en carga', fg='red')
            tk.messagebox.showinfo("En Carga", msgEnCarga)
            valorEnCarga = serialread.getCalibrationDataAVG()
    
            # Terminando
            labelTitulo.configure(text='Generar archivo', fg='black')
            tk.messagebox.showinfo("Terminando...", msgTerminando)
                # Mostron botón de guardar archivo y formulario
            updateLabels()                                                                      # Actualizar labels de valores recibidos
            showCalibrationFormularAndButton()                                                  # Mostrar formulario

            


        # - Titulo de paguina -
        labelTitulo = tk.Label(self, text="Calibrar máquina", font=controller.font_title)
        labelTitulo.pack(side="top", fill="x", pady=10)
        

        # - Start: Boton Iniciar Calibracion - 
        frameBotonIniciarCalibracion = tk.Frame(self,
                               width=width_acercade_window-24,
                               height=50,
                               bg=colorPageBg,
                               )
        frameBotonIniciarCalibracion.pack_propagate(False)
        frameBotonIniciarCalibracion.pack()

        botonIniciarCalibracion = tk.Button(frameBotonIniciarCalibracion,
                                text="Iniciar calibración",
                                font=buttonFontVolver,
                                fg='white',
                                command= calibrarMaquina,  # No se por que va sin Lambda
                                bg=colorMenuBoton,                                         #
                                activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                                cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                                height=40,
                                width=30
                                )
        botonIniciarCalibracion.pack(pady=5)
        # - End: Boton Generar archivo - 


        # - Start: Formulario - #

                # Frame Formulario
        frameFormularioCargaAplicada = tk.Frame(self,
                               width=width_acercade_window-24,
                               height=450,
                               bg=colorPageBg,
                               )
        frameFormularioCargaAplicada.pack_propagate(False)
        frameFormularioCargaAplicada.pack()

               # Valor en cero
        labelEnCero = tk.Label(frameFormularioCargaAplicada, text="n/a", font=controller.font_subtitle, anchor="w")
        labelEnCero.pack(side="top", fill="x", pady=10)
        labelEnCero.pack_forget()
        
                # Valor en carga
        labelEnCarga = tk.Label(frameFormularioCargaAplicada, text="n/a", font=controller.font_subtitle, anchor="w")
        labelEnCarga.pack(side="top", fill="x", pady=10)
        labelEnCarga.pack_forget()

                # Carga aplicada Kg
        CargaAplicadaKg_Label = tk.Label(frameFormularioCargaAplicada, text="Carga aplicada [Kg]",  font=controller.font_subtitle, anchor="w") #, font=controller.font_title)
        CargaAplicadaKg_Label.pack(side="top", fill="x", pady=10)
        CargaAplicadaKg_Label.pack_forget()

        CargaAplicadaKg_EntryBox = tk.Entry(frameFormularioCargaAplicada, font=controller.font_subtitle, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected) 
        CargaAplicadaKg_EntryBox.bind('<KeyRelease>', updateCargaAplicadaN)
        CargaAplicadaKg_EntryBox.pack(side="top", fill="x", pady=10)
        CargaAplicadaKg_EntryBox.pack_forget()
       
                # Carga aplicada N
        CargaAplicadaN_Label = tk.Label(frameFormularioCargaAplicada, text="Carga aplicada [N]",  font=controller.font_subtitle, anchor="w") #, font=controller.font_title)
        CargaAplicadaN_Label.pack(side="top", fill="x", pady=10)
        CargaAplicadaN_Label.pack_forget()

        CargaAplicadaN_EntryBox = tk.Entry(frameFormularioCargaAplicada, width=entryBox_Width, font=controller.font_subtitle, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected) 
        CargaAplicadaN_EntryBox.bind('<KeyRelease>', updateCargaAplicadaKg)
        CargaAplicadaN_EntryBox.pack(side="top", fill="x", pady=10)
        CargaAplicadaN_EntryBox.pack_forget()

                # Notas
        Notas_Label = tk.Label(frameFormularioCargaAplicada, text="Notas",  font=controller.font_subtitle, anchor="w")
        Notas_Label.pack(side="top", fill="x", pady=10)
        Notas_Label.pack_forget()
        
        Notas_EntryBox = tk.Entry(frameFormularioCargaAplicada, width=entryBox_Width, font=controller.font_subtitle, highlightthickness=entryBox_BorderWidth, relief="solid", highlightbackground = colorEntryBoxUnselected, highlightcolor= colorEntryBoxSelected)
        Notas_EntryBox.bind('<KeyRelease>', updateNotas)
        Notas_EntryBox.pack(side="top", fill="x", pady=10)
        Notas_EntryBox.pack_forget() 

        # - End: Formulario - #
        


        # - Start: Boton Generar archivo - 
        framebotonGenerarArchivo = tk.Frame(self,
                               width=width_acercade_window-24,
                               height=50,
                               bg=colorPageBg,
                               )
        framebotonGenerarArchivo.pack_propagate(False)
        framebotonGenerarArchivo.pack()

        botonGenerarArchivo = tk.Button(framebotonGenerarArchivo,
                                text="Generar archivo de calibracion",
                                font=buttonFontVolver,
                                fg='white',
                                command= lambda:[
                                    generarArchivoCalibration(controller),
                                    hideCalibrationFormularAndButton(),
                                    labelTitulo.configure(text='Calibrar máquina'),
                                    botonIniciarCalibracion.pack(),                                          # Ocultar boton iniciar calibracion
                                    buttonVolver.pack()                                                     # Ocultar boton volver al menu
                                    ],             # Va con lambda para que no se ejecute al inicio
                                bg=colorMenuBoton,                                                  #
                                activebackground=colorMenuBotonClicked,                             #'#rrggbb' Background color al clickear
                                cursor="hand2",                                                     # Cambiar al cursor al estar por encima del boton
                                height=40,
                                width=30
                                )
        botonGenerarArchivo.pack(pady=5)
        botonGenerarArchivo.pack_forget()
        # - End: Boton Generar archivo - 

        # - Start: Boton Volver - 
        frameVolverAlMenu = tk.Frame(self,
                               width=width_acercade_window-24,
                               height=50,
                               bg=colorPageBg,
                               )
        frameVolverAlMenu.pack_propagate(False)
        frameVolverAlMenu.pack()

        buttonVolver = tk.Button(frameVolverAlMenu,
                                text="Volver al menú",
                                font=buttonFontVolver,
                                fg='white',
                                command=lambda: controller.show_frame("PageMenuPrincipal"),
                                bg=colorMenuBoton3,                                         #
                                activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                                cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                                height=40,
                                width=30
                                )
        buttonVolver.pack(pady=5)
        # - End: Boton Volver - 


class PageEnsayoRunning(tk.Frame):


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        global redirectPage

        # Page Frame Setup
        self.config(bg=colorAppBg)                   # Background color


        # Create a ScrolledFrame widget

        sf2 = ScrolledFrame(self, bg='grey', relief='flat',borderwidth=0)         # Ancho definido por la variable del texto
        sf2.pack(side="top", expand=True, fill="both")                  # Expandir vertical y horizontal
        #sf2.grid(row=0, column=0, sticky="n")

        # Bind the arrow keys and scroll wheel
        sf2.bind_arrow_keys(self)
        sf2.bind_scroll_wheel(self)

        frameEnsayoRunning = sf2.display_widget(tk.Frame)
        frameEnsayoRunning.config(bg=colorPageBg)

        
        
        # Para centrar, se usa el Wight excepto en el contenido que se autodefine
        frameEnsayoRunning.grid_columnconfigure(0, weight=1)
        frameEnsayoRunning.grid_columnconfigure(2, weight=1)

        # Label Titulo #
        labelTitulo = tk.Label(frameEnsayoRunning, text="Running test", font=controller.font_title)
        labelTitulo.grid(row=0, column=1, sticky="s")  


    # --- Start: Frame que contiene los 4 graficos --- #

        frameGraficos = tk.Frame(frameEnsayoRunning) #, bg='yellow')
        frameGraficos.grid(row=1, column=1, sticky="s")  
        
        # --- Ubicacion Graficos --- #
        # Grafico N-E #
        canvas1 = FigureCanvasTkAgg(figure1, frameGraficos)
        canvas1.get_tk_widget().grid(row=1, column=1, sticky='n')
        toolbar1 = NavigationToolbar2Tk(canvas1, frameGraficos, pack_toolbar=False)
        toolbar1.update()
        toolbar1.grid(row=2, column=1, sticky='s')
        # Grafico N-W #
        canvas2 = FigureCanvasTkAgg(figure2, frameGraficos)
        canvas2.get_tk_widget().grid(row=1, column=2, sticky='n')
        toolbar2 = NavigationToolbar2Tk(canvas2, frameGraficos, pack_toolbar=False)
        toolbar2.update()
        toolbar1.grid(row=2, column=2, sticky='s')        
        # Grafico S-E #
        canvas3 = FigureCanvasTkAgg(figure3, frameGraficos)
        canvas3.get_tk_widget().grid(row=4, column=1, sticky='n')
        toolbar3 = NavigationToolbar2Tk(canvas3, frameGraficos, pack_toolbar=False)
        toolbar3.update()
        toolbar3.grid(row=5, column=1, sticky='s')
        # Grafico S-W #
        canvas4 = FigureCanvasTkAgg(figure4, frameGraficos)
        canvas4.get_tk_widget().grid(row=4, column=2, sticky='n')
        toolbar4 = NavigationToolbar2Tk(canvas4, frameGraficos, pack_toolbar=False)
        toolbar4.update()
        toolbar4.grid(row=5, column=2, sticky='s')



        def finishEnsayo():                                                     #Funcion al terminar ensayo
            global todoOk
            if todoOk is True:      # El ensayo finalizo correctamente
                tk.messagebox.showinfo("Finalizando...", msgDatosObtenidos)     # Mostrar messagebox maquina conectada
                controller.show_frame("PagePinDiskRadius")
            else:                   # Parada de emergencia
                tk.messagebox.showinfo("Ensayo Detenido", "Se ha detenido el ensayo")
                MenuPrincipal_Button.grid(row=1, column=1, sticky="s", padx=10, pady=10)
        
        def boton_menuprincipal():
            global IsOver, IsRun, todoOk 
            if messagebox.askokcancel("Desea volver?", "NO PODRA VOLVER A ESTA PANTALLA"):
                IsRun = False                                                               # Actualizo bandera
                todoOk = True                                                               # Actualizo bandera (Sirve si ocurre Emergencia)
                controller.show_frame("PageMenuPrincipal")                                  

        def stop_test():
            global todoOk
            todoOk = False      # Actualizo bandera
            serialread.stopSerialData() # Paro adquisicion Arduino
            getSerialData_thread.join() # Se detiene el thread

        # --- Botones --- #
        Emergency_Button = tk.Button(frameEnsayoRunning, text='Detener Ensayo', font=controller.font_title, command=lambda: stop_test())
        Emergency_Button.grid(row=1, column=1, sticky='s', padx=10, pady=10)

        MenuPrincipal_Button = tk.Button(frameEnsayoRunning, text="Menu Principal", font=controller.font_title, command=lambda: boton_menuprincipal())
        MenuPrincipal_Button.grid(row=1, column=1, sticky="s", padx=10, pady=10)
        MenuPrincipal_Button.grid_remove()
        # --- --- #

        # --- Ejecutar funcion para plotear los graficos --- #
       
        def UpdateChartEverySecond():                                               # Funcion para plotear cada 1 segundo
            global lastFileSize, timer                                                    # Pasar variable
            global ani1, ani2, ani3, ani4
            timer = threading.Timer(1, UpdateChartEverySecond)
            timer.start()   # Update 1 segundo
            

            if (lastFileSize == Path(RutaEnsayoArchivoRawData).stat().st_size ):    # Si es el mismo tamaño de archivo
                #print("Killed")                                                        # For debugging
                lastFileSize = int                                                      # Resetear variable
                timer.cancel()                                                          # Terminar thread de update de graficos
                getSerialData_thread.join()                                          # Terminar thread de adquisicion de datos  NO VA CON CANCEL
                finishEnsayo()                                                          # llamar funcion de terminar ensayo
                labelTitulo['text'] = "Graficos"                                       
                Emergency_Button.grid_remove()                                          # Elimina boton Emergencia
                MenuPrincipal_Button.grid(row=1, column=1, sticky="s", padx=10, pady=10) # Aparece boton MenuPrincipal
                for anim in (ani1, ani2, ani3, ani4):
                    anim.pause()                                                    # Para ploteo de graficos
                check_runtest()                                                     # Vuelve a cargar funcion

        def check_runtest():    # Verifica estados del programa - Reinicia para iniciar nuevo ensayo
            global ani1, ani2, ani3, ani4
            global IsRun, FirstTime, IsOver

            if (IsRun is True) and (FirstTime is True): # Inicia el ensayo
                FirstTime = False
                for anim in (ani1, ani2, ani3, ani4):   # Vuelve a iniciar ploteo de graficos
                    anim.resume()                       # Sirve cuando se reinicia ensayo
                UpdateChartEverySecond()
                self.after(1000, check_runtest)

            elif (IsRun is False) and (FirstTime is False):# Reinicia para iniciar nuevo ensayo
                FirstTime = True
                MenuPrincipal_Button.grid_remove()          # Elimina boton MenuPrincipal
                Emergency_Button.grid(row=1, column=1, sticky="s", padx=10, pady=10)    # Aparece boton Emergencia
                self.after(1000, check_runtest)

            else:                               # Espera a actualizacion de bandera
                self.after(1000, check_runtest)

        check_runtest()

        # --- End: Frame que contiene los 4 graficos --- #
        
  


# --- Start: PAGINA "ACERA DE" --- #

class PagePinDiskRadius(tk.Frame):           # DENTRO UTILIZA UN ScrolledFrame
            


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Page Frame Setup
        self.config(bg=colorAppBg)                   # Background color
        

        
        # Create a ScrolledFrame widget

        sf = ScrolledFrame(self, width=width_acercade_text, bg='grey', relief='flat',borderwidth=0)         # Ancho definido por la variable del texto
        sf.pack(side="top", expand=True, fill="y")                  # Expandir solo en vertical (y)

        # Bind the arrow keys and scroll wheel
        sf.bind_arrow_keys(self)
        sf.bind_scroll_wheel(self)

        framePinDiskRadius = sf.display_widget(tk.Frame)
        framePinDiskRadius.config(bg=colorPageBg)

        
        
        
    # - Start:  - #
      
        # Label Titulo
        labelAcercaDeManual_title = tk.Label(framePinDiskRadius, text="Medicion radio pin disco", font=controller.font_title_acercade, bg=colorPageBg)
        labelAcercaDeManual_title.pack(pady=10)
        
        # Message Contenido
        messageAcercaDeManual_contenido = tk.Message(framePinDiskRadius, width=width_acercade_text, font=controller.font_text_acercade, anchor="nw", bg=colorPageBg, 
                                                    text="Ingresar valor. Luego hacer click en Continuar.")
        messageAcercaDeManual_contenido.pack() 
        

        # Entrybox del valor medido
        RadioPinDiscoReal_EntryBox = tk.Entry(framePinDiskRadius, width=30) 
        RadioPinDiscoReal_EntryBox.pack()
        
        # Boton Continuar
        buttonAbrirManual = tk.Button(framePinDiskRadius, text="Continuar", width=30,command=lambda: verificarYmandarValor())
        buttonAbrirManual.pack()

        # Imagen de referencia
        img = Image.open(rutaimgMed)
        img = img.resize((590,300))
        img_Medicion = ImageTk.PhotoImage(img)
        ImagenMedicion = tk.Label(framePinDiskRadius, image=img_Medicion)
        ImagenMedicion.image = img_Medicion
        ImagenMedicion.pack(fill='both')


    # - End:  - #

        def verificarYmandarValor():
                  # Proyecto
            #print('verificar')
            
            ErrorMessage = ''

            if len(RadioPinDiscoReal_EntryBox.get()) == 0: ErrorMessage = ErrorMessage + 'Falta Valor \n'
            elif isfloat(RadioPinDiscoReal_EntryBox.get()) == False: ErrorMessage = ErrorMessage + 'Usar solo valores numericos \n'
            
            # Checkear si hay algun error
            if ErrorMessage != '': 
                tk.messagebox.showerror("Error", ErrorMessage)    # Mostrar messagebox con errores
                return                                              # Salir de la funcion para no continuar con la ejecucion del codigo
           

            # Actualizar archivo con valor real de diametro de MM
            global RutaEnsayoCarpeta
            
            directory = RutaEnsayoCarpeta+"/Setup.json"  
            #listObj = []
 
            # Read JSON file
            with open(directory) as fp:
              listObj = json.load(fp)
 
            # Verify existing list
            listObj["RadioDiscoPistaMMReal"] = RadioPinDiscoReal_EntryBox.get()
          
            with open(directory, 'w') as json_file:                                     # Guardar cambios en el archivo json
                json.dump(listObj, json_file, indent=4)

            # Copiar Archivo xlsm
            global RutaEnsayoArchivoInforme
            global rutaInformeXlsm

            RutaEnsayoArchivoInforme = RutaEnsayoCarpeta+"/Informe_00.xlsm"         # Archivo informe

            shutil.copy(rutaInformeXlsm, RutaEnsayoArchivoInforme)                             # Copiar archivo de calibracion

            # Ejecutar Macros del Excel
            xlApp = win32com.client.DispatchEx('Excel.Application')
            xlsPath = os.path.expanduser(RutaEnsayoArchivoInforme)       # xlsPath = os.path.expanduser('C:\test1\test2\test3\test4\MacroFile.xlsm')'
            wb = xlApp.Workbooks.Open(Filename=xlsPath)
            xlApp.Run('EjecutarTodasLasMacros')                 # xlApp.Run('macroName') 
            wb.Save()
            xlApp.Quit()
            

            
            # Continuar proceso de terminar el archivo
            tk.messagebox.showinfo("Ensayo Finalizado", msgEnsayoFinalizado+RutaEnsayoArchivoInforme)     # Mostrar messagebox maquina conectada
            os.startfile(RutaEnsayoArchivoInforme)                                                           # Abrir archivo de informe
                            

            controller.show_frame("PageEnsayoRunning")

            

            # PageEnsayoRunning.draw_chart()

# --- End: PAGINA "PIN DISK RADIUS" --- #




# --- Start: PAGINA "ACERA DE" --- #

class PageAcercaDe(tk.Frame):           # DENTRO UTILIZA UN ScrolledFrame
            


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Page Frame Setup
        self.config(bg=colorAppBg)                   # Background color
        
        
        # Create a ScrolledFrame widget

        sf = ScrolledFrame(self, width=width_acercade_text, bg='grey', relief='flat',borderwidth=0)         # Ancho definido por la variable del texto
        sf.pack(side="top", expand=True, fill="y")                  # Expandir solo en vertical (y)

        # Bind the arrow keys and scroll wheel
        sf.bind_arrow_keys(self)
        sf.bind_scroll_wheel(self)

        frameAcercaDe = sf.display_widget(tk.Frame)
        frameAcercaDe.config(bg=colorPageBg)


    # - Start: Acerca de Proyecto - #

        # Label Titulo
        labelAcercaDeP_title = tk.Label(frameAcercaDe, text="Acerca del proyecto", font=controller.font_title_acercade, bg=colorPageBg)
        labelAcercaDeP_title.pack(pady=10)        #labelAcercaDeP_title.pack(side="top", expand=True, fill="both", pady=10)

        # Message Contenido
        messageAcercaDelP_contenido = tk.Message(frameAcercaDe,
                                                 width=width_acercade_text,
                                                 font=controller.font_text_acercade,     # Formato de texto
                                                 anchor="nw",                             # Ubicar el texto a la izquierda
                                                 bg=colorPageBg,                            # Para debuggear
                                                 text="Dispositivo creado como proyecto final de la carrera Ingeniería Mecánica por los alumnos:\
                                                   \n \
                                                   \n - Miche, Alexander \
                                                   \n - Molina, Matías Fabián \
                                                   \n - Viola, Lucas Micael \
                                                   \n - Zamberlan, Agustin \
                                                   \n \
                                                   \n \
                                                   \n  Agradecimientos especiales: \
                                                   \n - Zanin, Maximiliano \
                                                   \n - Urbano, Nicolás \
                                                   \n \
                                                    ")

        messageAcercaDelP_contenido.pack() #(fill='both')
    # - End: Acerca de Proyecto - #


    # - Start: Boton Volver - 
        frameVolverAlMenu = tk.Frame(self,
                               width=width_acercade_window-24,
                               height=50,
                               bg=colorPageBg,
                               )
        frameVolverAlMenu.pack_propagate(False)
        frameVolverAlMenu.pack()

        buttonVolver = tk.Button(frameVolverAlMenu,
                                text="Volver al menú",
                                font=buttonFontVolver,
                                fg='white',
                                command=lambda: controller.show_frame("PageMenuPrincipal"),
                                bg=colorMenuBoton3,                                         #
                                activebackground=colorMenuBotonClicked,                           #'#rrggbb' Background color al clickear
                                cursor="hand2",                                                   # Cambiar al cursor al estar por encima del boton
                                height=40,
                                width=30
                                )
        buttonVolver.pack(pady=5)
    # - End: Boton Volver - 


# --- End: PAGINA "ACERA DE" --- #



# --- Start: CONFIGURACION DEL PROGRAMA --- #

if __name__ == "__main__":
    app = SampleApp()
    # Actualizacion de graficos #
    ani1 = anim.FuncAnimation(figure1, draw_chart, 30, interval=1000, blit=False)
    ani2 = anim.FuncAnimation(figure2, draw_chart, 30, interval=1000, blit=False)
    ani3 = anim.FuncAnimation(figure3, draw_chart, 30, interval=1000, blit=False)
    ani4 = anim.FuncAnimation(figure4, draw_chart, 30, interval=1000, blit=False)


    # - Definir tamaño de pantalla - #
            # app.geometry(defaultGeometry)                              # Dimensiones por default, seteadas en la variable global
            # app.attributes('-fullscreen', True)                        # Pantalla completa (sin barra superior ni menu de inicio)
            # w, h = app.winfo_screenwidth(), app.winfo_screenheight()   # Variables de resolucion de pantalla
            # app.geometry("%dx%d+0+0" % (w, h-100))                     # Setear tamaño
    app.state("zoomed")                 # Maximizar pantalla, sin cubrir title bar and taskbar
    
    app.minsize(minWidth,minHeight)     # Dimensiones minimas
    app.iconbitmap(rutaLogoUtn)         # Poner logo de la UTN en la barra superior
    app.title(titleBarText)             # Titulo de la ventana
    app.config(bg=colorAppBg)           # Color de fondo
    
    def close_window():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            app.destroy() # Mata la GUI
            os._exit(0) # Mata el proceso en python

    app.protocol("WM_DELETE_WINDOW", close_window) # Cerrar programa
    app.mainloop()                      # Mainloop, fundamental
# --- End: CONFIGURACION DEL PROGRAMA --- #
