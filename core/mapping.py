# core/mapping.py
from dataclasses import dataclass

@dataclass
class ActiveRegion:
    x0: int
    y0: int
    x1: int
    y1: int

def compute_active_region(frame_w: int, frame_h: int, margin: float) -> ActiveRegion:
    mx = int(frame_w * margin)
    my = int(frame_h * margin)
    return ActiveRegion(mx, my, frame_w - mx, frame_h - my)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def curve01(v: float, gamma: float) -> float:
    # v in [0,1] -> curved [0,1]
    v = clamp(v, 0.0, 1.0)
    return v ** gamma

def map_cam_to_screen(
    x_px: float,
    y_px: float,
    region: ActiveRegion,
    screen_w: int,
    screen_h: int,
    gamma: float = 1.0,
):
    # Clamp into active region
    x_px = clamp(x_px, region.x0, region.x1)
    y_px = clamp(y_px, region.y0, region.y1)

    # Normalize within region
    nx = (x_px - region.x0) / max(1, (region.x1 - region.x0))
    ny = (y_px - region.y0) / max(1, (region.y1 - region.y0))

    # Non-linear curve for precision
    if gamma and gamma != 1.0:
        nx = curve01(nx, gamma)
        ny = curve01(ny, gamma)

    # Map to screen
    sx = int(nx * (screen_w - 1))
    sy = int(ny * (screen_h - 1))
    return sx, sy
