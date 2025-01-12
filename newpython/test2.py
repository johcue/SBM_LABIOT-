import cv2
import paho.mqtt.client as mqtt
from cvzone.HandTrackingModule import HandDetector
import time

# Configuración de MQTT
BROKER = "broker.hivemq.com"
TOPIC = "bebida/gesto"
mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER)

# Configuración de la ESP32-CAM
#ESP32_CAM_URL = "http://192.168.137.24:81/stream"
ESP32_CAM_URL = "http://192.168.137.185:81/stream"

# Detector de manos
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Iniciar la conexión con ESP32-CAM
#cap = cv2.VideoCapture(0)  // usa webcam nbk
cap = cv2.VideoCapture(0)


if not cap.isOpened():
    print("Error al conectar con ESP32-CAM.")
    exit()

# Variables de estado
gesture_detected = None
start_time = None
user_identified = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al recibir imágenes de ESP32-CAM.")
        break

    hands, img = detector.findHands(frame)


    if hands:
        for hand in hands:
            hand_type = hand["type"]  # "Left" o "Right"
            fingers = detector.fingersUp(hand)

            if not user_identified:
                # Detectar palma de la mano izquierda abierta para identificación
                if hand_type == "Left" and fingers == [1, 1, 1, 1, 1]:
                    user_identified = True                    
                    mqtt_client.publish(TOPIC, "MENSAJE-LOGIN")                    
                    print("MENSAJE-LOGIN")
                    start_time = time.time()
                    break

            elif user_identified:
                if time.time() - start_time > 10:
                    #TODO enviar mensaje TIMEOUT, para pedir identificar
                    print("Tiempo expirado. Por favor, identifíquese nuevamente.")
                    user_identified = False
                    start_time = None
                    break

                elif hand_type == "Right":
                # Detectar gestos de selección de bebida con la mano derecha
                     
                        if fingers == [0, 1, 0, 0, 0]:
                            gesture = "cafe"
                        elif fingers == [0, 0, 0, 0, 0]:
                            gesture = "leche"
                        elif fingers == [0, 1, 1, 0, 0]:
                            gesture = "cafe_leche"
                        else:
                            gesture = None

                        if gesture:
                            mqtt_client.publish(TOPIC, gesture)
                            print(f"Bebida seleccionada: {gesture}")

                            # Enviar mensaje de logoff
                            mqtt_client.publish(TOPIC, "MENSAJE-LOGOFF")
                            print("MENSAJE-LOGOFF")
                            #TODO agregar en Arduino "MENSAJE-LOGOFF" = display "Gracias, disfrute su bebida"

                            # Resetear el estado
                            user_identified = False
                            start_time = None
                            break

                
    cv2.imshow("ESP32-CAM", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
