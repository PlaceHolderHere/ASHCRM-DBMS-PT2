# Pages Imports
from pages.home_page import HomePage
from pages.patients_page import PatientsPage
from pages.login_page import LogInPage
from pages.students_page import StudentsPage
from qr_scanner import QrScanner
from pages.staff_page import StaffPage
from pages.service_forms_page import ServiceFormPage

# Imports
from tkinter import ttk

# List of all global variables and constants that can be accessed by all python files
PRIMARY_COLOR = "#aecfe4"
ACCENT_COLOR = "#46748e"
ACCENT_DARK = "#335e76"
BACKGROUND_COLOR = "#ffffff"
HEADER_COLOR = "#627e8f"
window_width: int = 1280
window_height: int = 720
viewWidth: float = window_width / 100
viewHeight: float = window_height / 100
pages = {
    "HOME": HomePage,
    "PATIENTS": PatientsPage,
    "LOGIN": LogInPage,
    "QR": QrScanner,
    "STUDENTS": StudentsPage,
    "STAFF": StaffPage,
    "SERVICE_FORMS": ServiceFormPage
}

def init_ttk_styles():
    # Entries
    entry_style = ttk.Style()
    entry_style.theme_use("clam") # For custom border and background doverrides
    entry_style.configure(
        "ENTRY.TEntry",
        font=("Helvetica", 11),
        bordercolor=PRIMARY_COLOR,
        relief="solid",
        padding=4,
    )

    entry_style.map(
        "Custom.TEntry",
        bordercolor=[
            ("focus", ACCENT_COLOR)
        ]
    )

    button_style = ttk.Style()
    button_style.configure(
        "BTN.TButton",
        foreground=ACCENT_COLOR,
        background=BACKGROUND_COLOR,
        focusthickness=2,
        font=("Helvetica", 11, "bold"),
        padding=(8, 4),
        bordercolor=ACCENT_COLOR,  # Primary border color
        lightcolor=ACCENT_COLOR,  # Prevents 3D top/left highlights
        darkcolor=ACCENT_COLOR,  # Prevents 3D bottom/right shadows
        borderwidth=2,  # Border thickness
        relief="solid",
    )
    button_style.map(
        "BTN.TButton",
        background=[
            ("active", ACCENT_DARK),  # Color when clicked
            ("hover", ACCENT_DARK)  # Color on mouse hover
        ],
        foreground=[
            ("active", BACKGROUND_COLOR),  # Color when clicked
            ("hover", BACKGROUND_COLOR)  # Color on mouse hover
        ],
    )

    button_solid_style = ttk.Style()
    button_solid_style.configure(
        "BTN_SOLID.TButton",
        foreground=BACKGROUND_COLOR,
        background=ACCENT_COLOR,
        focusthickness=2,
        font=("Helvetica", 11, "bold"),
        padding=(8, 4),
        borderwidth=1,
        relief="flat",
    )
    button_solid_style.map(
        "BTN_SOLID.TButton",
        background=[
            ("active", ACCENT_DARK),  # Color when clicked
            ("hover", ACCENT_DARK)  # Color on mouse hover
        ]
    )