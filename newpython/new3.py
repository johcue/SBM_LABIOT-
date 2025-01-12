import cv2
from cvzone.HandTrackingModule import HandDetector
import controller as cnt  # Controlador para manejar los LEDs

# Inicializar el detector de manos
detector = HandDetector(detectionCon=0.8, maxHands=2)  # Detectar hasta 2 manos

# Inicializar la cámara
video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    frame = cv2.flip(frame, 1)  # Efecto espejo
    hands, img = detector.findHands(frame)  # Detectar manos en el cuadro actual

    # Inicialización del estado de los LEDs
    led_status = [0, 0, 0, 0, 0]

    # Variables para verificar los pulgares
    thumb_right_up = False
    thumb_left_up = False

    if hands:
        for hand in hands:
            hand_type = hand["type"]  # Tipo de mano: "Right" o "Left"
            finger_up = detector.fingersUp(hand)  # Detectar qué dedos están levantados

            # Verificar si sólo el pulgar está levantado
            if finger_up == [1, 1, 0, 0, 0]:
                if hand_type == "Right":
                    thumb_right_up = True  # Pulgar derecho levantado
                elif hand_type == "Left":
                    thumb_left_up = True  # Pulgar izquierdo levantado

    # Controlar los LEDs según el estado de los pulgares
    if thumb_right_up and thumb_left_up:
        led_status = [1, 1, 1, 1, 1]  # Encender todos los LEDs
        cv2.putText(frame, 'Thumbs: Both', (20, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    elif thumb_right_up:
        led_status = [1, 0, 0, 0, 0]  # Encender el primer LED
        cv2.putText(frame, 'Thumb: Right', (20, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    elif thumb_left_up:
        led_status= [0, 0, 0, 0, 1]  # Encender el último LED
        cv2.putText(frame, 'Thumb: Left', (20, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

    # Enviar el estado de los LEDs al controlador
    cnt.led(led_status)

    # Mostrar el cuadro en pantalla
    cv2.imshow("frame", frame)
    k = cv2.waitKey(1)
    if k == ord("k"):  # Presionar "k" para salir
        break

# Liberar recursos
video.release()
cv2.destroyAllWindows()
