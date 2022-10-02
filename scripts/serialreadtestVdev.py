# --- IMPORTAR LIBRERIAS NECESARIAS --- #
from sqlite3 import paramstyle
import serial                                               # Importar libreria pyserial
import time                                                 # Importar libreria time
import pandas as pd

# --- DECLARACION DE VARIABLES --- #
comPort = ''                                                # Puerto COM
baudRate = 115200                                           # Baudrate 
ser = None                                                  # Variable de Objeto Serial

# --- FUNCION PARA CONECTAR AL PUERTO COM --- #
def connectSerial(puertoCom):                               # Pasar puerto COM como variable. Ej: 'COM5'
    try: 
        global ser                                              # Pasar variable global de Conexion Serial
        global comPort                                          # Pasar variable global de Puerto Com
        comPort = puertoCom                                     # Setear variable global de Puerto Com con variable de call de funci�n
        ser = serial.Serial(comPort,baudRate,timeout=5)         # Leer serial en puerto COM con Baudrate
        time.sleep(3)                                           # Esperar 3 segundos
        print('connected')                                     # Debugging
    except: 
        print('connectSerial Error')

# --- FUNCION PARA COMPROBAR SI ESTOY CONECTADO A LA MAQUINA --- #
def isSerialConnected():
    
    # Probar si se puede conectar
    try:    
        global ser
        serialCmd = 'CHECKCONNECTION'                           # Enviar se�al de probar conexion
        ser.write(serialCmd.encode())                           # Escribir comando
        decoded_bytes=""
        time.sleep(1)                                           # Esperar respuesta 1 segundos
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-1].decode('utf-8')       #Decode para evitar b   /n
        if decoded_bytes == 'PODCONNECTED':                      # Si recibe respuesta de conectado a maqina POD
            return True                                                 # Devolver Verdadero
        else:                                                    # Si la respuesta no existe, o es cualquier otra cosa
            return False                                                # Devolver falso

    # Si no se puede conectar, devolver Falso
    except:
        return False


# --- FUNCION PARA RECIBIR LA INFORMACION DEL ENSAYO --- #
def getSerialData(RPM,DurationSec,FileToSave):                         # RPM in String format "######" 6 digitos.
    global ser                                              # DurationSec in String format "######" 6 digitos.

    serialCmd = 'TESTSTART-'+RPM+'-'+DurationSec            # Ej:   serialCmd = "TESTSTART-000800-000015"
    #print(serialCmd)
    ser.write(serialCmd.encode())                               # Escribir comando
    print(ser.write(serialCmd.encode()))

    decoded_bytes=""

    print(FileToSave)
    columns=('tiempoMs,' + 'tempAmbC,' + 'tempObjC,' + 'vueltas,' + 'celdaCarga')
    open(FileToSave, 'a').write(columns)
    open(FileToSave, 'a').write('\n')

    dataf = []
    while True:
        
        if decoded_bytes == 'TESTEND' or decoded_bytes == 'TESTSTOPPED':
            with open(FileToSave,"r") as f:
                lines = f.readlines()                          # Guardar linea (Viene formatada en CSV)
                lines = lines[:-1]                                   # Nueva Linea

            open(FileToSave, "w").write(str(lines[0]))
            for i in range(1,len(lines)):
                open(FileToSave, "a").write(str(lines[i]))
            break
        else:
            ser_bytes = ser.readline()
            decoded_bytes = ser_bytes[0:len(ser_bytes)-1].decode('utf-8')
            list = decoded_bytes.split(',')
            # --- Promediar casa 0.25 seg --- #
            dataf.append(list)
            if len(dataf) == 20:
                prom_df = pd.DataFrame(dataf[1:], columns=['tiempoMs', 'tempAmbC', 'tempObjC', 'vueltas', 'celdaCarga'])
                data_send = (prom_df['tiempoMs'].max() +','
                            + prom_df['tempAmbC'].max() + ','
                            + prom_df['tempObjC'].max() + ','
                            + prom_df['vueltas'].max() + ','
                            + prom_df['celdaCarga'].max() )
                with open(FileToSave,"a") as f:
                    f.write(str(data_send))                          # Guardar linea (Viene formatada en CSV)
                    f.write('\n')                                   # Nueva Linea """                
                dataf = [] 

# --- Funcion Detener adquisicion Manualmente --- #
def stopSerialData():
    global ser

    serialCmd = 'TESTSTOP'
    ser.write(serialCmd.encode())                               # Escribir comando
    print(ser.write(serialCmd.encode()))
    

    






# --- FUNCION PARA RECIBIR LOS VALORES DE CALIBRACION --- #
def getCalibrationDataAVG():                        
    global ser                                            

    serialCmd = 'CALIBRACIONMEDICION'                       # Comando de comienzo de calibracion
    #print(serialCmd)
    ser.write(serialCmd.encode())                               # Escribir comando
    valuesArray=[]

    decoded_bytes=""

    while True:
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-1].decode('utf-8')       #Decode para evitar b   /n

        if decoded_bytes == 'CALIBRACIONEND':               # Salir si recibe se�al de finalizado
            promedio = sum(valuesArray)/float(len(valuesArray))
            #print(promedio)
            return promedio

        if decoded_bytes != 'CALIBRACIONSTART':             # Si no es esa se�al
            #print(decoded_bytes)                               # For debugging
            valuesArray.append(int(decoded_bytes))                  # Agregar valor leido al array (como int, para poder calcular)
    
if __name__ == "__main__":
    connectSerial("COM4")
    A = getSerialData("000700","00100",("C:\MaquinaPOD\Ensayos\EnsayoTest" + "/RawData.csv"))
    stopSerialData()
