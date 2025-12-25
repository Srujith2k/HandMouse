# gestures/recognizer.py
import math

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

class GestureRecognizer:
    def __init__(
        self,
        pinch_start_ratio=0.30,
        pinch_end_ratio=0.40,
        pinch_click_ms=120,
        pinch_drag_ms=480,
        click_debounce_ms=250,
        click_max_move_px=35,

        # scroll mode (thumb+pinky)
        scroll_start_ratio=0.32,
        scroll_end_ratio=0.42,
        scroll_px_per_step=22,
        scroll_max_step=6,
    ):
        # click/drag
        self.start_ratio = pinch_start_ratio
        self.end_ratio = pinch_end_ratio
        self.pinch_click_ms = pinch_click_ms
        self.pinch_drag_ms = pinch_drag_ms
        self.click_debounce_ms = click_debounce_ms
        self.click_max_move_px = click_max_move_px

        # scroll
        self.s_start = scroll_start_ratio
        self.s_end = scroll_end_ratio
        self.scroll_px_per_step = max(6, int(scroll_px_per_step))
        self.scroll_max_step = int(scroll_max_step)

        self._last_click_ms = 0

        # Middle pinch state (left click + drag)
        self._mid_pinched = False
        self._mid_start_ms = None
        self._mid_start_cursor = None
        self._mid_moved = False
        self._dragging = False

        # Ring pinch state (right click)
        self._ring_pinched = False
        self._ring_start_ms = None
        self._ring_start_cursor = None
        self._ring_moved = False

        # Pinky pinch state (scroll mode)
        self._scrolling = False
        self._scroll_last_y = None
        self._scroll_accum = 0.0

    def _pinch_state(self, ratio: float, currently_pinched: bool, start_ratio: float, end_ratio: float) -> bool:
        # hysteresis: start below start_ratio; remain until above end_ratio
        if currently_pinched:
            return ratio < end_ratio
        return ratio < start_ratio

    def update(self, hand, now_ms: int, cursor_xy: tuple[int, int]):
        pts = hand["landmarks"]

        thumb = pts[4]
        middle_tip = pts[12]  # left click + drag
        ring_tip = pts[16]    # right click
        pinky_tip = pts[20]   # scroll mode

        # Palm width proxy (scale-invariant)
        index_mcp = pts[5]
        pinky_mcp = pts[17]
        palm_w = max(dist(index_mcp, pinky_mcp), 1.0)

        mid_ratio = dist(thumb, middle_tip) / palm_w
        ring_ratio = dist(thumb, ring_tip) / palm_w
        pinky_ratio = dist(thumb, pinky_tip) / palm_w

        mid_pinch = self._pinch_state(mid_ratio, self._mid_pinched, self.start_ratio, self.end_ratio)
        ring_pinch = self._pinch_state(ring_ratio, self._ring_pinched, self.start_ratio, self.end_ratio)
        scroll_pinch = self._pinch_state(pinky_ratio, self._scrolling, self.s_start, self.s_end)

        cx, cy = cursor_xy

        out = {
            "left_click": False,
            "right_click": False,
            "drag_start": False,
            "drag_end": False,
            "scroll": 0,   # dy steps (pynput: +up, -down)
        }

        # -------------------------
        # Scroll Mode (thumb + pinky pinch)
        # -------------------------
        if scroll_pinch and not self._scrolling:
            self._scrolling = True
            # Use middle_tip y as the scroll tracker (stable); could use index_tip too
            self._scroll_last_y = middle_tip[1]
            self._scroll_accum = 0.0

        if self._scrolling and scroll_pinch:
            y = middle_tip[1]
            dy = y - (self._scroll_last_y if self._scroll_last_y is not None else y)
            self._scroll_last_y = y

            self._scroll_accum += dy

            # Convert accumulated camera pixels -> wheel steps
            steps = int(self._scroll_accum / self.scroll_px_per_step)

            if steps != 0:
                # finger moves DOWN (dy positive) => scroll DOWN => wheel dy negative
                wheel = -steps

                # cap to avoid bursts
                if wheel > self.scroll_max_step:
                    wheel = self.scroll_max_step
                elif wheel < -self.scroll_max_step:
                    wheel = -self.scroll_max_step

                out["scroll"] = wheel
                self._scroll_accum -= steps * self.scroll_px_per_step

        if self._scrolling and not scroll_pinch:
            self._scrolling = False
            self._scroll_last_y = None
            self._scroll_accum = 0.0

        # If scrolling, suppress click/drag recognition to avoid conflicts
        if self._scrolling:
            return out

        # -------------------------
        # Middle pinch => LEFT click + DRAG (click on release)
        # -------------------------
        if mid_pinch and not self._mid_pinched:
            self._mid_pinched = True
            self._mid_start_ms = now_ms
            self._mid_start_cursor = (cx, cy)
            self._mid_moved = False
            self._dragging = False

        if self._mid_pinched and mid_pinch:
            held = now_ms - (self._mid_start_ms or now_ms)
            sx, sy = self._mid_start_cursor or (cx, cy)

            if math.hypot(cx - sx, cy - sy) > self.click_max_move_px:
                self._mid_moved = True

            if (not self._dragging) and held >= self.pinch_drag_ms:
                self._dragging = True
                out["drag_start"] = True

        if self._mid_pinched and not mid_pinch:
            held = now_ms - (self._mid_start_ms or now_ms)

            if self._dragging:
                out["drag_end"] = True
            else:
                if held >= self.pinch_click_ms and (not self._mid_moved):
                    if (now_ms - self._last_click_ms) >= self.click_debounce_ms:
                        out["left_click"] = True
                        self._last_click_ms = now_ms

            self._mid_pinched = False
            self._mid_start_ms = None
            self._mid_start_cursor = None
            self._mid_moved = False
            self._dragging = False

        # -------------------------
        # Ring pinch => RIGHT click (click on release)
        # -------------------------
        if ring_pinch and not self._ring_pinched:
            self._ring_pinched = True
            self._ring_start_ms = now_ms
            self._ring_start_cursor = (cx, cy)
            self._ring_moved = False

        if self._ring_pinched and ring_pinch:
            sx, sy = self._ring_start_cursor or (cx, cy)
            if math.hypot(cx - sx, cy - sy) > self.click_max_move_px:
                self._ring_moved = True

        if self._ring_pinched and not ring_pinch:
            held = now_ms - (self._ring_start_ms or now_ms)

            if held >= self.pinch_click_ms and (not self._ring_moved):
                if (now_ms - self._last_click_ms) >= self.click_debounce_ms:
                    out["right_click"] = True
                    self._last_click_ms = now_ms

            self._ring_pinched = False
            self._ring_start_ms = None
            self._ring_start_cursor = None
            self._ring_moved = False

        return out
