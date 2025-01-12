import cv2
import paho.mqtt.client as mqtt
from cvzone.HandTrackingModule import HandDetector
import time
import mysql.connector
from datetime import datetime

# Configuración de MQTT
BROKER = "broker.hivemq.com"
TOPIC = "bebida/gesto"
mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER)

IP = "192.168.137.168"

# Configuración de la ESP32-CAM
ESP32_CAM_URL = "http://" + IP + ":81/stream"

# Detector de manos
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Iniciar la conexión con ESP32-CAM
#cap = cv2.VideoCapture(0)  // usa webcam nbk

cap = cv2.VideoCapture(ESP32_CAM_URL) #ESP32

if not cap.isOpened():
    print("Error al conectar con ESP32-CAM.")
    exit()

# Configuración de la conexión a MySQL
db_connection = mysql.connector.connect(
    host="localhost",  # Cambia esto si tu base de datos está en otro servidor
    user="root",  # Tu usuario de la base de datos
    password="my-secret-pw",  # Tu contraseña de la base de datos
    database="sbm"  # Nombre de la base de datos
)

db_cursor = db_connection.cursor()

# Variables de estado
gesture_detected = None
start_time = None
user_identified = False
coffee_exceeded = False
query = "SELECT COUNT(*) FROM Beverage WHERE Name = 'cafe' AND DATE(LogDateTime) = CURDATE()"
insert_query = "INSERT INTO Beverage (Name, LogDateTime) VALUES (%s, %s)"


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
                    # Tiempo expirado, solicitar nueva identificación
                    mqtt_client.publish(TOPIC, "TIMEOUT")                    
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
                        
                        if gesture == "cafe":
                            # Insertar el registro de la bebida "cafe" en la base de datos
                            current_time = datetime.now()
                            db_cursor.execute(insert_query, ("cafe", current_time))
                            db_connection.commit()
                            print("Se registró un café en la base de datos.")
                            # Consultar si existen más de 5 registros de "cafe" hoy
                            db_cursor.execute(query)
                            result = db_cursor.fetchone()
                            count = 0
                            count = result[0]
                            if count > 5:
                                mqtt_client.publish(TOPIC, "up5coffe")
                                print("Se ha excedido el límite de cafés hoy.")
                            else:
                                mqtt_client.publish(TOPIC, gesture)
                        else:
                            mqtt_client.publish(TOPIC, gesture)
                            print(f"Beverage selected: {gesture}")

                                                   
                        # Enviar mensaje de logoff
                        #mqtt_client.publish(TOPIC, "MENSAJE-LOGOFF")
                        print("MENSAJE-LOGOFF")
                        # Resetear el estado
                        user_identified = False
                        start_time = None
                        break

    cv2.imshow("ESP32-CAM", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Cerrar la conexión a la base de datos al finalizar
db_cursor.close()
db_connection.close()
