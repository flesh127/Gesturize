import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = "gesture_recognizer.task"


def make_recognizer(running_mode=vision.RunningMode.VIDEO, num_hands: int = 1):
    options = vision.GestureRecognizerOptions(
        base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=running_mode,
        num_hands=num_hands,
        min_hand_detection_confidence=0.85,
        min_tracking_confidence=0.85,
    )
    return vision.GestureRecognizer.create_from_options(options)


def open_camera(preferred_indices=(1, 0)) -> cv2.VideoCapture:
    for index in preferred_indices:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            return cap
        cap.release()
    raise RuntimeError("No camera found")