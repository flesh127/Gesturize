import math
from collections import namedtuple

from gesturize.core.landmarks import WRIST, INDEX_MCP, PINKY_MCP

Z_WEIGHT = 0.2  # MediaPipe's z is noisy. 1.0 = full 3D, 0.0 = pure 2D

Point = namedtuple("Point", ["x", "y", "z"])


def distance(a, b, z_weight: float = Z_WEIGHT) -> float:
    return math.hypot(a.x - b.x, a.y - b.y, z_weight * (a.z - b.z))


def midpoint(a, b) -> Point:
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2)


def hand_scale(hand_landmarks) -> float:
    wrist = hand_landmarks[WRIST]
    index_mcp = hand_landmarks[INDEX_MCP]
    pinky_mcp = hand_landmarks[PINKY_MCP]
    return (
        distance(wrist, index_mcp)
        + distance(wrist, pinky_mcp)
        + distance(index_mcp, pinky_mcp)
    ) / 3


def hand_speed(prev_center, center, scale: float, dt_s: float) -> float:
    # z ignored since its too too noisy
    if prev_center is None or dt_s <= 0 or scale == 0:
        return 0.0
    return distance(prev_center, center, 0.0) / scale / dt_s