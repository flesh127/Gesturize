from dataclasses import dataclass

from gesturize.core.geometry import Point


@dataclass
class CalibrationRegion:
    # cam boundaries; really depends on how well mediapipe predicts hand's position,
    # so needs to be calibrated accordingly
    x_min: float = 0.2
    x_max: float = 0.8
    y_min: float = 0.3 
    y_max: float = 0.7
    invert_x: bool = True
    invert_y: bool = False


def map_to_screen(
    point: Point,
    screen_width: int,
    screen_height: int,
    region: CalibrationRegion = CalibrationRegion(),
) -> tuple[int, int]:
    x_span = region.x_max - region.x_min
    y_span = region.y_max - region.y_min
    if x_span == 0 or y_span == 0:
        raise ValueError("CalibrationRegion must have non-zero width and height")

    x_norm = (point.x - region.x_min) / x_span
    y_norm = (point.y - region.y_min) / y_span
    x_norm = min(1.0, max(0.0, x_norm))
    y_norm = min(1.0, max(0.0, y_norm))

    if region.invert_x:
        x_norm = 1.0 - x_norm
    if region.invert_y:
        y_norm = 1.0 - y_norm

    screen_x = int(x_norm * (screen_width - 1))
    screen_y = int(y_norm * (screen_height - 1))
    return screen_x, screen_y
