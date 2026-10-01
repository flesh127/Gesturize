import cv2
from mediapipe.tasks.python import vision

from gesturize.core.geometry import Point, midpoint
from gesturize.core.landmarks import INDEX_TIP, MIDDLE_MCP, THUMB_TIP, WRIST

HAND_CONNECTIONS = vision.HandLandmarksConnections.HAND_CONNECTIONS


def draw_hand(image, hand_landmarks, pinching: bool, palm_open: bool, cursor_pos: Point | None = None):
    h, w, _ = image.shape
    points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]

    for connection in HAND_CONNECTIONS:
        cv2.line(image, points[connection.start], points[connection.end], (255, 255, 255), 2)

    for point in points:
        cv2.circle(image, point, 4, (0, 255, 0), -1)

    if pinching:
        mid = midpoint(hand_landmarks[INDEX_TIP], hand_landmarks[THUMB_TIP])
        cv2.circle(image, (int(mid.x * w), int(mid.y * h)), 4, (255, 0, 0), -1)

    if palm_open:
        mid = midpoint(hand_landmarks[WRIST], hand_landmarks[MIDDLE_MCP])
        cv2.circle(image, (int(mid.x * w), int(mid.y * h)), 4, (255, 0, 0), -1)

    if cursor_pos is not None:
        cv2.circle(image, (int(cursor_pos.x * w), int(cursor_pos.y * h)), 6, (0, 255, 255), 2)