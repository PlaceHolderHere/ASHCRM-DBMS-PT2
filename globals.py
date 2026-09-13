# Pages Imports
from pages.home_page import HomePage
from pages.login_page import LogInPage
from pages.students_page import StudentsPage
from qr_scanner import QrScanner
from pages.staff_page import StaffPage
from pages.service_forms_page import ServiceFormPage

# Imports
from tkinter import ttk

# List of all global variables and constants that can be accessed by all python files
PRIMARY_COLOR = "#aecfe4"
PRIMARY_LIGHT = "#d0e3ef"
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
    "LOGIN": LogInPage,
    "QR": QrScanner,
    "STUDENTS": StudentsPage,
    "STAFF": StaffPage,
    "SERVICE_FORMS": ServiceFormPage
}

def init_ttk_styles():
    styles = ttk.Style()
    styles.theme_use("clam")  # For custom border and background doverrides

    # SCROLL BARS
    styles.configure(
        "SCROLL.TScrollbar",
        troughcolor=BACKGROUND_COLOR,
        background=ACCENT_COLOR,
        bordercolor=BACKGROUND_COLOR,
        arrowcolor=BACKGROUND_COLOR,
        relief="flat",
        borderwidth=0,
        arrowsize=0,
    )

    styles.layout(
        "SCROLL.TScrollbar",
        [
            (
                "Scrollbar.trough",
                {
                    "sticky": "ns",
                    "children": [
                        ("Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                    ],
                },
            )
        ],
    )

    styles.map(
        "SCROLL.TScrollbar",
        background=[("active", ACCENT_DARK), ("pressed", PRIMARY_COLOR)],
    )

    # TABLES
    styles.configure(
        "Treeview",
        background=BACKGROUND_COLOR,
        foreground=ACCENT_COLOR,
        borderwidth=2,
        bordercolor=ACCENT_COLOR,
        rowheight=30,
        font=("Helvetica", 11)
    )
    styles.configure(
        "Treeview.Heading",
        background=ACCENT_COLOR,
        foreground=BACKGROUND_COLOR,
        borderwidth=2,
        bordercolor=ACCENT_COLOR,
        rowheight=30,
        font=("Helvetica", 11)
    )
    styles.map(
        "Treeview.Heading",
        background=[
            ("hover", ACCENT_DARK),
            ("active", ACCENT_DARK)
        ]
    )

    # ENTRIES
    styles.configure(
        "ENTRY.TEntry",
        font=("Helvetica", 11),
        bordercolor=PRIMARY_COLOR,
        relief="solid",
        padding=4,
    )

    styles.map(
        "ENTRY.TEntry",
        bordercolor=[
            ("focus", ACCENT_COLOR)
        ]
    )

    # DEFAULT BUTTON
    styles.configure(
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
    styles.map(
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

    # SOLID BUTTON
    styles = ttk.Style()
    styles.configure(
        "BTN_SOLID.TButton",
        foreground=BACKGROUND_COLOR,
        background=ACCENT_COLOR,
        focusthickness=2,
        font=("Helvetica", 11, "bold"),
        padding=(8, 4),
        borderwidth=1,
        relief="flat",
    )
    styles.map(
        "BTN_SOLID.TButton",
        background=[
            ("active", ACCENT_DARK),  # Color when clicked
            ("hover", ACCENT_DARK)  # Color on mouse hover
        ]
    )

    # SIDEBAR BUTTONS
    styles.configure(
        "SIDEBAR_BTN.TButton",
        font=("Helvetica", 15, "bold"),
        foreground=ACCENT_DARK,
        background=PRIMARY_LIGHT,
        anchor="w",
        padding=(15, 10),
        relief="flat"
    )
    styles.map(
        "SIDEBAR_BTN.TButton",
        background=[
            ("active", PRIMARY_COLOR),  # Color when clicked
            ("hover", PRIMARY_COLOR)  # Color on mouse hover
        ]
    )