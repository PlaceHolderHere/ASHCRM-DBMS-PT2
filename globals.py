# Pages Imports
from pages.home_page import HomePage
from pages.patients_page import PatientsPage
from pages.login_page import LogInPage
from pages.students_page import StudentsPage
from qr_scanner import QrScanner

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
    "STUDENTS": StudentsPage
}