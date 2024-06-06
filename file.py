import cv2
import mediapipe as mp
import RPi.GPIO as GPIO

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)

# Define motor control functions
def forward():
    GPIO.output(3, 1)
    GPIO.output(5, 0)
    GPIO.output(8, 1)
    GPIO.output(10, 0)
    print("Moving Forward")

def backward():
    GPIO.output(3, 0)
    GPIO.output(5, 1)
    GPIO.output(8, 0)
    GPIO.output(10, 1)
    print("Moving Backward")

def stop():
    GPIO.output(3, 0)
    GPIO.output(5, 0)
    GPIO.output(8, 0)
    GPIO.output(10, 0)
    print("Stopped")

def right():
    GPIO.output(3, 1)
    GPIO.output(5, 0)
    GPIO.output(8, 0)
    GPIO.output(10, 0)
    print("Turning Right")

def left():
    GPIO.output(3, 0)
    GPIO.output(5, 0)
    GPIO.output(8, 1)
    GPIO.output(10, 0)
    print("Turning Left")

# Initialize MediaPipe Hand module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Start capturing video from webcam
cap = cv2.VideoCapture(0)

def count_fingers(lm_list):
    fingers = []
    # Thumb
    if lm_list[4][1] > lm_list[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)
    # Fingers
    for tip in [8, 12, 16, 20]:
        if lm_list[tip][2] < lm_list[tip - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers.count(1)

while True:
    success, img = cap.read()
    if not success:
        break

    # Convert the image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process the image and detect hands
    result = hands.process(img_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Get landmark positions
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))

            if lm_list:
                # Count fingers
                fingers_count = count_fingers(lm_list)

                # Execute commands based on the number of fingers
                if fingers_count == 1:
                    forward()
                elif fingers_count == 2:
                    backward()
                elif fingers_count == 3:
                    left()
                elif fingers_count == 4:
                    right()
                else:
                    stop()

            # Draw landmarks on image
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Show the image
    cv2.imshow("Hand Tracking", img)

    # Break the loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()
