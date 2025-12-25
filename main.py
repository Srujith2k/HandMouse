# main.py
import ctypes
import time
import cv2

from config import (
    MODEL_PATH,
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, MIRROR_CAMERA,
    PROCESS_EVERY_N_FRAMES,
    ACTIVE_REGION_MARGIN, MAP_GAMMA,
    EMA_ALPHA, DEADZONE_PX, MAX_STEP_PX,
    MAX_HANDS, MIN_DETECTION_CONF, MIN_TRACKING_CONF, SHOW_DEBUG,
    MOUSE_SPEED,
    PINCH_START_RATIO, PINCH_END_RATIO, PINCH_CLICK_MS, PINCH_DRAG_MS,
    CLICK_DEBOUNCE_MS, CLICK_MAX_MOVE_PX,
)

from camera.webcam import Webcam
from vision.hand_tracker import HandTracker
from core.mapping import compute_active_region, map_cam_to_screen
from core.smoothing import CursorSmoother
from core.sensitivity import apply_mouse_speed
from core.pose import is_index_pointing
from actions.mouse_controller import MouseController
from gestures.recognizer import GestureRecognizer


def get_screen_size_windows():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def draw_landmarks_simple(frame, pts):
    for (x, y) in pts:
        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
    if len(pts) > 8:
        cv2.circle(frame, pts[8], 8, (0, 255, 0), -1)


def main():
    screen_w, screen_h = get_screen_size_windows()

    cam = Webcam(CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT)
    tracker = HandTracker(MAX_HANDS, MIN_DETECTION_CONF, MIN_TRACKING_CONF, MODEL_PATH)
    smoother = CursorSmoother(EMA_ALPHA, DEADZONE_PX, MAX_STEP_PX)
    mouse = MouseController()

    gestures = GestureRecognizer(
        pinch_start_ratio=PINCH_START_RATIO,
        pinch_end_ratio=PINCH_END_RATIO,
        pinch_click_ms=PINCH_CLICK_MS,
        pinch_drag_ms=PINCH_DRAG_MS,
        click_debounce_ms=CLICK_DEBOUNCE_MS,
        click_max_move_px=CLICK_MAX_MOVE_PX,
    )

    active_region = None
    start_time = time.monotonic()

    # Frame skipping / reuse last detection
    frame_count = 0
    last_hand = None

    # Cursor value used for gesture gating even when not moving
    last_cursor = (screen_w // 2, screen_h // 2)

    try:
        while True:
            frame = cam.read()
            if frame is None:
                continue

            if MIRROR_CAMERA:
                frame = cv2.flip(frame, 1)

            h, w = frame.shape[:2]
            if active_region is None:
                active_region = compute_active_region(w, h, ACTIVE_REGION_MARGIN)

            timestamp_ms = int((time.monotonic() - start_time) * 1000)
            frame_count += 1

            # Run detection every N frames
            if frame_count % PROCESS_EVERY_N_FRAMES == 0:
                data = tracker.process(frame, timestamp_ms)
                hands = data["hands"]
                last_hand = hands[0] if hands else None

            if last_hand is not None:
                hand0 = last_hand
                lms = hand0["landmarks"]

                # Move cursor only if user is "pointing" with index finger
                if is_index_pointing(lms):
                    x_px, y_px = hand0["index_tip"]

                    sx, sy = map_cam_to_screen(
                        x_px, y_px, active_region, screen_w, screen_h, gamma=MAP_GAMMA
                    )
                    sx, sy = smoother.update(sx, sy)
                    sx, sy = apply_mouse_speed(sx, sy, screen_w, screen_h, MOUSE_SPEED)

                    mouse.move_to(sx, sy)
                    last_cursor = (sx, sy)

                # Gestures still processed even if cursor isn't moving
                events = gestures.update(hand0, timestamp_ms, cursor_xy=last_cursor)

                if events.get("scroll", 0):
                    mouse.scroll(events["scroll"])

                if events["left_click"]:
                    mouse.left_click()

                if events["right_click"]:
                    mouse.right_click()

                if events["drag_start"]:
                    mouse.press_left()

                if events["drag_end"]:
                    mouse.release_left()

                if SHOW_DEBUG:
                    draw_landmarks_simple(frame, lms)

            if SHOW_DEBUG:
                ar = active_region
                cv2.rectangle(frame, (ar.x0, ar.y0), (ar.x1, ar.y1), (255, 255, 255), 2)
                cv2.putText(frame, "ESC to quit", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, f"N={PROCESS_EVERY_N_FRAMES} margin={ACTIVE_REGION_MARGIN:.2f} gamma={MAP_GAMMA:.2f} speed={MOUSE_SPEED:.2f}",
                            (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.imshow("HandMouse Debug", frame)

                if (cv2.waitKey(1) & 0xFF) == 27:
                    break

    finally:
        tracker.close()
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
