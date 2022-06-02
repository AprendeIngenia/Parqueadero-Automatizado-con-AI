# Importamos librerias
import torch
import cv2
import numpy as np
import serial

# Leemos el modelo
model = torch.hub.load('ultralytics/yolov5', 'custom',
                       path = 'C:/Users/santi/Desktop/Universidad/9 Semestre/Vision Python/ArduinoCom/Red.pt')

# Color Verde
verded = np.array([40,80,80])
verdeu = np.array([80,220,220])

# Púerto serial
com = serial.Serial("COM3", 9600, write_timeout= 10)
a = 'a'
c = 'c'

# Realizo Videocaptura
cap = cv2.VideoCapture(0)

# Variables
contafot = 0
contacar = 0
marca = 0
flag1 = 0
flag2 = 0

# Empezamos
while True:
    # Realizamos lectura de frames
    ret, frame = cap.read()

    # Creamos copia
    copia = frame.copy()

    # Mostramos el numero de vehiculos
    cv2.putText(frame, "Ocupacion: ", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, str(contacar), (200, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, "Carros", (240, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Mejoramos rendiemiento
    contafot += 1
    if contafot % 3 != 0:
        continue

    # Realizamos las detecciones
    detect = model(frame, size = 640)

    # Extraemos la info
    info = detect.pandas().xyxy[0].to_dict(orient="records")  # Predicciones

    # Preguntamos si hay Detecciones
    if len(info) != 0:
        # Creamos FOR
        for result in info:

            # Confianza
            conf = result['confidence']
            #print(conf)

            if conf >= 0.70:
                # Clase
                cls = int(result['class'])
                # Xi
                xi = int(result['xmin'])
                # Yi
                yi = int(result['ymin'])
                # Xf
                xf = int(result['xmax'])
                # Yf
                yf = int(result['ymax'])

                # Dibujamos
                cv2.rectangle(frame, (xi, yi), (xf, yf), (0,0,255), 2)

                # Buscamos la marca del suelo
                # copia = cv2.cvtColor(copia, cv2.COLOR_BGR2RGB)
                hsv = cv2.cvtColor(copia, cv2.COLOR_BGR2HSV)

                # Creamos mascara
                mask = cv2.inRange(hsv, verded, verdeu)

                # Contornos
                contornos, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                contornos = sorted(contornos, key=lambda x: cv2.contourArea(x), reverse=True)

                # Detectamos la Marca
                for ctn in contornos:
                    # Extraemos informacion de la marca
                    xiz, yiz, ancho, alto = cv2.boundingRect(ctn)
                    # Xf e Yf de la region de la marca
                    xfz, yfz = ancho + xiz, alto + yiz
                    # Dibujamos un rectangulo alrededor de la marca
                    cv2.rectangle(frame, (xiz, yiz), (xfz, yfz), (0, 255, 0), 2)

                    # Extraemos el centro
                    cxm, cym = (xiz + xfz) // 2, (yiz + yfz) // 2
                    # Dibujamos
                    cv2.circle(frame, (cxm, cym), 2, (0, 255, 0), 3)

                    # Delimitamos zonas de interes
                    # Entrada
                    linxe = cxm + 70

                    # Salida
                    linxs = cxm - 70

                    # Demarcamos zona en rojo
                    cv2.line(frame, (linxe, yiz), (linxe, yfz), (0, 0, 255), 2)
                    cv2.line(frame, (linxs, yiz), (linxs, yfz), (0, 0, 255), 2)
                    cv2.circle(frame, (20, 20), 15, (0, 0, 255), cv2.FILLED)

                    # Si el carro esta en zona de entrada
                    if xi < linxe < xf and flag1 == 0 and flag2 == 0 or marca == 1:
                        print("ENTRADA")
                        # Activamos primer marca
                        flag1 = 1

                        # Podemos hacer lo que queramos (Placas, etc ...)
                        cv2.circle(frame, (20, 20), 15, (0, 255, 255), cv2.FILLED)
                        cv2.line(frame, (linxe, yiz), (linxe, yfz), (0, 255, 255), 2)

                        # Enviamos señal y movemos servo
                        com.write(a.encode('ascii'))

                        marca = 1
                        # Punto Medio
                        if xi < linxs < xf and flag1 == 1:
                            print("ENTRADA2")
                            # Dibujamos
                            cv2.putText(frame, "ENTRANDO", (40, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                            cv2.line(frame, (linxs, yiz), (linxs, yfz), (0, 255, 255), 2)

                            # Activamos bandera 2
                            flag2 = 1

                        elif xf < linxs and flag2 == 1:
                            print("ENTRADA3")
                            # Cerramos puerta
                            com.write(c.encode('ascii'))
                            # Reiniciamos marcas y flags
                            marca = 0
                            flag1 = 0
                            flag2 = 0

                            # Contamos vehiculos
                            contacar = contacar + 1



                    # Si el carro esta en zona de salida
                    elif xi < linxs < xf and flag1 == 0 and flag2 == 0 or marca == 2:
                        print("SALIDA")
                        # Activamos primer marca
                        flag2 = 2

                        # Podemos hacer lo que queramos (Placas, etc ...)
                        cv2.circle(frame, (20, 20), 15, (0, 255, 255), cv2.FILLED)
                        cv2.line(frame, (linxs, yiz), (linxs, yfz), (0, 255, 255), 2)

                        # Enviamos señal y movemos servo
                        com.write(a.encode('ascii'))
                        marca = 2

                        # Punto Medio
                        if xi < linxe < xf and flag2 == 2:
                            print("SALIDA2")
                            # Dibujamos
                            cv2.putText(frame, "SALIENDO", (40, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                            cv2.line(frame, (linxe, yiz), (linxe, yfz), (0, 255, 255), 2)

                            # Activamos bandera 1
                            flag1 = 2

                        elif xi > linxe and flag1 == 2:
                            print("SALIDA3")
                            # Cerramos puerta
                            com.write(c.encode('ascii'))
                            # Reiniciamos marcas y flags
                            marca = 0
                            flag1 = 0
                            flag2 = 0

                            # Contamos vehiculos
                            contacar = contacar - 1

                    break

    # Mostramos FPS
    cv2.imshow('Parqueadero', frame)
    #cv2.imshow('Detector de Carros', np.squeeze(detect.render()))

    # Leemos el teclado
    t = cv2.waitKey(5)
    if t == 27:
        break

cap.release()
cv2.destroyAllWindows()
