# Gesture detection for the robotic arm (Taller de Electrónica I, Universidad de Ibagué, 2023).
#
# Transcribed from the screenshots in the annex of the original project report; the original
# source file was lost. This version detects the gestures and prints them. In the final build
# the same results were sent to the ESP32 over serial (PySerial); that part and the ESP32
# firmware (MicroPython) were not included in the report.
#
#   Right hand: turn direction from the middle fingertip vs. the wrist  ->  quto / derecha / izquierda
#   Left hand:  number of raised fingers (0-5)                          ->  which motor to move
#
# Requirements: pip install opencv-python mediapipe

# librerias
import cv2
import mediapipe as mp
import time

# inicializacion de mediapipe
mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
# captura de video con opencv
cap = cv2.VideoCapture(0)
# cosas importantes
ptiempo = 0
ctiempo = 0
# puntos de interes de cada dedo
puntas_dedos = [4, 8, 12, 16, 20]
segunda_linea = [2, 6, 10, 16, 18]
base_mano = 0
# parametros inciales de mediapipe solution hands
with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        model_complexity=1,
        min_tracking_confidence=0.6) as manos:

    while True:
        ret, frame = cap.read()
        alto, ancho, z = frame.shape
        frame = cv2.flip(frame, 1)
        frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = manos.process(frame_RGB)  # 3 salidas handedness, landmarks, world landmarks
        # Los landmarks se numeran del 0 al 20, y el punto de referencia más importante para distinguir
        # entre la mano derecha y la izquierda es el landmark[0] y el landmark[17].
        # Estos landmarks corresponden al extremo de la muñeca. Si el landmark[0] (muñeca izquierda)
        # tiene una coordenada x menor que el landmark[17] (muñeca derecha), entonces estás tratando con la
        # mano izquierda. Si el landmark[0] tiene una coordenada x mayor que el landmark[17], entonces estás
        # tratando con la mano derecha.
        if resultados.multi_hand_landmarks:
            coor_puntasD = [0, 0, 0, 0, 0]
            coor_lineaD = [0, 0, 0, 0, 0]
            coor_baseD = [0]
            coor_puntasZ = [0, 0, 0, 0, 0]
            coor_lineaZ = [0, 0, 0, 0, 0]
            coor_baseZ = [0]
            for hand_landmarks in resultados.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                for landmark in hand_landmarks.landmark:
                    # Mano derecha
                    # if hand_landmarks.landmark[0].x < (hand_landmarks.landmark[17].x + 5):
                    handedness = resultados.multi_handedness
                    for hand in handedness:
                        if hand.classification[0].label == "Right":
                            quto = 0
                            izqui = 0
                            dere = 0
                            # cordenadas de los puntos de interes
                            for j in range(len(puntas_dedos)):
                                i = puntas_dedos[j]
                                x = int(hand_landmarks.landmark[i].x * ancho)
                                y = int(hand_landmarks.landmark[i].y * alto)
                                coor_puntasD[j] = ([x, y])
                            for j in range(len(segunda_linea)):
                                i = segunda_linea[j]
                                x = int(hand_landmarks.landmark[i].x * ancho)
                                y = int(hand_landmarks.landmark[i].y * alto)
                                coor_lineaD[j] = ([x, y])
                            x = int(hand_landmarks.landmark[0].x * ancho)
                            y = int(hand_landmarks.landmark[0].y * alto)
                            coor_baseD[0] = ([x, y])
                            ###########################################
                            # giro derecha o izquierda
                            if (coor_baseD[0][0]-30) < coor_puntasD[2][0] < (coor_baseD[0][0]+30):
                                quto = 1
                            elif (coor_baseD[0][0]-10) > coor_puntasD[2][0]:
                                izqui = 1
                            else:
                                dere = 1
                            print("Nada= %r derecha= %r izquierda= %r" % (quto, dere, izqui))
                            ###########################################################################
                        elif hand_landmarks.landmark[0].x > hand_landmarks.landmark[17].x:
                            dedos = 0
                            # cordenadas de los puntos de interes
                            for j in range(len(puntas_dedos)):
                                i = puntas_dedos[j]
                                x = int(hand_landmarks.landmark[i].x * ancho)
                                y = int(hand_landmarks.landmark[i].y * alto)
                                coor_puntasZ[j] = ([x, y])
                            for j in range(len(segunda_linea)):
                                i = segunda_linea[j]
                                x = int(hand_landmarks.landmark[i].x * ancho)
                                y = int(hand_landmarks.landmark[i].y * alto)
                                coor_lineaZ[j] = ([x, y])
                            x = int(hand_landmarks.landmark[0].x * ancho)
                            y = int(hand_landmarks.landmark[0].y * alto)
                            coor_baseZ[0] = ([x, y])
                            ###########################################
                            # motor a mover
                            if coor_puntasZ[1][1] < coor_lineaZ[1][1]:
                                dedos = dedos + 1
                            if coor_puntasZ[2][1] < coor_lineaZ[2][1]:
                                dedos = dedos + 1
                            if coor_puntasZ[3][1] < coor_lineaZ[3][1]:
                                dedos = dedos + 1
                            if coor_puntasZ[4][1] < coor_lineaZ[4][1]:
                                dedos = dedos + 1
                            if coor_puntasZ[0][0] > coor_lineaZ[0][0]:
                                dedos = dedos + 1
                            print("dedos= ", dedos)
                            ###########################################
        # mostrar fps
        ctiempo = time.time()
        fps = 1/(ctiempo - ptiempo)
        ptiempo = ctiempo
        cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        # salida
        cv2.imshow("frame", frame)
        k = cv2.waitKey(1)
        if k == 27:
            break

    # print('Mano derecha: ', coor_puntasD, '\n', coor_lineaD, '\n', coor_baseD)
    # print('Mano izquierda: ', coor_puntasZ, '\n', coor_lineaZ, '\n', coor_baseZ)
    cap.release()
    cv2.destroyAllWindows()
