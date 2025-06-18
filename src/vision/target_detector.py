import cv2
import imutils
import numpy as np
import logging
import time
from threading import Thread, Event, Lock

class TargetDetector:
    """
    A class to handle real-time target detection using a camera.
    It runs in a separate thread and makes the latest detection result
    available through a thread-safe property.
    """
    def __init__(self, config, stop_event: Event):
        self.camera = cv2.VideoCapture(config.CAMERA_INDEX)
        if not self.camera.isOpened():
            logging.error("Could not open camera.")
            raise IOError("Could not open camera.")

        self.config = config
        self.stop_event = stop_event
        self.display_feed = False
        
        self._lock = Lock()
        self._latest_detection = {'found': False, 'cx': 0, 'cy': 0, 'quadrant': 0}

        self.frame_height, self.frame_width = self.get_frame_dimensions()
        self.center_x = self.frame_width // 2
        self.center_y = self.frame_height // 2
        
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        self.fps = 0

        self.thread = Thread(target=self.run, daemon=True)
        logging.info("TargetDetector initialized.")

    @property
    def latest_detection(self):
        with self._lock:
            return self._latest_detection.copy()

    def get_frame_dimensions(self):
        ret, frame = self.camera.read()
        if not ret:
            logging.error("Could not read frame for dimensions.")
            return 480, 640
        return frame.shape[:2]

    def start(self):
        self.thread.start()
        logging.info("Target detection thread started.")

    def run(self):
        logging.info("Detection loop running...")
        while not self.stop_event.is_set():
            ret, frame = self.camera.read()
            if not ret:
                logging.warning("Failed to grab frame.")
                continue

            self.fps_frame_count += 1
            elapsed_time = time.time() - self.fps_start_time
            if elapsed_time > 1.0:
                self.fps = self.fps_frame_count / elapsed_time
                self.fps_frame_count = 0
                self.fps_start_time = time.time()

            processed_frame = self._process_frame(frame)

            if self.display_feed:
                cv2.imshow("Processed Feed", processed_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop_event.set()

        self.camera.release()
        cv2.destroyAllWindows()
        logging.info("Target detection thread stopped and resources released.")

    def _process_frame(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.config.LOWER_HSV_BOUND, self.config.UPPER_HSV_BOUND)
        
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        
        detection_result = {'found': False, 'cx': 0, 'cy': 0, 'quadrant': 0}

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > self.config.MIN_CONTOUR_AREA:
                M = cv2.moments(largest_contour)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                detection_result['found'] = True
                detection_result['cx'] = cx
                detection_result['cy'] = cy
                
                cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 7, (255, 255, 255), -1)
                cv2.putText(frame, f"Target: ({cx}, {cy})", (cx + 10, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        with self._lock:
            self._latest_detection = detection_result
        
        return frame