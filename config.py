# config.py
import json
import os
import sys


# -----------------------
# Runtime paths
# -----------------------
def is_frozen() -> bool:
    return getattr(sys, "frozen", False)

def app_dir() -> str:
    # exe folder when packaged; project folder when running python
    return os.path.dirname(sys.executable) if is_frozen() else os.path.dirname(os.path.abspath(__file__))

BASE_DIR = app_dir()
CONFIG_JSON_PATH = os.path.join(BASE_DIR, "config.json")

# Model shipped as dist\HandMouse\models\hand_landmarker.task
MODEL_PATH = os.path.join(BASE_DIR, "models", "hand_landmarker.task")


# -----------------------
# Defaults (YOUR PARAMETERS)
# -----------------------
DEFAULTS = {
    "camera": {
        "index": 0,
        "width": 1920,
        "height": 1080,
        "mirror": True,
        "process_every_n_frames": 3,
    },
    "mapping": {
        "active_region_margin": 0.0,
        "map_gamma": 1.10,
        "mouse_speed": 3.0,
    },
    "smoothing": {
        "ema_alpha": 0.14,
        "deadzone_px": 3,
        "max_step_px": 70,
    },
    "mediapipe": {
        "max_hands": 1,
        "min_detection_conf": 0.6,
        "min_tracking_conf": 0.6,
    },
    "gestures": {
        "pinch_start_ratio": 0.30,
        "pinch_end_ratio": 0.40,
        "pinch_click_ms": 120,
        "pinch_drag_ms": 480,
        "click_debounce_ms": 250,
        "click_max_move_px": 35,
    },
    "scroll": {
        "pinch_start_ratio": 0.32,
        "pinch_end_ratio": 0.42,
        "px_per_step": 22,
        "max_step": 6,
    },
    "debug": {
        "show_debug": False,
    },
}


# -----------------------
# Load/merge JSON overrides
# -----------------------
def deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def load_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except FileNotFoundError:
        return {}
    except Exception:
        # corrupted JSON -> ignore instead of crashing
        return {}

def write_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

existing = load_json(CONFIG_JSON_PATH)
if not existing:
    # Create a default config.json next to exe/script so users can edit it
    write_json(CONFIG_JSON_PATH, DEFAULTS)
    settings = dict(DEFAULTS)
else:
    settings = deep_merge(DEFAULTS, existing)


# -----------------------
# Export constants for app imports
# -----------------------

# Camera
CAMERA_INDEX = int(settings["camera"]["index"])
CAMERA_WIDTH = int(settings["camera"]["width"])
CAMERA_HEIGHT = int(settings["camera"]["height"])
MIRROR_CAMERA = bool(settings["camera"]["mirror"])
PROCESS_EVERY_N_FRAMES = max(1, int(settings["camera"]["process_every_n_frames"]))

# Cursor mapping
ACTIVE_REGION_MARGIN = float(settings["mapping"]["active_region_margin"])
MAP_GAMMA = float(settings["mapping"]["map_gamma"])
MOUSE_SPEED = float(settings["mapping"]["mouse_speed"])

# Smoothing
EMA_ALPHA = float(settings["smoothing"]["ema_alpha"])
DEADZONE_PX = int(settings["smoothing"]["deadzone_px"])
MAX_STEP_PX = int(settings["smoothing"]["max_step_px"])

# MediaPipe
MAX_HANDS = int(settings["mediapipe"]["max_hands"])
MIN_DETECTION_CONF = float(settings["mediapipe"]["min_detection_conf"])
MIN_TRACKING_CONF = float(settings["mediapipe"]["min_tracking_conf"])

# Gestures
PINCH_START_RATIO = float(settings["gestures"]["pinch_start_ratio"])
PINCH_END_RATIO = float(settings["gestures"]["pinch_end_ratio"])
PINCH_CLICK_MS = int(settings["gestures"]["pinch_click_ms"])
PINCH_DRAG_MS = int(settings["gestures"]["pinch_drag_ms"])
CLICK_DEBOUNCE_MS = int(settings["gestures"]["click_debounce_ms"])
CLICK_MAX_MOVE_PX = int(settings["gestures"]["click_max_move_px"])

# Scroll (thumb+pinky mode)
SCROLL_PINCH_START_RATIO = float(settings["scroll"]["pinch_start_ratio"])
SCROLL_PINCH_END_RATIO = float(settings["scroll"]["pinch_end_ratio"])
SCROLL_PX_PER_STEP = int(settings["scroll"]["px_per_step"])
SCROLL_MAX_STEP = int(settings["scroll"]["max_step"])

# Debug
SHOW_DEBUG = bool(settings["debug"]["show_debug"])
