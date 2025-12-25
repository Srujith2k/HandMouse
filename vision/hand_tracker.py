# vision/hand_tracker.py
import os
import cv2
import mediapipe as mp


class HandTracker:
    """
    MediaPipe Tasks API hand tracker (works with mediapipe 0.10.30+).
    Returns pixel landmarks for each detected hand.
    """

    def __init__(self, max_hands: int, min_det_conf: float, min_track_conf: float, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found:\n  {model_path}\n\n"
                f"Download 'hand_landmarker.task' into:\n  handmouse/models/\n"
                f"and ensure MODEL_PATH in config.py points to it."
            )

        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode

        self._landmarker = HandLandmarker.create_from_options(
            HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=model_path),
                running_mode=RunningMode.VIDEO,
                num_hands=max_hands,
                min_hand_detection_confidence=min_det_conf,
                min_hand_presence_confidence=min_det_conf,
                min_tracking_confidence=min_track_conf,
            )
        )

    def close(self):
        try:
            self._landmarker.close()
        except Exception:
            pass

    def process(self, frame_bgr, timestamp_ms: int):
        """
        frame_bgr: OpenCV frame (BGR)
        timestamp_ms: monotonically increasing timestamp (ms)
        returns: dict with hands list
        """
        h, w = frame_bgr.shape[:2]
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        hands_out = []
        if result and result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                pts = []
                for lm in hand_landmarks:
                    x_px = int(lm.x * w)
                    y_px = int(lm.y * h)
                    pts.append((x_px, y_px))

                hands_out.append(
                    {
                        "landmarks": pts,
                        "thumb_tip": pts[4],
                        "index_tip": pts[8],
                    }
                )

        return {"hands": hands_out}
