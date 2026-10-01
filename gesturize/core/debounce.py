from dataclasses import dataclass

DEBOUNCE_FRAMES = {"pinch": (3, 5), "palm": (10, 5)}  # (press, release) per gesture


@dataclass(frozen=True)
class GestureState:
    held: bool = False      # gesture is currently confirmed
    pressed: bool = False   # True only on the frame it becomes confirmed
    released: bool = False  # True only on the frame it stops being confirmed


class GestureDebouncer:
    def __init__(self, press_frames: int = DEBOUNCE_FRAMES["pinch"][0], release_frames: int = DEBOUNCE_FRAMES["pinch"][1]):
        self.press_frames = press_frames
        self.release_frames = release_frames
        self.active_count = 0
        self.inactive_count = 0
        self.state = GestureState()

    def update(self, is_active: bool) -> GestureState:
        if is_active:
            self.active_count = min(self.active_count + 1, self.press_frames)
            self.inactive_count = 0
        else:
            self.inactive_count = min(self.inactive_count + 1, self.release_frames)
            self.active_count = 0

        was_held = self.state.held
        if not was_held and self.active_count >= self.press_frames:
            held = True
        elif was_held and self.inactive_count >= self.release_frames:
            held = False
        else:
            held = was_held 

        self.state = GestureState(
            held=held,
            pressed=held and not was_held,
            released=was_held and not held,
        )
        return self.state


class HandGestureTracker:
    def __init__(self):
        self.debouncers: dict[tuple[str, str], GestureDebouncer] = {}

    def update_frame(self, detections: dict[str, dict[str, bool]]):
        # detections: {hand_label: {gesture_name: is_active}}
        keys = set(self.debouncers)
        keys |= {(label, g) for label, gestures in detections.items() for g in gestures}

        events = []
        for label, gesture in keys:
            active = detections.get(label, {}).get(gesture, False)
            if (label, gesture) not in self.debouncers:
                press, release = DEBOUNCE_FRAMES.get(gesture, DEBOUNCE_FRAMES["pinch"])
                self.debouncers[(label, gesture)] = GestureDebouncer(press, release)
            state = self.debouncers[(label, gesture)].update(active)
            if state.pressed or state.released:
                events.append((label, gesture, state))
        return events