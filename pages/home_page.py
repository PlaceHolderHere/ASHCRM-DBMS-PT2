import tkinter as tk
from tkinter import ttk
import globals
from PIL import Image, ImageTk

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self._create_widgets()

    def _create_widgets(self):
        self.container = tk.Frame(self, bg=globals.BACKGROUND_COLOR)
        self.container.pack(expand=True, fill="both")

        self.container.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1, uniform="group1")
        self.columnconfigure(1, weight=1, uniform="group1")

        # SIDE BAR FRAME
        self.side_bar = tk.Frame(self.container, bg=globals.PRIMARY_LIGHT)
        self.side_bar.grid(row=0, column=0, sticky="nsew", ipadx=32, ipady=16)
        self.side_bar.grid_columnconfigure(0, weight=1)

        header = tk.Label(
            self.side_bar,
            bg=globals.PRIMARY_LIGHT,
            text="ASHCRM",
            fg=globals.ACCENT_COLOR,
            font=("Helvetica", 14, "bold"),
            compound="left",
        )
        header.grid(row=0, column=0, padx=32, pady=(16, 0))

        subtitle = tk.Label(
            self.side_bar,
            bg=globals.PRIMARY_LIGHT,
            text="SHS Clinic",
            fg=globals.ACCENT_COLOR,
            font=("Helvetica", 11),
            compound="left",
        )
        subtitle.grid(row=1, column=0, padx=32, pady=(2, 16))

        # Buttons and Icons
        self.icon_students = self._load_icon("assets/icons/students.png")
        self.icon_scanner = self._load_icon("assets/icons/Logo.png")
        self.icon_staff = self._load_icon("assets/icons/Staff.png")
        self.icon_service = self._load_icon("assets/icons/Service_Form.png")

        # 2. Define button parameters (text, page_key, parent, icon)
        buttons_config = [
            (
                "Students",
                "STUDENTS",
                self.icon_students,
            ),
            (
                "QR Scanner",
                "QR",
                self.icon_scanner,
            ),
            (
                "Staff",
                "STAFF",
                self.icon_staff
            ),
            (
                "Medical Service Forms",
                "SERVICE_FORMS",
                self.icon_service,
            ),
        ]

        self.sidebar_buttons = {}
        for row_idx, (text, page_key, icon) in enumerate(buttons_config):
            btn = ttk.Button(
                self.side_bar,
                text=f"  {text}",
                image=icon,
                compound="left",
                style="SIDEBAR_BTN.TButton",
                cursor="hand2",
                command=lambda p=page_key: self.controller.render_page(p),
            )

            # Use grid instead of pack
            btn.grid(row=row_idx + 2, column=0, sticky="nsew")
            self.sidebar_buttons[page_key] = btn

        # CONTENT AREA FRAME
        self.content_area = tk.Frame(self.container, bg=globals.BACKGROUND_COLOR)
        self.content_area.grid(row=0, column=1, sticky="nsew")

    @staticmethod
    def _load_icon(filepath, size=(20, 20)):
        img = Image.open(filepath)
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)