# Pages Imports
from pages.home_page import HomePage
from pages.patients_page import PatientsPage
from pages.login_page import LogInPage
from pages.students_page import StudentsPage
from qr_scanner import QrScanner
from pages.staff_page import StaffPage

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
    "STAFF": StaffPage
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