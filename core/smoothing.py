# core/smoothing.py
from dataclasses import dataclass

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

@dataclass
class SmoothState:
    x: float | None = None
    y: float | None = None

class CursorSmoother:
    def __init__(self, alpha: float, deadzone_px: int, max_step_px: int):
        self.alpha = alpha
        self.deadzone = deadzone_px
        self.max_step = max_step_px
        self.state = SmoothState()

    def update(self, target_x: int, target_y: int):
        if self.state.x is None or self.state.y is None:
            self.state.x, self.state.y = float(target_x), float(target_y)
            return int(self.state.x), int(self.state.y)

        dx = target_x - self.state.x
        dy = target_y - self.state.y

        # Deadzone
        if abs(dx) < self.deadzone:
            dx = 0
        if abs(dy) < self.deadzone:
            dy = 0

        # Step cap
        dx = _clamp(dx, -self.max_step, self.max_step)
        dy = _clamp(dy, -self.max_step, self.max_step)

        # EMA
        self.state.x = (1 - self.alpha) * self.state.x + self.alpha * (self.state.x + dx)
        self.state.y = (1 - self.alpha) * self.state.y + self.alpha * (self.state.y + dy)

        return int(self.state.x), int(self.state.y)
