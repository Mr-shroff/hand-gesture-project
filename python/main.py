import cv2
import mediapipe as mp
import serial
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# Arduino connection
arduino = serial.Serial("COM3", 9600)

time.sleep(2)

print("Arduino connected!")


# MediaPipe
base_options = python.BaseOptions(
    model_asset_path="hand_landmarker.task"
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

detector = vision.HandLandmarker.create_from_options(options)


# Camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open camera.")
    arduino.close()
    detector.close()
    exit()


start_time = time.time()


# Hand skeleton
connections = [
    (0, 1), (1, 2), (2, 3), (3, 4),

    (0, 5), (5, 6), (6, 7), (7, 8),

    (0, 9), (9, 10), (10, 11), (11, 12),

    (0, 13), (13, 14), (14, 15), (15, 16),

    (0, 17), (17, 18), (18, 19), (19, 20),

    (5, 9),
    (9, 13),
    (13, 17)
]


# Variables
last_finger_count = -1

brightness = 255

last_wrist_y = None

movement_threshold = 25

last_brightness_change = 0

brightness_delay = 0.25


while True:

    success, frame = cap.read()

    if not success:
        print("Could not read camera.")
        break


    # Mirror camera
    frame = cv2.flip(frame, 1)


    # Convert image
    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )


    # Timestamp
    timestamp_ms = int(
        (time.time() - start_time) * 1000
    )


    # Detect hand
    result = detector.detect_for_video(
        mp_image,
        timestamp_ms
    )


    finger_count = 0


    if result.hand_landmarks:

        hand = result.hand_landmarks[0]

        h, w, _ = frame.shape


        # Convert landmarks to pixels
        points = []

        for landmark in hand:

            x = int(landmark.x * w)
            y = int(landmark.y * h)

            points.append((x, y))


        # Draw green skeleton lines
        for start, end in connections:

            cv2.line(
                frame,
                points[start],
                points[end],
                (0, 255, 0),
                3
            )


        # Finger counting

        # Index
        if hand[8].y < hand[6].y:
            finger_count += 1

        # Middle
        if hand[12].y < hand[10].y:
            finger_count += 1

        # Ring
        if hand[16].y < hand[14].y:
            finger_count += 1

        # Pinky
        if hand[20].y < hand[18].y:
            finger_count += 1

        # Thumb
        if hand[4].x < hand[3].x:
            finger_count += 1


        # Send LED command when finger count changes
        if finger_count != last_finger_count:

            command = f"L{finger_count}\n"

            arduino.write(
                command.encode()
            )

            print(
                f"Fingers: {finger_count}"
            )

            last_finger_count = finger_count


        # ==================================
        # BRIGHTNESS CONTROL
        # ==================================

        if finger_count == 0:

            wrist_y = points[0][1]


            if last_wrist_y is not None:

                movement = last_wrist_y - wrist_y

                current_time = time.time()


                # Move UP
                if (
                    movement > movement_threshold
                    and
                    current_time - last_brightness_change
                    > brightness_delay
                ):

                    brightness += 15

                    if brightness > 255:
                        brightness = 255


                    command = f"B{brightness}\n"

                    arduino.write(
                        command.encode()
                    )


                    print(
                        f"UP → Brightness: {brightness}"
                    )


                    last_brightness_change = current_time


                # Move DOWN
                elif (
                    movement < -movement_threshold
                    and
                    current_time - last_brightness_change
                    > brightness_delay
                ):

                    brightness -= 15

                    if brightness < 0:
                        brightness = 0


                    command = f"B{brightness}\n"

                    arduino.write(
                        command.encode()
                    )


                    print(
                        f"DOWN → Brightness: {brightness}"
                    )


                    last_brightness_change = current_time


            last_wrist_y = wrist_y


        else:

            last_wrist_y = None


    else:

        last_wrist_y = None


    # Display finger count
    cv2.putText(
        frame,
        f"Fingers: {finger_count}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


    # Display brightness
    cv2.putText(
        frame,
        f"Brightness: {brightness}/255",
        (30, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # Instructions
    cv2.putText(
        frame,
        "Fist UP = Brighter",
        (30, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Fist DOWN = Dimmer",
        (30, 155),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Q = Quit",
        (30, 185),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    # Show camera
    cv2.imshow(
        "Hand Gesture LED Control",
        frame
    )


    # Quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Cleanup
cap.release()
cv2.destroyAllWindows()

arduino.close()
detector.close()

print("System stopped.")