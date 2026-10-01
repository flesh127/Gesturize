from gesturize.core.geometry import distance
from gesturize.core.landmarks import FINGER_TIP_PIP, WRIST

PALM_MIN_SCORE = 0.55      # minimum classifier confidence for Open_Palm
PALM_EXTEND_MARGIN = 1.28  # fingertip must be this many times farther from the wrist than its PIP
DEBUG_PALM = False


def min_finger_extension(hand_landmarks) -> float:
    wrist = hand_landmarks[WRIST]
    return min(
        distance(wrist, hand_landmarks[tip]) / distance(wrist, hand_landmarks[pip])
        for tip, pip in FINGER_TIP_PIP
    )