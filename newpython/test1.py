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
#ESP32_CAM_URL = "http://192.168.1.101:81/stream"

ESP32_CAM_URL = "http://192.168.1.143:81/stream"


# Detector de manos
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Iniciar la conexión con ESP32-CAM
cap = cv2.VideoCapture(ESP32_CAM_URL)


if not cap.isOpened():
    print("Error al conectar con ESP32-CAM.")
    exit()

gesture_detected = None
start_time = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al recibir imágenes de ESP32-CAM.")
        break

    hands, img = detector.findHands(frame)

    if hands:
        fingers = detector.fingersUp(hands[0])
        if fingers == [0, 1, 0, 0, 0]:  # Un dedo
            gesture = "cafe"
        elif fingers == [0, 0, 0, 0, 0]:  # Dos dedos
            gesture = "leche"
        elif fingers == [0, 1, 1, 0, 0]:  # Tres dedos
            gesture = "cafe_leche"
        else:
            gesture = None

        print(gesture)
        if gesture == gesture_detected:
            if start_time and time.time() - start_time >= 3:
                mqtt_client.publish(TOPIC, gesture)
                gesture_detected = None
                start_time = None
        else:
            gesture_detected = gesture
            start_time = time.time()

    cv2.imshow("ESP32-CAM", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
