# camera/webcam.py
import cv2

class Webcam:
    def __init__(self, index: int, width: int, height: int):
        self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam. Try changing CAMERA_INDEX.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Reduce latency due to buffered frames (best effort; depends on backend/driver)
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

    def read(self):
        # Flush a few buffered frames to reduce latency
        for _ in range(3):
            self.cap.grab()
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame

    def release(self):
        self.cap.release()
