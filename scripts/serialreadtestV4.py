# --- IMPORTAR LIBRERIAS NECESARIAS --- #
import serial                                               # Importar libreria pyserial
import time                                                 # Importar libreria time

# --- DECLARACION DE VARIABLES --- #
comPort = ''                                                # Puerto COM
baudRate = 115200                                           # Baudrate 
ser = None                                                  # Variable de Objeto Serial

# --- FUNCION PARA CONECTAR AL PUERTO COM --- #
def connectSerial(puertoCom):                               # Pasar puerto COM como variable. Ej: 'COM5'
    global ser                                              # Pasar variable global de Conexion Serial
    global comPort                                          # Pasar variable global de Puerto Com
    comPort = puertoCom                                     # Setear variable global de Puerto Com con variable de call de funci?n
    ser = serial.Serial(comPort,baudRate,timeout=5)         # Leer serial en puerto COM con Baudrate
    time.sleep(5)                                           # Esperar 5 segundos
    #print('connected')                                     # Debugging


# --- FUNCION PARA COMPROBAR SI ESTOY CONECTADO A LA MAQUINA --- #
def isSerialConnected():
    
    # Probar si se puede conectar
    try:    
        global ser
        serialCmd = 'CHECKCONNECTION'                           # Enviar se?al de probar conexion
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
def getSerialData(RPM,DurationSec):                         # RPM in String format "######" 6 digitos.
    global ser                                              # DurationSec in String format "######" 6 digitos.

    serialCmd = 'TESTSTART-'+RPM+'-'+DurationSec            # Ej:   serialCmd = "TESTSTART-000800-000015"
    ser.write(serialCmd.encode())                               # Escribir comando
    
    decoded_bytes=""

    while True:

        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-1].decode('utf-8')       #Decode para evitar b   /n
        print(decoded_bytes)                                # For debugging

        if decoded_bytes == 'TESTEND':                      # Salir si recibe se?al de finalizado
            break

        with open("test_data.csv","a") as f:
            f.write(decoded_bytes)                          # Guardar linea (Viene formatada en CSV)
            f.write('\n')                                   # Nueva Linea
