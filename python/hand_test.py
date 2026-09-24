import cv2
import mediapipe as mp
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# Load the hand model
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


# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open camera.")
    detector.close()
    exit()


start_time = time.time()


# MediaPipe hand connections
connections = [
    # Thumb
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),

    # Index finger
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),

    # Middle finger
    (0, 9),
    (9, 10),
    (10, 11),
    (11, 12),

    # Ring finger
    (0, 13),
    (13, 14),
    (14, 15),
    (15, 16),

    # Pinky
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),

    # Palm
    (5, 9),
    (9, 13),
    (13, 17)
]


while True:

    # Read camera
    success, frame = cap.read()

    if not success:
        print("Could not read camera.")
        break


    # Mirror the camera
    frame = cv2.flip(frame, 1)


    # Convert BGR to RGB
    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # Create MediaPipe image
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


    # Check if a hand was detected
    if result.hand_landmarks:

        h, w, _ = frame.shape

        hand = result.hand_landmarks[0]


        # Convert landmarks to pixel positions
        points = []

        for landmark in hand:

            x = int(landmark.x * w)
            y = int(landmark.y * h)

            points.append((x, y))


        # Draw ONLY green lines
        for start, end in connections:

            cv2.line(
                frame,
                points[start],
                points[end],
                (0, 255, 0),
                3
            )


    # Text
    cv2.putText(
        frame,
        "Hand Skeleton",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        "Press Q to quit",
        (30, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # Show camera
    cv2.imshow(
        "Hand Skeleton",
        frame
    )


    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Close everything
cap.release()
cv2.destroyAllWindows()
detector.close()

print("Camera closed.")