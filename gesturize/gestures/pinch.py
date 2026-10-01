"""Pinch (click) detection: normalized distance, smoothing, and speed-adaptive alpha."""

from gesturize.core.geometry import Point, distance, hand_scale, hand_speed, midpoint
from gesturize.core.landmarks import INDEX_TIP, MIDDLE_MCP, THUMB_TIP, WRIST

# Pinch tuning
PINCH_ON = 0.28         # ratio must drop below this to START a pinch
PINCH_OFF = 0.35        # ratio must rise above this to END a pinch
PINCH_ALPHA = 0.5       # smoothing: weight on the newest sample (1 -> no smoothing)
SPEED_GAIN = 2          # how strongly hand speed (hand-lengths/sec) lowers alpha; 0 = no effect
PINCH_MIN_ALPHA = 0.05  # alpha never drops below this, so the ratio can't freeze completely
MAX_MISSED_FRAMES = 3   # tolerate this many dropped frames before resetting pinch smoothing state
DEBUG_PINCH = False      # print the smoothed ratio to pick thresholds from real data


def pinch_ratio(hand_landmarks) -> float | None:
    scale = hand_scale(hand_landmarks)
    if scale == 0:
        return None
    # smaller = tighter pinch
    return distance(hand_landmarks[INDEX_TIP], hand_landmarks[THUMB_TIP]) / scale


class PinchDetector:
    def __init__(
        self,
        on: float = PINCH_ON,
        off: float = PINCH_OFF,
        alpha: float = PINCH_ALPHA,
        speed_gain: float = SPEED_GAIN,
        min_alpha: float = PINCH_MIN_ALPHA,
    ):
        self.on = on
        self.off = off
        self.alpha = alpha
        self.speed_gain = speed_gain
        self.min_alpha = min_alpha
        self.ratio: float | None = None
        self.pinching = False
        self.prev_center: Point | None = None
        self.prev_time_ms: float | None = None
        self.speed = 0.0
        self.alpha_used = alpha
        self.missed_frames = 0  # consecutive frames this hand was not detected

    def update(self, hand_landmarks, timestamp_ms: float) -> bool:
        raw = pinch_ratio(hand_landmarks)
        if raw is None:
            self.ratio, self.pinching = None, False
            self.prev_center, self.prev_time_ms = None, None
            return False

        center = midpoint(hand_landmarks[WRIST], hand_landmarks[MIDDLE_MCP])
        dt_s = 0.0 if self.prev_time_ms is None else (timestamp_ms - self.prev_time_ms) / 1000
        self.speed = hand_speed(self.prev_center, center, hand_scale(hand_landmarks), dt_s)
        self.prev_center, self.prev_time_ms = center, timestamp_ms

        self.alpha_used = max(self.min_alpha, self.alpha / (1 + self.speed_gain * self.speed))

        if self.ratio is None:
            self.ratio = raw
        else:
            self.ratio = self.alpha_used * raw + (1 - self.alpha_used) * self.ratio

        self.pinching = self.ratio < (self.off if self.pinching else self.on)
        return self.pinching