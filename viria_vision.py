import cv2
import numpy as np
import time
from datetime import datetime

class ViriaVision:
    def __init__(self, camera_index=0):
        self.cam = cv2.VideoCapture(camera_index)
        self.previous_frame = None
        self.trigger_log = []

    def detect_motion(self, threshold=25):
        ret, frame = self.cam.read()
        if not ret:
            return False, None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.previous_frame is None:
            self.previous_frame = gray
            return False, frame

        frame_diff = cv2.absdiff(self.previous_frame, gray)
        thresh = cv2.threshold(frame_diff, threshold, 255, cv2.THRESH_BINARY)[1]
        motion_detected = np.sum(thresh) > 50000

        self.previous_frame = gray
        return motion_detected, frame

    def scan_loop(self):
        print("[👁️] VIRIA Vision activated. Scanning for motion...")
        while True:
            try:
                motion, frame = self.detect_motion()
                if motion:
                    timestamp = datetime.now().isoformat()
                    print(f"[📸] Motion Detected at {timestamp}")
                    self.trigger_log.append({
                        "time": timestamp,
                        "trigger": "motion",
                        "event": "ritual_presence_detected"
                    })
                    # Optional: trigger ritual or reaction here
                time.sleep(1)
            except KeyboardInterrupt:
                break

    def release(self):
        self.cam.release()
        print("[🛑] Vision system shutdown.")

# --- Example usage ---
if __name__ == "__main__":
    vision = ViriaVision()
    try:
        vision.scan_loop()
    finally:
        vision.release()
