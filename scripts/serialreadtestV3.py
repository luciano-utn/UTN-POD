import serial                                           # Importar libreria pyserial
import time                                             # Importar libreria time

comPort = ''                                            # Puerto COM
baudRate = 115200                                       # Baudrate 
ser = None                                              # Variable de Objeto Serial

def connectSerial(puertoCom):                           # Pasar puerto COM como variable. Ej: 'COM5'
    global ser                                          # Pasar variable global de Conexion Serial
    global comPort                                      # Pasar variable global de Puerto Com
    comPort = puertoCom                                 # Setear variable global de Puerto Com con variable de call de función
    ser = serial.Serial(comPort,baudRate,timeout=5)     # Leer serial en puerto COM con Baudrate
    time.sleep(5)                                       # Esperar 5 segundos
    print('connected')


def sendSerialData(dataToSend):
    print(dataToSend)


def testStart():
    ser = serial.Serial(comPort,baudRate,timeout=5)            # Leer serial en puerto COM con Baudrate  
    serialCmd = 'TESTSTART-000800-000015'
    ser.write(serialCmd.encode())                               # Escribir comando


def getSerialData():
    global ser
    
    #ser = serial.Serial('COM5',115200,timeout=5)            # Leer serial en puerto COM con Baudrate  
    #ser.flushInput()                                        # Flush

    #time.sleep(5)

    serialCmd = "TESTSTART-000800-000015"
    ser.write(serialCmd.encode())                               # Escribir comando


    decoded_bytes=""

    while True:

        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-1].decode('utf-8')       #Decode para evitar b   /n

        print(decoded_bytes)

        if decoded_bytes == 'TESTEND':
            break


        with open("test_data.csv","a") as f:
            f.write(decoded_bytes)                          # Guardar linea (Viene formatada en CSV)
            f.write('\n')                                   # Nueva Linea
            




    #while True:
    #    try:
    #        ser_bytes = ser.readline()
    #        decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode('utf-8')       #Decode para evitar b   /n
        

    #        #print(decoded_bytes)
    #        #wait = input("Press Enter to continue.")           # Para debugear

    #        with open("test_data.csv","a") as f:
    #            f.write(decoded_bytes)                          # Guardar linea (Viene formatada en CSV)
    #            f.write('\n')                                   # Nueva Linea
            
    #    except:
    #        print("Keyboard Interrupt")
    #        break






#wait = input("Press Enter to continue.")

#getSerialData()

#wait = input("Press Enter to continue2.")
