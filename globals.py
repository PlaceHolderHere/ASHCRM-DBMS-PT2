# Pages Imports
from pages.home_page import HomePage
from pages.patients_page import PatientsPage
from pages.login_page import LogInPage
from pages.students_page import StudentsPage
from qr_scanner import QrScanner

# List of all global variables that can be accessed by all python files
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