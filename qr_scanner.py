import cv2
from pyzbar.pyzbar import decode
import threading

class QRScanner:
    def __init__(self, controller):
        self.cap = None
        self.is_running = True
        self.camera_ready = False
        self.controller = controller

        threading.Thread(target=self._init_camera, daemon=True).start()

    def _init_camera(self):
        cap = cv2.VideoCapture(0)
        if self.is_running:
            self.controller.after(0, self._camera_ready, cap)
        else:
            cap.release()

    def _camera_ready(self, cap):
        self.cap = cap
        if self.cap.isOpened():
            self.camera_ready = True

    def get_frame_and_qr(self):
        if not self.is_running or not self.cap or not self.cap.isOpened() or not self.camera_ready:
            return False, None, None

        ret, frame = self.cap.read()
        if not ret:
            return False, None, None

        qr_data = None
        # Decode any barcodes/QR codes present in the frame
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')

            # Draw bounding box around detected QR code
            pts = obj.polygon
            if len(pts) == 4:
                pts = [(pt.x, pt.y) for pt in pts]
                for i in range(4):
                    cv2.line(frame, pts[i], pts[(i + 1) % 4], (0, 255, 0), 2)
            break

        return True, frame, qr_data

    def stop_camera(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None