# core/sensitivity.py

def apply_mouse_speed(x: int, y: int, screen_w: int, screen_h: int, speed: float):
    """
    Scales movement around the screen center.
    speed=1.0 => no change
    speed>1.0 => more sensitive (less hand movement needed)
    speed<1.0 => less sensitive
    """
    cx, cy = screen_w // 2, screen_h // 2

    sx = int(cx + (x - cx) * speed)
    sy = int(cy + (y - cy) * speed)

    sx = max(0, min(screen_w - 1, sx))
    sy = max(0, min(screen_h - 1, sy))
    return sx, sy
