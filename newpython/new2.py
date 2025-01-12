import cv2
from cvzone.HandTrackingModule import HandDetector
import controller as cnt  # Controlador para manejar los LEDs

# Inicializar el detector de manos
detector = HandDetector(detectionCon=0.8, maxHands=2)  # Permitimos detectar hasta 2 manos

# Inicializar la cámara
video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    frame = cv2.flip(frame, 1)  # Efecto espejo
    hands, img = detector.findHands(frame)  # Detectar manos en el cuadro actual

    # Inicialización del estado de los LEDs
    led_status = [0, 0, 0, 0, 0]

    if hands:
        for hand in hands:
            hand_type = hand["type"]  # Tipo de mano: "Right" o "Left"
            finger_up = detector.fingersUp(hand)  # Detectar qué dedos están levantados

            # Verificar si sólo el pulgar está levantado
            if finger_up == [1, 0, 0, 0, 0]:
                if hand_type == "Right":
                    led_status[0] = 1  # Encender el primer LED
                    led_status[1] = 1  # Encender el segundo LED
                elif hand_type == "Left":
                    led_status[3] = 1  # Encender el cuarto LED
                    led_status[4] = 1  # Encender el quinto LED

    # Si ambas manos están detectadas y sólo los pulgares están levantados
    if len(hands) == 2:
        finger_up_right = detector.fingersUp(hands[0])
        finger_up_left = detector.fingersUp(hands[1])
        if finger_up_right == [1, 0, 0, 0, 0] and finger_up_left == [1, 0, 0, 0, 0]:
            led_status = [1, 1, 1, 1, 1]  # Encender todos los LEDs

    # Enviar el estado de los LEDs al controlador
    cnt.led(led_status)

    # Mostrar el estado en el marco
    if led_status == [1, 1, 1, 1, 1]:
        cv2.putText(frame, 'Thumbs: Both', (20, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    elif led_status[0] == 1 and led_status[1] == 1:
        cv2.putText(frame, 'Thumb: Right', (20, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    elif led_status[3] == 1 and led_status[4] == 1:
        cv2.putText(frame, 'Thumb: Left', (20, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow("frame", frame)
    k = cv2.waitKey(1)
    if k == ord("k"):  # Presionar "k" para salir
        break

# Liberar recursos
video.release()
cv2.destroyAllWindows()
