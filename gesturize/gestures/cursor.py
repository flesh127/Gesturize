from gesturize.core.geometry import Point, distance
from gesturize.core.landmarks import FINGER_TIP_MCP, INDEX_MCP, WRIST

CURSOR_REF = INDEX_MCP  # point tracked for cursor position (expected to stay stable during pinch)
CURSOR_ALPHA = 0.4      # smoothing for cursor position, separate from pinch's alpha

POINT_Z_WEIGHT = 1.0  # 3d z noise is outweighed by 2d curl error (0 -> 2d, 1 -> 3d distance calculation)
POINT_EXTEND_MARGIN = 1.1  # wrist->TIP / wrist->MCP ratio for the index finger
POINT_CURL_MARGIN = 1.1    # wrist->TIP / wrist->MCP ratio for the other three fingers
DEBUG_CURSOR = False


def is_pointing(hand_landmarks) -> bool:
    wrist = hand_landmarks[WRIST]
    index_tip, index_mcp = FINGER_TIP_MCP[0]
    index_ok = distance(wrist, hand_landmarks[index_tip], POINT_Z_WEIGHT) >= POINT_EXTEND_MARGIN * distance(
        wrist, hand_landmarks[index_mcp], POINT_Z_WEIGHT
    )
    others_ok = all(
        distance(wrist, hand_landmarks[tip], POINT_Z_WEIGHT) < POINT_CURL_MARGIN * distance(wrist, hand_landmarks[mcp], POINT_Z_WEIGHT)
        for tip, mcp in FINGER_TIP_MCP[1:]
    )
    return index_ok and others_ok


class CursorTracker:
    def __init__(self, alpha: float = CURSOR_ALPHA):
        self.alpha = alpha
        self.position: Point | None = None

    def update(self, hand_landmarks) -> Point:
        raw = hand_landmarks[CURSOR_REF]
        if self.position is None:
            self.position = Point(raw.x, raw.y, raw.z)
        else:
            self.position = Point(
                self.alpha * raw.x + (1 - self.alpha) * self.position.x,
                self.alpha * raw.y + (1 - self.alpha) * self.position.y,
                self.alpha * raw.z + (1 - self.alpha) * self.position.z,
            )
        return self.position