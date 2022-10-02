import serial

def getSerialData():

    ser = serial.Serial('COM5',115200,timeout=5)            # Leer serial en puerto COM con Baudrate
    ser.flushInput()                                        # Flush

    while True:
        try:
            ser_bytes = ser.readline()
            decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode('utf-8')       #Decode para evitar b   /n
        

            #print(decoded_bytes)
            #wait = input("Press Enter to continue.")           # Para debugear

            with open("test_data.csv","a") as f:
                f.write(decoded_bytes)                          # Guardar linea (Viene formatada en CSV)
                f.write('\n')                                   # Nueva Linea
            
        except:
            print("Keyboard Interrupt")
            break

#wait = input("Press Enter to continue.")

#getSerialData()

#wait = input("Press Enter to continue2.")
