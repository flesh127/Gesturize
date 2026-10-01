import time
from collections import defaultdict

import cv2
import mediapipe as mp
import pyautogui

from gesturize.vision.camera import make_recognizer, open_camera
from gesturize.gestures.cursor import CursorTracker, DEBUG_CURSOR, is_pointing
from gesturize.core.debounce import HandGestureTracker
from gesturize.vision.drawing import draw_hand
from gesturize.gestures.palm import DEBUG_PALM, PALM_EXTEND_MARGIN, PALM_MIN_SCORE, min_finger_extension
from gesturize.gestures.pinch import DEBUG_PINCH, MAX_MISSED_FRAMES, PinchDetector
from gesturize.input.calibration import CalibrationRegion, map_to_screen
from gesturize.input.keyboard import KeyboardController
from gesturize.input.mouse import MouseController

WINDOW_NAME = "Gesturize"
FLIP_DISPLAY = True


def should_quit() -> bool:
    return (
        cv2.waitKey(5) & 0xFF == 27  # Esc
        or cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1  # X button
    )


def run_on_webcam():
    recognizer = make_recognizer()
    tracker = HandGestureTracker()
    pinch_detectors: defaultdict[str, PinchDetector] = defaultdict(PinchDetector)
    cursor_trackers: dict[str, CursorTracker] = {}  # one per hand
                                                    # decided to force 1 hand tho
    cap = open_camera()
    start_time = time.time()

    mouse = MouseController()
    keyboard = KeyboardController()
    calibration = CalibrationRegion()
    screen_width, screen_height = pyautogui.size()
    active_hand = None  # whichever hand most recently had cursor_pos; drives mouse clicks

    try:
        while cap.isOpened():
            success, frame_bgr = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            timestamp_ms = int((time.time() - start_time) * 1000)

            result = recognizer.recognize_for_video(mp_image, timestamp_ms)

            detections = {}
            for i, hand_landmarks in enumerate(result.hand_landmarks):
                label = result.handedness[i][0].category_name  # "Left" / "Right"
                gesture = result.gestures[i][0].category_name if result.gestures[i] else "None"

                detector = pinch_detectors[label]
                pinching = detector.update(hand_landmarks, timestamp_ms)

                if DEBUG_PINCH and detector.ratio is not None:
                    print(f"{label}: pinch ratio={detector.ratio:.2f} speed={detector.speed:.2f} alpha={detector.alpha_used:.2f}")

                score = result.gestures[i][0].score if result.gestures[i] else 0.0
                extension = min_finger_extension(hand_landmarks)
                palm_open = gesture == "Open_Palm" and score >= PALM_MIN_SCORE and extension >= PALM_EXTEND_MARGIN

                if DEBUG_PALM:
                    print(f"{label}: gesture={gesture} score={score:.2f} extension={extension:.2f} palm_open={palm_open}")

                pointing = is_pointing(hand_landmarks)
                cursor_pos = None
                if pointing:
                    cursor_pos = cursor_trackers.setdefault(label, CursorTracker()).update(hand_landmarks)
                    if DEBUG_CURSOR:
                        print(f"{label}: cursor=({cursor_pos.x:.2f}, {cursor_pos.y:.2f})")

                    active_hand = label
                    screen_x, screen_y = map_to_screen(cursor_pos, screen_width, screen_height, calibration)
                    mouse.move(screen_x, screen_y)

                detections[label] = {"pinch": pinching, "palm": palm_open}
                draw_hand(frame_bgr, hand_landmarks, pinching, palm_open, cursor_pos)

            # Only drop a hand's smoothing state after several consecutive
            # missed frames, instead of on the first one.
            for label, detector in list(pinch_detectors.items()):
                if label not in detections:
                    detector.missed_frames += 1
                    if detector.missed_frames > MAX_MISSED_FRAMES:
                        del pinch_detectors[label]
                else:
                    detector.missed_frames = 0

            for label in set(cursor_trackers) - set(detections):
                del cursor_trackers[label]

            for label, gesture, state in tracker.update_frame(detections):
                if state.pressed:
                    print(f"{gesture} ON  ({label} hand)")
                elif state.released:
                    print(f"{gesture} OFF ({label} hand)")

                if gesture == "pinch" and label == active_hand:
                    if state.pressed:
                        mouse.press()
                    elif state.released:
                        mouse.release()

                if gesture == "palm" and state.pressed:
                    keyboard.toggle()

            shown = cv2.flip(frame_bgr, 1) if FLIP_DISPLAY else frame_bgr
            cv2.imshow(WINDOW_NAME, shown)
            if should_quit():
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        recognizer.close()


if __name__ == "__main__":
    run_on_webcam()