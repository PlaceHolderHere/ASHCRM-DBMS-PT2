import threading
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode

class QrScanner(tk.Frame):
    def __init__(self, parent, controller):
        # Initialization
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.cap = None

        # Variables
        self.is_running = True

        # Components
        title = ttk.Label(self, text="Please Scan the QR Code")
        title.pack(pady=(16, 0))

        self.webcam_video_frame = ttk.Label(self)
        self.webcam_video_frame.pack(pady=8)

        # Frame for decoded output
        self.info_frame = ttk.Frame(self)
        self.info_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(self.info_frame, text="Scanned Result:").pack(anchor="w")
        self.result_var = tk.StringVar(value="No QR code detected")
        self.result_label = ttk.Label(self.info_frame, textvariable=self.result_var)
        self.result_label.pack(anchor="w", pady=2)

        # Connect to Camera in the background (prevents program from freezing)
        threading.Thread(target=self._init_camera, daemon=True).start()

    def _init_camera(self):
        cap = cv2.VideoCapture(0)
        if self.is_running:
            self.after(0, self._camera_ready, cap)
        else:
            cap.release()

    def _camera_ready(self, cap):
        self.cap = cap
        if self.cap.isOpened():
            self.update_webcam()

    def update_webcam(self):
        if not self.is_running or not self.cap or not self.cap.isOpened():
            return

        frame_recorded, frame = self.cap.read()
        if frame_recorded:
            qr_data = self.read_qr(frame)
            if qr_data:
                self.result_var.set(qr_data)

            # Convert OpenCV BGR frame to RGB for Tkinter display
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv2_image)

            # Resize frame to fit GUI dimensions
            pil_image = pil_image.resize((640, 400), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=pil_image)

            # Keep a reference and update label image
            self.webcam_video_frame.imgtk = imgtk
            self.webcam_video_frame.configure(image=imgtk)

        # Update the frame every 30ms~
        self.controller.root.after(30, self.update_webcam)

    @staticmethod
    def read_qr(frame) -> str:
        qr_data = ""
        qr_codes = decode(frame)
        for qr_code in qr_codes:
            qr_data = qr_code.data.decode("utf-8")

            # Drawing a bounding box around the QR code
            pts = qr_code.polygon
            if len(pts) == 4:
                pts = [(pt.x, pt.y) for pt in pts]
                for i in range(4):
                    cv2.line(frame, pts[i], pts[(i + 1) % 4], (0, 255, 0), 3)

        return qr_data

    def on_close(self):
        if self.cap.isOpened():
            self.cap.release()