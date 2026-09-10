import tkinter as tk
from tkinter import ttk

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="Home Page", font=("Arial", 18), bg="#ecf0f1").pack(pady=20)

        patients_button = ttk.Button(
            self,
            text="Go to Patients Page",
            style="BTN.TButton",
            cursor="hand2",
            command=lambda: controller.render_page("PATIENTS"))
        patients_button.pack(pady=4)

        students_button = ttk.Button(
            self,
            text="Go to Students Page",
            style="BTN.TButton",
            cursor="hand2",
            command=lambda: controller.render_page("STUDENTS"))
        students_button.pack(pady=4)

        scanner_button = ttk.Button(
            self,
            text="Open QR Code Scanner",
            style="BTN.TButton",
            cursor="hand2",
            command=lambda: controller.render_page("QR"))
        scanner_button.pack(pady=4)
        staff_button = ttk.Button(
            self,
            text="Staff",
            style="BTN.TButton",
            cursor="hand2",
            command=lambda: controller.render_page("STAFF"))
        staff_button.pack(pady=4)